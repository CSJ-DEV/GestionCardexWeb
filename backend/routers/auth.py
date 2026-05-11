"""Routes d'authentification : login, logout, /me, refresh, change-password."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from database import get_db
from models import AppUser
from schemas import LoginIn, UserOut, ChangePasswordIn
from security import (
    create_access_token, create_refresh_token, get_current_user, get_jwt_secret,
    hash_password, set_auth_cookies, verify_password, JWT_ALGORITHM,
)

import jwt

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=UserOut)
def login(payload: LoginIn, response: Response, db: Session = Depends(get_db)):
    email = payload.email.lower()
    u = db.query(AppUser).filter_by(email=email).first()
    if not u or not verify_password(payload.password, u.password_hash):
        raise HTTPException(status_code=401, detail="Identifiants invalides")
    set_auth_cookies(response, create_access_token(u.id, u.email), create_refresh_token(u.id))
    return UserOut(id=u.id, email=u.email, name=u.name or "", role=u.role or "admin")


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
    return UserOut(id=u.id, email=u.email, name=u.name or "", role=u.role or "admin")


@router.get("/me", response_model=UserOut)
def me(user: dict = Depends(get_current_user)):
    return UserOut(id=user["id"], email=user["email"],
                   name=user.get("name") or "", role=user.get("role") or "admin")


@router.put("/change-password")
def change_password(payload: ChangePasswordIn,
                    user: dict = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    """Permet à un utilisateur connecté de changer son propre mot de passe."""
    u = db.query(AppUser).filter_by(id=user["id"]).first()
    if not u:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable")
    if not verify_password(payload.current_password, u.password_hash):
        raise HTTPException(status_code=400, detail="Mot de passe actuel incorrect")
    if payload.current_password == payload.new_password:
        raise HTTPException(status_code=400, detail="Le nouveau mot de passe doit être différent")
    u.password_hash = hash_password(payload.new_password)
    db.commit()
    return {"ok": True, "message": "Mot de passe mis à jour"}
