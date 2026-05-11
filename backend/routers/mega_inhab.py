"""Routes Méga + Inhabilité + Web password (regroupées car liées à un avocat)."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from audit import write_audit, mega_to_dict, inhab_to_dict
from database import get_db
from models import Avocat, InfoMega, InfoDistrict, Inhpra, bool_to_yn
from schemas import InfoMegaIn, InhabIn, WebPasswordIn
from security import get_current_user, hash_password, now_iso, require_role

router = APIRouter(prefix="/avocats", tags=["mega-inhab-web"])


# ---------- Méga ----------
@router.get("/{avocat_id}/mega")
def get_mega(avocat_id: str, user: dict = Depends(get_current_user),
             db: Session = Depends(get_db)):
    m = db.query(InfoMega).filter_by(avocat_id=avocat_id).first()
    if not m:
        return {}
    avo = db.query(Avocat).filter_by(id=avocat_id).first()
    districts = []
    if avo and avo.code:
        districts = [d.nodist for d in db.query(InfoDistrict).filter_by(code=avo.code).all()]
    return mega_to_dict(m, districts)


@router.put("/{avocat_id}/mega")
def upsert_mega(avocat_id: str, payload: InfoMegaIn,
                user: dict = Depends(require_role("admin", "editeur")),
                db: Session = Depends(get_db)):
    avo = db.query(Avocat).filter_by(id=avocat_id).first()
    if not avo:
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    now = now_iso()
    m = db.query(InfoMega).filter_by(avocat_id=avocat_id).first()
    if not m:
        m = InfoMega(id=str(uuid.uuid4()), avocat_id=avocat_id, code=avo.code, created_at=now)
        db.add(m)
    m.sectbar = payload.sectbar or ""
    m.districthab = payload.districthab or ""
    m.francais = bool_to_yn(payload.francais)
    m.anglais = bool_to_yn(payload.anglais)
    m.autres = payload.autres or ""
    m.experience = payload.experience or 0
    m.details = payload.details or ""
    m.art486 = bool_to_yn(payload.art486)
    m.art672 = bool_to_yn(payload.art672)
    m.art684 = bool_to_yn(payload.art684)
    m.commentaire = payload.commentaire or ""
    m.dateinsc = payload.dateinsc or ""
    m.tous_districts = bool(payload.tous_districts)
    m.mega = "O"
    m.updated_at = now
    m.usermodif = user.get("email", "")

    if avo.code:
        db.query(InfoDistrict).filter_by(code=avo.code).delete()
        for nodist in (payload.districts or []):
            db.add(InfoDistrict(code=avo.code, nodist=int(nodist)))

    avo.mega = "O"
    avo.updated_at = now
    db.commit()
    write_audit(db, avocat_id, "mega_update", user.get("email", ""),
                f"Profil Méga mis à jour (sectbar={payload.sectbar or '—'}, exp={payload.experience or 0} an(s), districts={len(payload.districts or [])})")
    return {"ok": True}


@router.delete("/{avocat_id}/mega")
def delete_mega(avocat_id: str, user: dict = Depends(require_role("admin", "editeur")),
                db: Session = Depends(get_db)):
    avo = db.query(Avocat).filter_by(id=avocat_id).first()
    db.query(InfoMega).filter_by(avocat_id=avocat_id).delete()
    if avo and avo.code:
        db.query(InfoDistrict).filter_by(code=avo.code).delete()
    if avo:
        avo.mega = "N"
    db.commit()
    write_audit(db, avocat_id, "mega_delete", user.get("email", ""), "Profil Méga supprimé")
    return {"ok": True}


# ---------- Inhabilité ----------
@router.get("/{avocat_id}/inhabilites")
def list_inhab(avocat_id: str, user: dict = Depends(get_current_user),
               db: Session = Depends(get_db)):
    rows = (db.query(Inhpra).filter_by(avocat_id=avocat_id)
              .order_by(desc(Inhpra.datedeb)).limit(200).all())
    return [inhab_to_dict(i) for i in rows]


@router.post("/{avocat_id}/inhabilites", status_code=201)
def create_inhab(avocat_id: str, payload: InhabIn,
                 user: dict = Depends(require_role("admin", "editeur")),
                 db: Session = Depends(get_db)):
    avo = db.query(Avocat).filter_by(id=avocat_id).first()
    if not avo:
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    now = now_iso()
    i = Inhpra(uuid=str(uuid.uuid4()), avocat_id=avocat_id, code=avo.code,
               datedeb=payload.datedeb, datefin=payload.datefin or "",
               comm=payload.comm or "", created_at=now, updated_at=now)
    db.add(i)
    db.commit()
    db.refresh(i)
    write_audit(db, avocat_id, "inhab_create", user.get("email", ""),
                f"Période d'inhabilité ajoutée : {payload.datedeb} → {payload.datefin or 'en cours'}")
    return inhab_to_dict(i)


@router.put("/{avocat_id}/inhabilites/{inhab_id}")
def update_inhab(avocat_id: str, inhab_id: str, payload: InhabIn,
                 user: dict = Depends(require_role("admin", "editeur")),
                 db: Session = Depends(get_db)):
    i = db.query(Inhpra).filter_by(uuid=inhab_id, avocat_id=avocat_id).first()
    if not i:
        raise HTTPException(status_code=404, detail="Période introuvable")
    i.datedeb = payload.datedeb
    i.datefin = payload.datefin or ""
    i.comm = payload.comm or ""
    i.updated_at = now_iso()
    db.commit()
    write_audit(db, avocat_id, "inhab_update", user.get("email", ""),
                f"Période d'inhabilité modifiée : {payload.datedeb} → {payload.datefin or 'en cours'}")
    return {"ok": True}


@router.delete("/{avocat_id}/inhabilites/{inhab_id}")
def delete_inhab(avocat_id: str, inhab_id: str,
                 user: dict = Depends(require_role("admin", "editeur")),
                 db: Session = Depends(get_db)):
    i = db.query(Inhpra).filter_by(uuid=inhab_id, avocat_id=avocat_id).first()
    if not i:
        raise HTTPException(status_code=404, detail="Période introuvable")
    summary = f"Période supprimée : {i.datedeb or '?'} → {i.datefin or 'en cours'}"
    db.delete(i)
    db.commit()
    write_audit(db, avocat_id, "inhab_delete", user.get("email", ""), summary)
    return {"ok": True}


# ---------- Web password ----------
@router.put("/{avocat_id}/web-password")
def set_web_password(avocat_id: str, payload: WebPasswordIn,
                     user: dict = Depends(require_role("admin", "editeur")),
                     db: Session = Depends(get_db)):
    avo = db.query(Avocat).filter_by(id=avocat_id).first()
    if not avo:
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    avo.web_password_hash = hash_password(payload.password)
    avo.updated_at = now_iso()
    db.commit()
    write_audit(db, avocat_id, "web_password_set", user.get("email", ""), "Mot de passe web défini")
    return {"ok": True}


@router.delete("/{avocat_id}/web-password")
def clear_web_password(avocat_id: str, user: dict = Depends(require_role("admin", "editeur")),
                       db: Session = Depends(get_db)):
    avo = db.query(Avocat).filter_by(id=avocat_id).first()
    if not avo:
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    avo.web_password_hash = None
    avo.updated_at = now_iso()
    db.commit()
    write_audit(db, avocat_id, "web_password_clear", user.get("email", ""), "Mot de passe web réinitialisé")
    return {"ok": True}


# ---------- Audit log (admin only) ----------
audit_router = APIRouter(prefix="/avocats", tags=["audit"])


@audit_router.get("/{avocat_id}/audit")
def list_audit(avocat_id: str, user: dict = Depends(require_role("admin")),
               db: Session = Depends(get_db),
               page: int = 1, page_size: int = 20):
    from models import AuditLog
    page = max(page, 1)
    page_size = min(max(page_size, 1), 200)
    base = db.query(AuditLog).filter_by(avocat_id=avocat_id)
    total = base.count()
    rows = (base.order_by(desc(AuditLog.timestamp))
                .offset((page - 1) * page_size).limit(page_size).all())
    items = [{"id": r.id, "avocat_id": r.avocat_id, "action": r.action,
              "user_email": r.user_email, "summary": r.summary or "",
              "timestamp": r.timestamp} for r in rows]
    return {"items": items, "total": total, "page": page, "page_size": page_size}
