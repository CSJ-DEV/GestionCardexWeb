"""Routes Users CRUD avec cloisonnement Admin / TI."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import AppUser
from schemas import UserCreate, UserUpdate
from security import hash_password, now_utc, require_role

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
def list_users(user: dict = Depends(require_role("admin")), db: Session = Depends(get_db)):
    q = db.query(AppUser)
    # Cloisonnement : un admin (non-TI) ne voit pas les comptes TI.
    if user.get("role") != "ti":
        q = q.filter(AppUser.role != "ti")
    rows = q.limit(500).all()
    return [{"id": u.id, "email": u.email, "name": u.name or "", "role": u.role,
             "created_at": u.created_at} for u in rows]


@router.post("", status_code=201)
def create_user(payload: UserCreate, user: dict = Depends(require_role("admin")),
                db: Session = Depends(get_db)):
    if payload.role == "ti" and user.get("role") != "ti":
        raise HTTPException(status_code=403, detail="Seul un Technicien TI peut créer un compte TI")
    email = payload.email.lower()
    if db.query(AppUser).filter_by(email=email).first():
        raise HTTPException(status_code=409, detail="Courriel déjà utilisé")
    u = AppUser(id=str(uuid.uuid4()), email=email, name=payload.name, role=payload.role,
                password_hash=hash_password(payload.password), created_at=now_utc())
    db.add(u)
    db.commit()
    return {"id": u.id, "email": email, "name": payload.name, "role": payload.role}


@router.put("/{user_id}")
def update_user(user_id: str, payload: UserUpdate, user: dict = Depends(require_role("admin")),
                db: Session = Depends(get_db)):
    u = db.query(AppUser).filter_by(id=user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    if u.role == "ti" and user.get("role") != "ti":
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    if payload.role == "ti" and user.get("role") != "ti":
        raise HTTPException(status_code=403, detail="Seul un Technicien TI peut attribuer le rôle TI")
    if payload.name is not None:
        u.name = payload.name
    if payload.role is not None:
        u.role = payload.role
    if payload.password:
        u.password_hash = hash_password(payload.password)
    db.commit()
    return {"ok": True}


@router.delete("/{user_id}")
def delete_user(user_id: str, user: dict = Depends(require_role("admin")),
                db: Session = Depends(get_db)):
    if user_id == user["id"]:
        raise HTTPException(status_code=400, detail="Impossible de supprimer son propre compte")
    u = db.query(AppUser).filter_by(id=user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    if u.role == "ti" and user.get("role") != "ti":
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    db.delete(u)
    db.commit()
    return {"ok": True}
