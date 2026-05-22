"""Routes Connexions : catalogue des BDD (MongoDB / SQL Server / SQLite).

⚠️ Accès STRICTEMENT réservé au rôle TI (Technicien). Les administrateurs n'y
ont pas accès — les connexions BDD sont une zone technique sensible
(chaînes de connexion + mots de passe chiffrés).
"""
from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import asc
from sqlalchemy.orm import Session

from connexions import (
    ConnexionCreate, ConnexionUpdate, ConnexionOut,
    encrypt_password, decrypt_password, test_connection,
)
from database import get_db
from models import Connexion
from schemas import ConnexionTestPayload
from security import now_utc, require_role

ROOT_DIR = Path(__file__).parent.parent
router = APIRouter(prefix="/connexions", tags=["connexions"])


def _conn_to_out(c: Connexion) -> dict:
    return ConnexionOut(
        id=c.id, name=c.name, type=c.type, server=c.server, port=c.port,
        database=c.database or "", user=c.user or "", description=c.description or "",
        has_password=bool(c.password_enc), is_primary=bool(c.is_primary),
        created_at=c.created_at or "", updated_at=c.updated_at or "",
    ).model_dump()


@router.get("")
def list_connexions(user: dict = Depends(require_role("ti")), db: Session = Depends(get_db)):
    rows = db.query(Connexion).order_by(asc(Connexion.name)).all()
    return [_conn_to_out(c) for c in rows]


@router.get("/{conn_id}")
def get_connexion(conn_id: str, user: dict = Depends(require_role("ti")),
                  db: Session = Depends(get_db)):
    c = db.query(Connexion).filter_by(id=conn_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Connexion introuvable")
    return _conn_to_out(c)


@router.post("", status_code=201)
def create_connexion(payload: ConnexionCreate, user: dict = Depends(require_role("ti")),
                     db: Session = Depends(get_db)):
    now = now_utc()
    pwd = (payload.password or "").strip()
    c = Connexion(
        id=str(uuid.uuid4()), name=payload.name, type=payload.type, server=payload.server,
        port=payload.port, user=payload.user or "", database=payload.database or "",
        description=payload.description or "",
        password_enc=encrypt_password(pwd) if pwd else "",
        is_primary=False, created_at=now, updated_at=now,
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return _conn_to_out(c)


@router.put("/{conn_id}")
def update_connexion(conn_id: str, payload: ConnexionUpdate,
                     user: dict = Depends(require_role("ti")),
                     db: Session = Depends(get_db)):
    c = db.query(Connexion).filter_by(id=conn_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Connexion introuvable")
    update = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if c.is_primary:
        update = {k: v for k, v in update.items() if k == "description"}
        if not update:
            raise HTTPException(status_code=403, detail="La connexion principale est en lecture seule (sauf description)")
    pwd = update.pop("password", None)
    if pwd:
        c.password_enc = encrypt_password(pwd)
    for k, v in update.items():
        setattr(c, k, v)
    c.updated_at = now_utc()
    db.commit()
    db.refresh(c)
    return _conn_to_out(c)


@router.delete("/{conn_id}")
def delete_connexion(conn_id: str, user: dict = Depends(require_role("ti")),
                     db: Session = Depends(get_db)):
    c = db.query(Connexion).filter_by(id=conn_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Connexion introuvable")
    if c.is_primary:
        raise HTTPException(status_code=403, detail="La connexion principale ne peut pas être supprimée")
    db.delete(c)
    db.commit()
    return {"ok": True}


@router.get("/{conn_id}/download")
def download_sqlite_file(conn_id: str, user: dict = Depends(require_role("ti")),
                         db: Session = Depends(get_db)):
    c = db.query(Connexion).filter_by(id=conn_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Connexion introuvable")
    if c.type != "sqlite":
        raise HTTPException(status_code=400, detail="Téléchargement réservé aux connexions SQLite")
    file_rel = c.database or ""
    file_path = ROOT_DIR / file_rel
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail=f"Fichier introuvable : {file_rel}")
    return FileResponse(path=str(file_path), media_type="application/x-sqlite3", filename=file_path.name)


@router.post("/{conn_id}/test")
def test_existing_connexion(conn_id: str, user: dict = Depends(require_role("ti")),
                            db: Session = Depends(get_db)):
    c = db.query(Connexion).filter_by(id=conn_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Connexion introuvable")
    pwd = decrypt_password(c.password_enc or "")
    return test_connection(c_type=c.type, server=c.server, port=c.port,
                           user=c.user or "", password=pwd, database=c.database or "")


@router.post("/test")
def test_arbitrary_connexion(payload: ConnexionTestPayload,
                             user: dict = Depends(require_role("ti"))):
    return test_connection(
        c_type=payload.type, server=payload.server, port=payload.port,
        user=payload.user or "", password=payload.password or "", database=payload.database or "",
    )
