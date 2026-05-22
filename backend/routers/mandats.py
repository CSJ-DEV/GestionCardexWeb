"""Routes Mandats : CRUD utilisé par les rapports Registre97 et Registre98."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from audit import mandat_to_dict
from database import get_db
from models import Avocat, Mandat
from schemas import MandatBase, MandatUpdate
from security import get_current_user, now_utc, require_role

router = APIRouter(prefix="/mandats", tags=["mandats"])


def _parse_date(s: Optional[str]):
    """Parse une date ISO (YYYY-MM-DD) ou ISO 8601 complet en datetime. Retourne None si vide."""
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


@router.get("")
def list_mandats(user: dict = Depends(get_current_user),
                 db: Session = Depends(get_db),
                 avocat_id: Optional[str] = None,
                 article: Optional[str] = None,
                 date_debut: Optional[str] = None,
                 date_fin: Optional[str] = None):
    q = db.query(Mandat)
    if avocat_id: q = q.filter(Mandat.avocat_id == avocat_id)
    if article: q = q.filter(Mandat.article == article)
    if date_debut and date_fin:
        d1 = _parse_date(date_debut)
        d2 = _parse_date(date_fin)
        if d1 and d2:
            q = q.filter(Mandat.date_ordonnance >= d1, Mandat.date_ordonnance <= d2)
    rows = q.order_by(desc(Mandat.date_ordonnance)).limit(2000).all()
    return [mandat_to_dict(m) for m in rows]


@router.post("", status_code=201)
def create_mandat(payload: MandatBase, user: dict = Depends(require_role("admin", "editeur")),
                  db: Session = Depends(get_db)):
    if not db.query(Avocat).filter_by(id=payload.avocat_id).first():
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    now = now_utc()
    m = Mandat(id=str(uuid.uuid4()), avocat_id=payload.avocat_id,
               requerant=payload.requerant, article=payload.article,
               date_ordonnance=_parse_date(payload.date_ordonnance),
               date_emission=_parse_date(payload.date_emission),
               numero=payload.numero, groupe=payload.groupe,
               commentaire=payload.commentaire or "",
               usermodif=user.get("email", ""), created_at=now, updated_at=now)
    db.add(m)
    db.commit()
    db.refresh(m)
    return mandat_to_dict(m)


@router.put("/{mandat_id}")
def update_mandat(mandat_id: str, payload: MandatUpdate,
                  user: dict = Depends(require_role("admin", "editeur")),
                  db: Session = Depends(get_db)):
    m = db.query(Mandat).filter_by(id=mandat_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Mandat introuvable")
    for k, v in payload.model_dump(exclude_unset=True).items():
        if v is None:
            continue
        if k in ("date_ordonnance", "date_emission"):
            setattr(m, k, _parse_date(v))
        else:
            setattr(m, k, v)
    m.updated_at = now_utc()
    db.commit()
    return {"ok": True}


@router.delete("/{mandat_id}")
def delete_mandat(mandat_id: str, user: dict = Depends(require_role("admin")),
                  db: Session = Depends(get_db)):
    m = db.query(Mandat).filter_by(id=mandat_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Mandat introuvable")
    db.delete(m)
    db.commit()
    return {"ok": True}
