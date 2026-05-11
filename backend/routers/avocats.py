"""Routes Avocats : CRUD principal + génération de code séquentiel."""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, desc, asc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from audit import write_audit, avocat_to_dict
from database import get_db
from models import Avocat, Adresse, InfoMega, Inhpra, Mandat, InfoDistrict, bool_to_yn
from schemas import (
    AvocatCreate, AvocatUpdate, AvocatOut, AvocatsListOut, StatsOut,
)
from security import funcValidNoAssSoc, get_current_user, now_iso, require_role

logger = logging.getLogger("gestioncardex")
router = APIRouter(prefix="/avocats", tags=["avocats"])


def _generate_avocat_code(db: Session, type_code: str) -> str:
    type_code = (type_code or "A").upper()
    rows = (db.query(Avocat.code)
              .filter(Avocat.code.like(f"{type_code}%"))
              .order_by(desc(Avocat.code)).limit(50).all())
    next_num = 1
    for (c,) in rows:
        try:
            n = int(c[1:])
            if n >= next_num:
                next_num = n + 1
        except (ValueError, TypeError):
            continue
    return f"{type_code}{next_num:05d}"


@router.get("", response_model=AvocatsListOut)
def list_avocats(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None),
    statut: Optional[str] = Query(None),
    mega: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
):
    query = db.query(Avocat).filter(Avocat.id.isnot(None))
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Avocat.code.ilike(like), Avocat.nom.ilike(like), Avocat.prenom.ilike(like)))
    if statut == "actif":
        query = query.filter(Avocat.actif.is_(True))
    elif statut == "inactif":
        query = query.filter(Avocat.actif.is_(False))
    if mega is not None:
        query = query.filter(Avocat.mega == ("O" if mega else "N"))
    total = query.count()
    rows = (query.order_by(asc(Avocat.nom), asc(Avocat.prenom))
                 .offset((page - 1) * page_size).limit(page_size).all())
    items = [AvocatOut(**avocat_to_dict(a)) for a in rows]
    return AvocatsListOut(items=items, total=total, page=page, page_size=page_size)


@router.get("/next-code")
def next_avocat_code(
    type: str = Query("A", pattern="^[ANP]$"),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return {"code": _generate_avocat_code(db, type)}


@router.get("/stats", response_model=StatsOut)
def avocats_stats(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    base = db.query(Avocat).filter(Avocat.id.isnot(None))
    total = base.count()
    actifs = base.filter(Avocat.actif.is_(True)).count()
    inactifs = base.filter(Avocat.actif.is_(False)).count()
    mega = base.filter(Avocat.mega == "O").count()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    nouveaux = base.filter(Avocat.created_at >= cutoff).count()
    return StatsOut(total=total, actifs=actifs, inactifs=inactifs, mega=mega, nouveaux_30j=nouveaux)


@router.get("/{avocat_id}", response_model=AvocatOut)
def get_avocat(avocat_id: str, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    a = db.query(Avocat).filter_by(id=avocat_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    return AvocatOut(**avocat_to_dict(a))


@router.post("", response_model=AvocatOut, status_code=201)
def create_avocat(payload: AvocatCreate,
                  user: dict = Depends(require_role("admin", "editeur")),
                  db: Session = Depends(get_db)):
    if payload.nas and not funcValidNoAssSoc(payload.nas):
        raise HTTPException(status_code=422, detail="Numéro NAS invalide (algorithme Luhn)")
    type_code = (payload.type_code or "A").upper()
    if type_code not in {"A", "N", "P"}:
        raise HTTPException(status_code=422, detail="type_code invalide (A/N/P)")

    new_id = str(uuid.uuid4())
    now = now_iso()
    adr_json = json.dumps(payload.adresse.model_dump()) if payload.adresse else "{}"

    last_err: Optional[Exception] = None
    for _ in range(5):
        code = _generate_avocat_code(db, type_code)
        a = Avocat(
            code=code, id=new_id, type_code=type_code,
            nom=payload.nom, prenom=payload.prenom,
            sectbar=payload.sectbar or "",
            mega=bool_to_yn(payload.mega), actpass="A" if payload.actif else "P",
            actif=payload.actif, attente=payload.attente,
            annee_barreau=payload.annee_barreau or "",
            dateinscbarr=payload.dateinscbarr or "",
            payable=bool_to_yn(payload.payable),
            codebar=payload.codebar or "", comm=payload.comm or "",
            nas=payload.nas or "", taxes=payload.taxes or "",
            depodirect=bool_to_yn(payload.depodirect),
            factweb=bool_to_yn(payload.factweb),
            confweb=bool_to_yn(payload.confweb),
            villerref=payload.villerref or "", villeref=payload.villerref or "",
            surveil=bool_to_yn(payload.surveil),
            neq=payload.neq or "", codeusager=payload.codeusager or "",
            adresse_courante=adr_json,
            created_at=now, updated_at=now,
            usermodif=user.get("email", ""),
        )
        try:
            db.add(a)
            db.commit()
            db.refresh(a)
            write_audit(db, new_id, "create", user.get("email", ""),
                        f"Création de la fiche {code} — {payload.nom}, {payload.prenom}")
            return AvocatOut(**avocat_to_dict(a))
        except IntegrityError as e:
            db.rollback()
            last_err = e
            continue
    logger.error(f"Avocat code generation failed: {last_err}")
    raise HTTPException(status_code=500, detail="Impossible de générer un code unique. Réessayez.")


@router.put("/{avocat_id}", response_model=AvocatOut)
def update_avocat(avocat_id: str, payload: AvocatUpdate,
                  user: dict = Depends(require_role("admin", "editeur")),
                  db: Session = Depends(get_db)):
    a = db.query(Avocat).filter_by(id=avocat_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Avocat introuvable")

    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="Aucun champ à mettre à jour")

    yn_fields = {"mega", "payable", "depodirect", "factweb", "confweb", "surveil"}
    bool_fields = {"actif", "attente"}

    changed = []
    for k, v in data.items():
        if k == "adresse" and v is not None:
            a.adresse_courante = json.dumps(v if isinstance(v, dict) else v.model_dump())
            changed.append("adresse")
        elif k in yn_fields:
            setattr(a, k, bool_to_yn(v))
            changed.append(k)
        elif k in bool_fields:
            setattr(a, k, bool(v))
            if k == "actif":
                a.actpass = "A" if v else "P"
            changed.append(k)
        elif k == "villerref":
            a.villerref = v or ""
            a.villeref = v or ""
            changed.append(k)
        else:
            setattr(a, k, v)
            changed.append(k)

    a.updated_at = now_iso()
    a.usermodif = user.get("email", "")
    db.commit()
    db.refresh(a)
    if changed:
        write_audit(db, avocat_id, "update", user.get("email", ""),
                    f"Modification : {', '.join(sorted(changed))}")
    return AvocatOut(**avocat_to_dict(a))


@router.delete("/{avocat_id}")
def delete_avocat(avocat_id: str, user: dict = Depends(require_role("admin")),
                  db: Session = Depends(get_db)):
    a = db.query(Avocat).filter_by(id=avocat_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    summary = f"Suppression de {a.code or ''} — {a.nom}, {a.prenom}"
    code = a.code
    db.query(Adresse).filter_by(avocat_id=avocat_id).delete()
    db.query(InfoMega).filter_by(avocat_id=avocat_id).delete()
    db.query(Inhpra).filter_by(avocat_id=avocat_id).delete()
    db.query(Mandat).filter_by(avocat_id=avocat_id).delete()
    if code:
        db.query(InfoDistrict).filter_by(code=code).delete()
    db.delete(a)
    db.commit()
    write_audit(db, avocat_id, "delete", user.get("email", ""), summary)
    return {"ok": True}
