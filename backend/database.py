"""SQLAlchemy engine + session pour les 3 bases SQLite locales (CardAvo, StaticPc, Art52).

L'app travaille principalement sur `CardAvo` (avocats, mandats, audit, users, connexions).
Les BDD `StaticPc` et `Art52` restent disponibles via leur propre engine pour les
prochains modules (référentiels, paiements). Pour l'instant, seul CardAvo est branché.

Ce module est conçu pour être agnostique : on peut basculer sur SQL Server en
remplaçant `DATABASE_URL` par `mssql+pymssql://user:pwd@host/CardAvo` sans
rien changer dans le reste du code.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session

ROOT_DIR = Path(__file__).parent
SQLITE_DIR = ROOT_DIR / "sqlite_dbs"

# URL principale (CardAvo). Surchargeable via .env (DATABASE_URL).
DEFAULT_CARDAVO_URL = f"sqlite:///{SQLITE_DIR / 'CardAvo.db'}"
DATABASE_URL = os.environ.get("DATABASE_URL", DEFAULT_CARDAVO_URL)

# `check_same_thread=False` requis car FastAPI peut traiter plusieurs requêtes
# sur la même session (chaque requête a la sienne, mais le pool peut partager).
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    future=True,
)

# Active les FK SQLite (sinon ON DELETE CASCADE est ignoré).
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


# Engines secondaires (lazy) pour les autres BDD locales
_secondary_engines: dict[str, "Engine"] = {}  # type: ignore[name-defined]


def get_secondary_engine(name: str):
    """Retourne un engine SQLAlchemy pour une BDD secondaire (StaticPc, Art52)."""
    if name in _secondary_engines:
        return _secondary_engines[name]
    db_file = SQLITE_DIR / f"{name}.db"
    if not db_file.exists():
        raise FileNotFoundError(f"BDD introuvable : {db_file}")
    eng = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
    _secondary_engines[name] = eng
    return eng
