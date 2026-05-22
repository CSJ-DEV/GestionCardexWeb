"""Routes Adresses : sous-ressource de Avocats."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, asc
from sqlalchemy.orm import Session

from audit import write_audit, adresse_to_dict
from database import get_db
from models import Avocat, Adresse, bool_to_yn
from schemas import AdresseModel
from security import get_current_user, now_utc, require_role

router = APIRouter(prefix="/avocats", tags=["adresses"])


def _get_avocat(db: Session, avocat_id: str) -> Avocat:
    """Retrouve un avocat par UUID web ou par code legacy."""
    a = db.query(Avocat).filter_by(id=avocat_id).first()
    if a is None:
        a = db.query(Avocat).filter_by(code=avocat_id).first()
    if a is None:
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    return a


@router.get("/{avocat_id}/adresses")
def list_adresses(avocat_id: str, user: dict = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    avo = _get_avocat(db, avocat_id)
    # Jointure legacy : Adresses.code = Avocats.code
    rows = (db.query(Adresse)
              .filter(Adresse.code == avo.code)
              .order_by(desc(Adresse.courant), asc(Adresse.noseq))
              .limit(200).all())
    return [adresse_to_dict(a) for a in rows]


@router.post("/{avocat_id}/adresses", status_code=201)
def create_adresse(avocat_id: str, payload: AdresseModel, courant: bool = False,
                   user: dict = Depends(require_role("admin", "editeur")),
                   db: Session = Depends(get_db)):
    avo = _get_avocat(db, avocat_id)
    now = now_utc()
    new_rowid = str(uuid.uuid4())
    if courant:
        db.query(Adresse).filter(Adresse.code == avo.code).update({"courant": "N"})
    adr = Adresse(
        RowId=new_rowid, code=avo.code,
        address=payload.address or "", adresse2=payload.adresse2 or "",
        adresse3=payload.adresse3 or "", ville=payload.ville or "",
        province=payload.province or "", codepostal=payload.codepostal or "",
        telephone=payload.telephone or "", telephone2=payload.telephone2 or "",
        fax=payload.fax or "", adremail=payload.email or "",
        courant=bool_to_yn(courant),
        dateadr=now, datemodif=now,
        created_at=now, updated_at=now,
        usermodif=user.get("email", ""),
    )
    db.add(adr)
    db.flush()
    if courant and adr.noseq is not None:
        avo.adrcour = adr.noseq
        avo.updated_at = now
    db.commit()
    db.refresh(adr)
    write_audit(db, avo.id or avo.code, "adresse_create", user.get("email", ""),
                f"Adresse ajoutée : {payload.address or '?'}, {payload.ville or ''}".strip(", "))
    return adresse_to_dict(adr)


@router.put("/{avocat_id}/adresses/{adresse_id}")
def update_adresse(avocat_id: str, adresse_id: str, payload: AdresseModel, courant: bool = False,
                   user: dict = Depends(require_role("admin", "editeur")),
                   db: Session = Depends(get_db)):
    avo = _get_avocat(db, avocat_id)
    # Lookup par RowId (UUID legacy) en priorité, puis fallback noseq legacy
    adr = (db.query(Adresse)
             .filter(Adresse.code == avo.code, Adresse.RowId == adresse_id)
             .first())
    if not adr:
        try:
            adr = (db.query(Adresse)
                     .filter(Adresse.code == avo.code, Adresse.noseq == int(adresse_id))
                     .first())
        except (ValueError, TypeError):
            adr = None
    if not adr:
        raise HTTPException(status_code=404, detail="Adresse introuvable")
    now = now_utc()
    for f in ("address", "adresse2", "adresse3", "ville", "province", "codepostal",
              "telephone", "telephone2", "fax"):
        setattr(adr, f, getattr(payload, f) or "")
    # `email` côté front-end → `adremail` legacy
    adr.adremail = payload.email or ""
    adr.courant = bool_to_yn(courant)
    adr.updated_at = now
    adr.datemodif = now
    adr.usermodif = user.get("email", "")
    if courant:
        (db.query(Adresse).filter(Adresse.code == avo.code, Adresse.RowId != adr.RowId)
           .update({"courant": "N"}))
        if adr.noseq is not None:
            avo.adrcour = adr.noseq
            avo.updated_at = now
    db.commit()
    write_audit(db, avo.id or avo.code, "adresse_update", user.get("email", ""),
                f"Adresse modifiée : {payload.address or '?'}, {payload.ville or ''}".strip(", "))
    return {"ok": True}


@router.delete("/{avocat_id}/adresses/{adresse_id}")
def delete_adresse(avocat_id: str, adresse_id: str,
                   user: dict = Depends(require_role("admin", "editeur")),
                   db: Session = Depends(get_db)):
    avo = _get_avocat(db, avocat_id)
    adr = (db.query(Adresse)
             .filter(Adresse.code == avo.code, Adresse.RowId == adresse_id)
             .first())
    if not adr:
        raise HTTPException(status_code=404, detail="Adresse introuvable")
    label = f"{adr.address or '?'}, {adr.ville or ''}"
    if avo.adrcour == adr.noseq:
        avo.adrcour = None
    db.delete(adr)
    db.commit()
    write_audit(db, avo.id or avo.code, "adresse_delete", user.get("email", ""),
                f"Adresse supprimée : {label}".strip(", "))
    return {"ok": True}
