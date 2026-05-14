"""Routes de diagnostic système : santé des 3 BDD.

Accessible UNIQUEMENT au rôle TI (Technicien). Permet de vérifier visuellement
depuis l'interface que l'app est bien connectée à chaque base et de mesurer
les latences.
"""
from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import text

from database import describe_databases, engine, get_secondary_engine
from security import require_role

router = APIRouter(prefix="/system", tags=["system"])


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
    """Retourne l'état des 3 BDD (CardAvo, StaticPc, Art52).

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

    # StaticPc et Art52 via engines secondaires (lazy)
    for name in ("StaticPc", "Art52"):
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
    return out
