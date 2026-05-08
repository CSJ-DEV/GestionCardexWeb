"""
Gestion des connexions externes (MongoDB principal + bases SQL Server).

Sécurité :
- Mots de passe chiffrés par Fernet (clé `CONNEXIONS_FERNET_KEY` du .env).
- Jamais retournés en clair par les endpoints, sauf via le test de connexion.
- Le rôle requis pour modifier ces entrées est `ti` ou `admin`.

Comportement :
- Les modifications n'affectent **pas** la connexion vivante de l'app.
- Bouton de test : valide réellement les credentials avant que l'utilisateur
  ne tente de basculer dessus.
"""
from __future__ import annotations

import os
import socket
from datetime import datetime, timezone
from typing import Literal, Optional
from urllib.parse import urlparse

from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field


# ---------- Chiffrement ----------
def _get_fernet() -> Fernet:
    key = os.environ.get("CONNEXIONS_FERNET_KEY")
    if not key:
        raise HTTPException(status_code=500, detail="CONNEXIONS_FERNET_KEY manquante dans .env")
    return Fernet(key.encode())


def encrypt_password(plain: str) -> str:
    if not plain:
        return ""
    return _get_fernet().encrypt(plain.encode()).decode()


def decrypt_password(token: str) -> str:
    if not token:
        return ""
    try:
        return _get_fernet().decrypt(token.encode()).decode()
    except InvalidToken:
        return ""


# ---------- Modèles ----------
ConnexionType = Literal["mongodb", "sqlserver", "sqlite"]


class ConnexionBase(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str = Field(..., min_length=1, max_length=80)
    type: ConnexionType
    server: str = Field(..., min_length=1, max_length=200)
    port: Optional[int] = None
    database: Optional[str] = ""
    user: Optional[str] = ""
    description: Optional[str] = ""


class ConnexionCreate(ConnexionBase):
    password: Optional[str] = ""


class ConnexionUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: Optional[str] = None
    type: Optional[ConnexionType] = None
    server: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None  # "" = inchangé (sentinel) ; non-vide = nouveau mot de passe
    description: Optional[str] = None


class ConnexionOut(ConnexionBase):
    id: str
    has_password: bool = False
    is_primary: bool = False
    created_at: str
    updated_at: str


def _to_out(doc: dict) -> ConnexionOut:
    return ConnexionOut(
        id=doc["id"],
        name=doc.get("name", ""),
        type=doc.get("type", "mongodb"),
        server=doc.get("server", ""),
        port=doc.get("port"),
        database=doc.get("database", ""),
        user=doc.get("user", ""),
        description=doc.get("description", ""),
        has_password=bool(doc.get("password_enc")),
        is_primary=bool(doc.get("is_primary", False)),
        created_at=doc.get("created_at", ""),
        updated_at=doc.get("updated_at", ""),
    )


# ---------- Tests de connexion ----------
def _test_mongodb(server: str, port: int, user: str, password: str, database: str) -> dict:
    """Test rapide d'une URL MongoDB. Renvoie {ok, message, latency_ms?}."""
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError, OperationFailure, ServerSelectionTimeoutError

    user_part = ""
    if user:
        from urllib.parse import quote_plus
        user_part = f"{quote_plus(user)}:{quote_plus(password or '')}@"
    port_part = f":{port}" if port else ""
    db_part = f"/{database}" if database else ""
    uri = f"mongodb://{user_part}{server}{port_part}{db_part}"

    started = datetime.now(timezone.utc)
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=4000)
        client.admin.command("ping")
        latency = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)
        client.close()
        return {"ok": True, "message": f"MongoDB joignable ({latency} ms)", "latency_ms": latency}
    except (ServerSelectionTimeoutError, OperationFailure) as e:
        return {"ok": False, "message": f"Authentification ou serveur injoignable : {e}"}
    except PyMongoError as e:
        return {"ok": False, "message": f"Erreur MongoDB : {e}"}


def _test_sqlserver(server: str, port: int, user: str, password: str, database: str) -> dict:
    """Test d'une connexion SQL Server (TCP + auth via pymssql)."""
    # Étape 1 : socket TCP — détecte rapidement les serveurs injoignables
    target_port = port or 1433
    try:
        sock = socket.create_connection((server, target_port), timeout=3)
        sock.close()
    except (socket.timeout, OSError) as e:
        return {"ok": False, "message": f"Serveur injoignable {server}:{target_port} ({e})"}

    # Étape 2 : auth via pymssql
    try:
        import pymssql
    except ImportError:
        return {"ok": False, "message": "Module pymssql non installé sur le serveur"}

    started = datetime.now(timezone.utc)
    try:
        conn = pymssql.connect(
            server=server, port=str(target_port), user=user, password=password or "",
            database=database or "", login_timeout=4, timeout=4,
        )
        cur = conn.cursor()
        cur.execute("SELECT @@VERSION")
        row = cur.fetchone()
        cur.close()
        conn.close()
        latency = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)
        version = (row[0] if row else "").split("\n")[0] if row else ""
        return {"ok": True, "message": f"SQL Server OK ({latency} ms) — {version}", "latency_ms": latency}
    except pymssql.OperationalError as e:
        return {"ok": False, "message": f"Authentification refusée : {e}"}
    except Exception as e:  # pylint: disable=broad-except
        return {"ok": False, "message": f"Erreur SQL Server : {e}"}


def _test_sqlite(server: str, database: str) -> dict:
    """Test d'un fichier SQLite local (le 'server' est ignoré, c'est un chemin de fichier)."""
    import sqlite3
    from pathlib import Path

    path = Path(database) if database else Path(server)
    if not path.is_absolute():
        # Chemin relatif → on le résout par rapport au backend
        path = Path(__file__).parent / path
    if not path.exists():
        return {"ok": False, "message": f"Fichier introuvable : {path}"}

    started = datetime.now(timezone.utc)
    try:
        conn = sqlite3.connect(str(path))
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        tables = cur.fetchone()[0]
        cur.close()
        conn.close()
        latency = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)
        size_kb = path.stat().st_size // 1024
        return {"ok": True, "message": f"SQLite OK ({latency} ms) — {tables} tables, {size_kb} KB", "latency_ms": latency}
    except sqlite3.Error as e:
        return {"ok": False, "message": f"Erreur SQLite : {e}"}


def test_connection(c_type: str, server: str, port: Optional[int], user: str,
                    password: str, database: str) -> dict:
    if c_type == "mongodb":
        return _test_mongodb(server, port or 27017, user, password, database)
    if c_type == "sqlserver":
        return _test_sqlserver(server, port or 1433, user, password, database)
    if c_type == "sqlite":
        return _test_sqlite(server, database)
    return {"ok": False, "message": f"Type de connexion inconnu : {c_type}"}


# ---------- Seed primaire (entrée auto pour MONGO_URL courant) ----------
def parse_mongo_url(url: str) -> dict:
    """Parse mongodb://user:pwd@host:port/db en composants."""
    try:
        p = urlparse(url)
        return {
            "server": p.hostname or "",
            "port": p.port or 27017,
            "user": p.username or "",
            "database": (p.path or "").lstrip("/") or "",
        }
    except Exception:  # pylint: disable=broad-except
        return {"server": "", "port": 27017, "user": "", "database": ""}
