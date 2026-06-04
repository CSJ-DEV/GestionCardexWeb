"""Routes de diagnostic système : santé des 3 BDD + version applicative.

Accessible UNIQUEMENT au rôle TI (Technicien). Permet de vérifier visuellement
depuis l'interface que l'app est bien connectée à chaque base et de mesurer
les latences.
"""
from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import text

from database import describe_databases, engine, get_secondary_engine
from security import get_current_user, require_role
import mailer

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/email-status")
def email_status(_=Depends(get_current_user)):
    """Indique si le service courriel ACS est configuré côté serveur.
    Accessible à tout utilisateur connecté (sert au frontend pour activer/masquer
    les fonctions d'envoi)."""
    return {"enabled": mailer.is_email_enabled()}

# Date de dernière modification du backend = horodatage du fichier le plus récent
# parmi server.py, models.py et les routers. Représente la version déployée.
_BACKEND_DIR = Path(__file__).resolve().parent.parent
APP_VERSION = "2.1.0"


def _last_deployment_date() -> str:
    """Retourne la date du fichier .py le plus récemment modifié dans backend/.

    En production Azure App Service, c'est la date du déploiement. En local,
    c'est la date de la dernière édition de code.
    """
    latest = 0.0
    for py in _BACKEND_DIR.rglob("*.py"):
        # Ignore venv, tests et caches Python
        if any(part in {"venv", "__pycache__", "tests", "antenv"} for part in py.parts):
            continue
        try:
            latest = max(latest, py.stat().st_mtime)
        except OSError:
            continue
    if latest == 0.0:
        return ""
    return datetime.fromtimestamp(latest, tz=timezone.utc).isoformat()


def _ping_engine(eng: Any) -> dict:
    """Teste un engine SQLAlchemy avec `SELECT 1` et mesure la latence."""
    t0 = time.perf_counter()
    try:
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
        return {"ok": True, "latency_ms": elapsed_ms, "error": None}
    except Exception as e:
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
        return {"ok": False, "latency_ms": elapsed_ms, "error": str(e)[:200]}


@router.get("/health")
def system_health(user: dict = Depends(require_role("ti"))):
    """Retourne l'état des 5 BDD (CardAvo, StaticPc, Art52, Themis, Fvi).

    Pour chacune : ok (bool), latency_ms (float), dialect (sqlite/mssql),
    url masquée (sans mot de passe), et message d'erreur le cas échéant.
    """
    urls = describe_databases()
    out = {"databases": {}, "mode": "production" if not urls["CardAvo"].startswith("sqlite") else "development"}

    # CardAvo via l'engine principal
    cardavo_ping = _ping_engine(engine)
    out["databases"]["CardAvo"] = {
        **cardavo_ping,
        "url": urls["CardAvo"],
        "dialect": engine.dialect.name,
        "primary": True,
    }

    # StaticPc, Art52, Themis et Fvi via engines secondaires (lazy)
    for name in ("StaticPc", "Art52", "Themis", "Fvi"):
        try:
            eng = get_secondary_engine(name)
            ping = _ping_engine(eng)
            out["databases"][name] = {
                **ping,
                "url": urls[name],
                "dialect": eng.dialect.name,
                "primary": False,
            }
        except Exception as e:
            out["databases"][name] = {
                "ok": False, "latency_ms": 0,
                "error": f"Engine init failed: {e}",
                "url": urls.get(name, "?"),
                "dialect": "?",
                "primary": False,
            }

    out["all_ok"] = all(d["ok"] for d in out["databases"].values())
    out["version"] = APP_VERSION
    out["deployed_at"] = _last_deployment_date()
    out["server_time"] = datetime.now(timezone.utc).isoformat()
    return out


@router.get("/version")
def system_version(user: dict = Depends(require_role("ti"))):
    """Retourne la version applicative et la date du dernier déploiement.

    Endpoint léger (sans ping des BDD) pour affichage dans la sidebar TI.
    """
    return {
        "version": APP_VERSION,
        "deployed_at": _last_deployment_date(),
        "server_time": datetime.now(timezone.utc).isoformat(),
    }
