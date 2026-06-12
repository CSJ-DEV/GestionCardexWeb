"""Helpers d'authentification : hash mot de passe, JWT, dépendances FastAPI."""
from __future__ import annotations

import os
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

import bcrypt
import jwt
from fastapi import Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from database import get_db
from models import AppUser

JWT_ALGORITHM = "HS256"
ADMIN_LIKE = {"admin", "ti"}

# Sentinel marqueur pour les comptes Microsoft Entra ID : on stocke cette
# chaîne fixe dans AppUser.password_hash (au lieu d'un vrai bcrypt aléatoire)
# pour identifier les comptes SSO sans nouvelle colonne en BDD. C'est par
# conception un hash bcrypt invalide → `verify_password` renverra toujours
# False → login email/mdp impossible pour les comptes SSO.
ENTRA_SSO_HASH = "__ENTRA_SSO__"


def is_sso_user(u) -> bool:
    """True si l'utilisateur est authentifié via Microsoft Entra ID."""
    return getattr(u, "password_hash", None) == ENTRA_SSO_HASH


def auth_provider_of(u) -> str:
    """Retourne 'entra' ou 'local' pour un AppUser."""
    return "entra" if is_sso_user(u) else "local"

# Timezone métier (Québec) — pour reproduire le comportement `Now()` du legacy VB.
# Override possible via la variable d'env APP_TIMEZONE (utile pour tests).
APP_TZ = ZoneInfo(os.environ.get("APP_TIMEZONE", "America/Toronto"))


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def get_jwt_secret() -> str:
    return os.environ["JWT_SECRET"]


def now_iso() -> str:
    """ISO 8601 string. Conservée pour compatibilité (logs, payloads JSON)."""
    return datetime.now(timezone.utc).isoformat()


def now_utc() -> datetime:
    """Datetime aware UTC, sans microsecondes — réservé au JWT et aux usages où UTC est nécessaire."""
    return datetime.now(timezone.utc).replace(microsecond=0)


def now_local() -> datetime:
    """Datetime naïf en heure locale Québec (= legacy VB `Now()`).

    Utilisé pour les colonnes `datemodif`, `created_at`, `updated_at`,
    `timestamp` (audit). Naïf car SQL Server stocke en local sans TZ.
    """
    return datetime.now(APP_TZ).replace(tzinfo=None, microsecond=0)


def create_access_token(user_id, email: str) -> str:
    # SQL Server (UNIQUEIDENTIFIER) renvoie un objet uuid.UUID via pyodbc — force str.
    payload = {
        "sub": str(user_id), "email": email, "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=60 * 8),
    }
    return jwt.encode(payload, get_jwt_secret(), algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id) -> str:
    payload = {
        "sub": str(user_id), "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }
    return jwt.encode(payload, get_jwt_secret(), algorithm=JWT_ALGORITHM)


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    secure = os.environ.get("COOKIE_SECURE", "false").lower() == "true"
    # samesite=None requis pour cross-site (frontend et backend sur des sous-domaines différents).
    # `None` exige `secure=True`, donc COOKIE_SECURE doit être true en prod.
    samesite = os.environ.get("COOKIE_SAMESITE", "lax").lower()
    if samesite == "none":
        secure = True  # contrainte navigateur
    response.set_cookie("access_token", access_token, httponly=True, secure=secure, samesite=samesite,
                        max_age=60 * 60 * 8, path="/")
    response.set_cookie("refresh_token", refresh_token, httponly=True, secure=secure, samesite=samesite,
                        max_age=60 * 60 * 24 * 7, path="/")


def get_current_user(request: Request, db: Session = Depends(get_db)) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Non authentifié")
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Type de jeton invalide")
        u = db.query(AppUser).filter_by(id=payload["sub"]).first()
        if not u:
            raise HTTPException(status_code=401, detail="Utilisateur introuvable")
        return {"id": u.id, "email": u.email, "name": u.name, "role": u.role,
                "auth_provider": auth_provider_of(u)}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Jeton expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Jeton invalide")


def require_role(*allowed_roles):
    """Crée une dépendance qui n'autorise que les rôles donnés.

    Règle métier : le rôle TI est un super-utilisateur technique avec accès
    complet à l'application — il est automatiquement autorisé partout où
    admin ou editeur le sont. Le rôle admin est de son côté autorisé partout
    où editeur l'est (hiérarchie de privilèges).
    """
    expanded = set(allowed_roles)
    # Hiérarchie : admin ⊃ editeur (admin couvre éditeur)
    if "editeur" in expanded:
        expanded.add("admin")
    # TI = super-utilisateur : couvre tout
    if expanded & {"admin", "editeur"}:
        expanded.add("ti")
    if "admin" in expanded:
        expanded.add("ti")

    def checker(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role") not in expanded:
            raise HTTPException(status_code=403, detail="Accès refusé")
        return user
    return checker


# Limite défensive pour la colonne `usermodif` legacy (taille variable selon la table).
# Le DBA peut élargir la colonne ; on tronque côté app pour ne jamais déclencher
# l'erreur SQL « String or binary data would be truncated » sur un email long.
USERMODIF_MAX = 50


def trunc_usermodif(email: str | None) -> str:
    """Retourne l'email tronqué à USERMODIF_MAX caractères (safe pour la BD legacy)."""
    return (email or "")[:USERMODIF_MAX]


def funcValidNoAssSoc(no: str) -> bool:
    """Validation Luhn du NAS canadien (port direct du VB legacy)."""
    if not no:
        return True
    no = no.strip()
    if len(no) != 9 or not no.isdigit():
        return False
    tot = 0
    for i, ch in enumerate(no[:-1], start=1):
        c = int(ch)
        if i % 2 == 0:
            c = c * 2
            if c > 9:
                c = (c // 10) + (c % 10)
        tot += c
    v = (10 - (tot % 10)) % 10
    return v == int(no[-1])
