"""Routes Adresses : sous-ressource de Avocats."""
from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from audit import write_audit, adresse_to_dict
from database import get_db
from models import Avocat, Adresse, bool_to_yn
from schemas import AdresseModel
from security import get_current_user, now_iso, require_role

router = APIRouter(prefix="/avocats", tags=["adresses"])


@router.get("/{avocat_id}/adresses")
def list_adresses(avocat_id: str, user: dict = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    rows = (db.query(Adresse).filter_by(avocat_id=avocat_id)
              .order_by(desc(Adresse.created_at)).limit(200).all())
    return [adresse_to_dict(a) for a in rows]


@router.post("/{avocat_id}/adresses", status_code=201)
def create_adresse(avocat_id: str, payload: AdresseModel, courant: bool = False,
                   user: dict = Depends(require_role("admin", "editeur")),
                   db: Session = Depends(get_db)):
    avo = db.query(Avocat).filter_by(id=avocat_id).first()
    if not avo:
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    now = now_iso()
    new_id = str(uuid.uuid4())
    if courant:
        db.query(Adresse).filter_by(avocat_id=avocat_id).update({"courant": "N"})
        avo.adresse_courante = json.dumps(payload.model_dump())
        avo.updated_at = now
    adr = Adresse(
        id=new_id, RowId=new_id, avocat_id=avocat_id, code=avo.code,
        address=payload.address or "", adresse2=payload.adresse2 or "",
        adresse3=payload.adresse3 or "", ville=payload.ville or "",
        province=payload.province or "", codepostal=payload.codepostal or "",
        telephone=payload.telephone or "", telephone2=payload.telephone2 or "",
        fax=payload.fax or "", email=payload.email or "", adremail=payload.email or "",
        courant=bool_to_yn(courant),
        created_at=now, updated_at=now,
    )
    db.add(adr)
    db.commit()
    db.refresh(adr)
    write_audit(db, avocat_id, "adresse_create", user.get("email", ""),
                f"Adresse ajoutée : {payload.address or '?'}, {payload.ville or ''}".strip(", "))
    return adresse_to_dict(adr)


@router.put("/{avocat_id}/adresses/{adresse_id}")
def update_adresse(avocat_id: str, adresse_id: str, payload: AdresseModel, courant: bool = False,
                   user: dict = Depends(require_role("admin", "editeur")),
                   db: Session = Depends(get_db)):
    adr = db.query(Adresse).filter_by(id=adresse_id, avocat_id=avocat_id).first()
    if not adr:
        raise HTTPException(status_code=404, detail="Adresse introuvable")
    now = now_iso()
    for f in ("address", "adresse2", "adresse3", "ville", "province", "codepostal",
              "telephone", "telephone2", "fax", "email"):
        setattr(adr, f, getattr(payload, f) or "")
    adr.adremail = payload.email or ""
    adr.courant = bool_to_yn(courant)
    adr.updated_at = now
    if courant:
        (db.query(Adresse).filter(Adresse.avocat_id == avocat_id, Adresse.id != adresse_id)
           .update({"courant": "N"}))
        avo = db.query(Avocat).filter_by(id=avocat_id).first()
        if avo:
            avo.adresse_courante = json.dumps(payload.model_dump())
            avo.updated_at = now
    db.commit()
    write_audit(db, avocat_id, "adresse_update", user.get("email", ""),
                f"Adresse modifiée : {payload.address or '?'}, {payload.ville or ''}".strip(", "))
    return {"ok": True}


@router.delete("/{avocat_id}/adresses/{adresse_id}")
def delete_adresse(avocat_id: str, adresse_id: str,
                   user: dict = Depends(require_role("admin", "editeur")),
                   db: Session = Depends(get_db)):
    adr = db.query(Adresse).filter_by(id=adresse_id, avocat_id=avocat_id).first()
    if not adr:
        raise HTTPException(status_code=404, detail="Adresse introuvable")
    label = f"{adr.address or '?'}, {adr.ville or ''}"
    db.delete(adr)
    db.commit()
    write_audit(db, avocat_id, "adresse_delete", user.get("email", ""),
                f"Adresse supprimée : {label}".strip(", "))
    return {"ok": True}
