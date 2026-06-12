"""SQLAlchemy engine + session pour les 3 bases (CardAvo principale + StaticPc / Art52).

CONFIGURATION SIMPLIFIÉE — deux modes au choix :

  Mode 1 (recommandé en prod) : 4 champs séparés, comme dans SSMS
  ────────────────────────────────────────────────────────────────
  SQLSERVER_HOST=csj-sql-test
  SQLSERVER_USER=gestioncardex_app
  SQLSERVER_PASSWORD=votreMotDePasse
  SQLSERVER_PORT=1433                  (optionnel, 1433 par défaut)
  DB_CARDAVO=CardAvo                   (nom de la base sur le serveur)
  DB_STATICPC=StaticPc
  DB_ART52=Art52

  Mode 2 (avancé) : URL complète SQLAlchemy
  ─────────────────────────────────────────
  DATABASE_URL=mssql+pymssql://user:pwd@host/db
  DATABASE_URL_STATICPC=mssql+pymssql://...
  DATABASE_URL_ART52=mssql+pymssql://...

  Aucune variable définie ?
  ─────────────────────────
  → Fallback automatique sur les 3 fichiers SQLite locaux (sqlite_dbs/*.db).
    C'est le mode dev sur Emergent.

Le code applicatif reste identique dans les 3 cas.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Generator
from urllib.parse import quote_plus

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session

ROOT_DIR = Path(__file__).parent
SQLITE_DIR = ROOT_DIR / "sqlite_dbs"


# ============================================================
#         Construction des URLs depuis les variables env
# ============================================================
def _build_sqlserver_url(db_name: str) -> str | None:
    """Assemble une URL SQLAlchemy à partir des champs SQL Server.
    Retourne None si les champs requis ne sont pas définis.

    Deux modes d'authentification supportés :
    - SQL Server Authentication : SQLSERVER_USER + SQLSERVER_PASSWORD
    - Windows Authentication    : SQLSERVER_TRUSTED=yes (compte du process)
      → utilise pyodbc + ODBC Driver 17 for SQL Server (livré Windows).
    """
    host = os.environ.get("SQLSERVER_HOST")
    port = os.environ.get("SQLSERVER_PORT", "1433")
    if not (host and db_name):
        return None

    # Mode 1 : Windows Authentication (Trusted Connection) — via pyodbc
    if os.environ.get("SQLSERVER_TRUSTED", "").lower() in ("yes", "true", "1"):
        driver = os.environ.get("SQLSERVER_ODBC_DRIVER", "ODBC Driver 17 for SQL Server")
        return (
            f"mssql+pyodbc://@{host}:{port}/{db_name}"
            f"?driver={quote_plus(driver)}&trusted_connection=yes"
        )

    # Mode 2 : SQL Server Authentication — via pymssql
    user = os.environ.get("SQLSERVER_USER")
    pwd = os.environ.get("SQLSERVER_PASSWORD", "")  # vide accepté
    if not user:
        return None
    return f"mssql+pymssql://{user}:{quote_plus(pwd)}@{host}:{port}/{db_name}"


def _build_fvi_url() -> str | None:
    """Assemble l'URL SQLAlchemy pour la BDD Fvi (sur un serveur SÉPARÉ, CSJ-WEB01).

    Variables d'env attendues :
      FVI_SERVER, FVI_DATABASE, FVI_USER, FVI_PASSWORD, FVI_PORT (optionnel, 1433)
    """
    host = os.environ.get("FVI_SERVER")
    db = os.environ.get("FVI_DATABASE")
    user = os.environ.get("FVI_USER")
    pwd = os.environ.get("FVI_PASSWORD", "")
    port = os.environ.get("FVI_PORT", "1433")
    if not (host and db and user):
        return None
    return f"mssql+pymssql://{user}:{quote_plus(pwd)}@{host}:{port}/{db}"


def _resolve_url(db_logical_name: str, env_url_var: str, env_dbname_var: str) -> str:
    """Détermine l'URL effective d'une base selon l'ordre de priorité :
       1. URL complète si fournie (DATABASE_URL...)
       2. Pour Fvi : pattern FVI_* (serveur dédié CSJ-WEB01)
       3. 4-champs SQL Server si host+user+pwd+nomBase fournis (CardAvo/StaticPc/Art52/Themis)
       4. Fichier SQLite local de fallback (dev)
    """
    # 1. URL complète prioritaire (mode avancé)
    url = os.environ.get(env_url_var)
    if url:
        return url

    # 2. Cas spécial Fvi : serveur dédié via FVI_*
    if db_logical_name == "Fvi":
        url = _build_fvi_url()
        if url:
            return url

    # 3. Mode 4-champs : on regarde si on a un host SQL Server + le nom de la base
    db_name = os.environ.get(env_dbname_var)
    if db_name:
        url = _build_sqlserver_url(db_name)
        if url:
            return url

    # 4. Fallback dev → fichier SQLite
    return f"sqlite:///{SQLITE_DIR / f'{db_logical_name}.db'}"


DATABASE_URL = _resolve_url("CardAvo", "DATABASE_URL", "DB_CARDAVO")


# ============================================================
#               Moteur principal (CardAvo)
# ============================================================
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    future=True,
)

# Active les FK SQLite (sinon ON DELETE CASCADE est ignoré). Sans effet sur SQL Server.
if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _):  # noqa: ANN001
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dépendance FastAPI : ouvre/ferme une session par requête."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================
#         Moteurs secondaires (StaticPc, Art52) — lazy
# ============================================================
_secondary_engines: dict[str, object] = {}

# Mapping nom logique → (variable URL, variable nom de base)
_SECONDARY_CONFIG = {
    "StaticPc": ("DATABASE_URL_STATICPC", "DB_STATICPC"),
    "Art52": ("DATABASE_URL_ART52", "DB_ART52"),
    "Themis": ("DATABASE_URL_THEMIS", "DB_THEMIS"),
    "Fvi": ("DATABASE_URL_FVI", "DB_FVI"),
}


def get_secondary_engine(name: str):
    """Retourne un engine SQLAlchemy pour une BDD secondaire.

    En prod : SQL Server (résolu depuis SQLSERVER_HOST + DB_STATICPC / DB_ART52,
    ou via DATABASE_URL_STATICPC / DATABASE_URL_ART52).
    En dev : fichier SQLite local.
    """
    if name in _secondary_engines:
        return _secondary_engines[name]
    if name not in _SECONDARY_CONFIG:
        raise ValueError(f"BDD secondaire inconnue : {name}")
    env_url_var, env_dbname_var = _SECONDARY_CONFIG[name]
    url = _resolve_url(name, env_url_var, env_dbname_var)
    args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    eng = create_engine(url, connect_args=args, pool_pre_ping=True, future=True)
    _secondary_engines[name] = eng
    return eng


def describe_databases() -> dict[str, str]:
    """Utilitaire de diagnostic : retourne le type de BDD utilisé par chaque base.

    Masque les mots de passe dans les URLs avant retour.
    """
    out = {"CardAvo": _mask(DATABASE_URL)}
    for name, (url_var, db_var) in _SECONDARY_CONFIG.items():
        out[name] = _mask(_resolve_url(name, url_var, db_var))
    return out


def describe_server_context() -> dict:
    """Retourne un résumé court de l'environnement de connexion CardAvo.

    Sert à l'UI pour afficher « connecté à <serveur> » sous le bouton de
    déconnexion. Ne révèle jamais d'identifiant ni de mot de passe.

    Retour :
      - kind : 'sqlite' | 'sqlserver' | 'other'
      - label : chaîne courte affichable (ex. « SQLite local (dev) » ou
                « SRV01 / CardAvo »)
      - host : nom du serveur (sans port) ou 'localhost' pour SQLite
      - database : nom logique de la base
    """
    url = DATABASE_URL or ""
    if url.startswith("sqlite"):
        # ex. sqlite:////app/backend/sqlite_dbs/CardAvo.db
        db_file = url.split("/")[-1] or "CardAvo.db"
        return {
            "kind": "sqlite",
            "label": f"SQLite local · {db_file}",
            "host": "localhost",
            "database": db_file,
        }
    if "://" in url and "@" in url:
        # ex. mssql+pymssql://user:pwd@host:1433/CardAvo
        try:
            _, rest = url.split("://", 1)
            _, host_db = rest.rsplit("@", 1)
            host_part, _, db_part = host_db.partition("/")
            host_only = host_part.split(":")[0]
            db_name = db_part or os.getenv("DB_CARDAVO", "CardAvo")
            return {
                "kind": "sqlserver",
                "label": f"{host_only} · {db_name}",
                "host": host_only,
                "database": db_name,
            }
        except ValueError:
            pass
    return {"kind": "other", "label": "Inconnu", "host": "", "database": ""}


def _mask(url: str) -> str:
    """Masque le mot de passe dans une URL SQLAlchemy (ne pas logger en clair)."""
    if "://" not in url or "@" not in url:
        return url
    scheme, rest = url.split("://", 1)
    creds, host = rest.rsplit("@", 1)
    if ":" in creds:
        user, _ = creds.split(":", 1)
        return f"{scheme}://{user}:***@{host}"
    return url
