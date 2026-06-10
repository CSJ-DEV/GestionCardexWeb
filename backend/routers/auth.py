"""Routes d'authentification : login, logout, /me, refresh, change-password."""
from __future__ import annotations

import os

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from database import get_db
from models import AppUser
from schemas import LoginIn, UserOut, ChangePasswordIn
from security import (
    create_access_token, create_refresh_token, get_current_user, get_jwt_secret,
    hash_password, set_auth_cookies, verify_password, JWT_ALGORITHM,
    is_sso_user, auth_provider_of,
)

import jwt

router = APIRouter(prefix="/auth", tags=["auth"])


def _local_login_disabled() -> bool:
    """True si la variable d'env DISABLE_LOCAL_LOGIN est activée (prod Azure).

    Bloque l'usage du formulaire courriel/mot de passe → seuls les comptes Entra ID
    peuvent se connecter. La variable est volontairement absente en dev (Emergent,
    local) pour permettre le développement avec les comptes admin/ti seed.
    """
    return os.environ.get("DISABLE_LOCAL_LOGIN", "").strip().lower() in ("1", "true", "yes")


@router.post("/login", response_model=UserOut)
def login(payload: LoginIn, response: Response, db: Session = Depends(get_db)):
    # Blocage global du login local en production Azure
    if _local_login_disabled():
        raise HTTPException(
            status_code=403,
            detail="La connexion par mot de passe est désactivée sur cet environnement. "
                   "Veuillez utiliser « Se connecter avec Microsoft ».",
        )

    email = payload.email.lower()
    u = db.query(AppUser).filter_by(email=email).first()
    if not u or is_sso_user(u) or not verify_password(payload.password, u.password_hash):
        # On groupe les deux refus pour ne pas révéler l'existence des comptes SSO.
        # Cas SSO : verify_password renverrait False de toute façon (hash invalide).
        if u is not None and is_sso_user(u):
            raise HTTPException(
                status_code=401,
                detail="Ce compte est géré par Microsoft. Utilisez « Se connecter avec Microsoft ».",
            )
        raise HTTPException(status_code=401, detail="Identifiants invalides")
    set_auth_cookies(response, create_access_token(u.id, u.email), create_refresh_token(u.id))
    return UserOut(id=u.id, email=u.email, name=u.name or "", role=u.role or "admin",
                   auth_provider=auth_provider_of(u))


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return {"ok": True}


@router.post("/refresh", response_model=UserOut)
def refresh_token_endpoint(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Aucun jeton de rafraîchissement")
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Type de jeton invalide")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expirée — veuillez vous reconnecter")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Jeton invalide")
    u = db.query(AppUser).filter_by(id=payload["sub"]).first()
    if not u:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable")
    set_auth_cookies(response, create_access_token(u.id, u.email), create_refresh_token(u.id))
    return UserOut(id=u.id, email=u.email, name=u.name or "", role=u.role or "admin",
                   auth_provider=auth_provider_of(u))


@router.get("/me", response_model=UserOut)
def me(user: dict = Depends(get_current_user)):
    return UserOut(id=user["id"], email=user["email"],
                   name=user.get("name") or "", role=user.get("role") or "admin",
                   auth_provider=user.get("auth_provider") or "local")


@router.put("/change-password")
def change_password(payload: ChangePasswordIn,
                    user: dict = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    """Permet à un utilisateur connecté de changer son propre mot de passe."""
    u = db.query(AppUser).filter_by(id=user["id"]).first()
    if not u:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable")
    if is_sso_user(u):
        raise HTTPException(
            status_code=400,
            detail="Compte géré par Microsoft : le mot de passe se change dans votre compte Microsoft.",
        )
    if not verify_password(payload.current_password, u.password_hash):
        raise HTTPException(status_code=400, detail="Mot de passe actuel incorrect")
    if payload.current_password == payload.new_password:
        raise HTTPException(status_code=400, detail="Le nouveau mot de passe doit être différent")
    u.password_hash = hash_password(payload.new_password)
    db.commit()
    return {"ok": True, "message": "Mot de passe mis à jour"}
