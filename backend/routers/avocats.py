"""Routes Avocats : CRUD principal + génération de code séquentiel."""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, and_, desc, asc, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from audit import write_audit, avocat_to_dict
from database import get_db, get_secondary_engine
from models import Avocat, Adresse, InfoMega, Inhpra, Mandat, InfoDistrict, bool_to_yn
from schemas import (
    AvocatCreate, AvocatUpdate, AvocatOut, AvocatsListOut, StatsOut,
)
from security import funcValidNoAssSoc, get_current_user, now_local, require_role

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


def _create_or_update_main_address(db: Session, a: Avocat, data: dict, user_email: str) -> None:
    """Upsert l'adresse courante (Adresses.code = a.code, courant='O').

    Met `Avocats.adrcour = Adresses.noseq` pour pointer dessus.
    """
    now = now_local()
    adr = (db.query(Adresse)
             .filter(Adresse.code == a.code, Adresse.courant == "O")
             .first())
    if adr is None:
        adr = Adresse(
            RowId=str(uuid.uuid4()),
            code=a.code,
            courant="O",
            dateadr=now,
            created_at=now,
        )
        db.add(adr)
    for field in ("address", "adresse2", "adresse3", "ville", "province",
                  "codepostal", "telephone", "telephone2", "fax"):
        if field in data:
            setattr(adr, field, data.get(field) or "")
    # `email` côté front-end → `adremail` legacy (colonne unique)
    if "email" in data:
        adr.adremail = data.get("email") or ""
    adr.updated_at = now
    adr.datemodif = now
    adr.usermodif = user_email
    db.flush()
    if adr.noseq is not None:
        a.adrcour = adr.noseq
    db.commit()


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
    query = db.query(Avocat).filter(Avocat.code.isnot(None))
    if q:
        # Recherche tolérante à l'ordre : on découpe en tokens (espaces / virgules).
        # Chaque token doit matcher au moins l'un de (code, nom, prénom) en LIKE.
        # → "Tremblay Alain", "Alain Tremblay", "Tremb Ala" donnent tous le même résultat.
        # → "Tremblay" seul ou "P00963" seul fonctionne aussi (rétro-compat).
        tokens = [t for t in q.replace(",", " ").split() if t.strip()]
        if not tokens:
            tokens = [q]  # garde-fou : si q n'a que des espaces/virgules
        for tok in tokens:
            like = f"%{tok}%"
            query = query.filter(or_(
                Avocat.code.ilike(like),
                Avocat.nom.ilike(like),
                Avocat.prenom.ilike(like),
            ))
    if statut == "actif":
        query = query.filter(Avocat.actpass == "A")
    elif statut == "inactif":
        query = query.filter(Avocat.actpass == "P")
    if mega is not None:
        query = query.filter(Avocat.mega == ("O" if mega else "N"))
    total = query.count()
    rows = (query.order_by(asc(Avocat.nom), asc(Avocat.prenom))
                 .offset((page - 1) * page_size).limit(page_size).all())
    items = [AvocatOut(**avocat_to_dict(a, db)) for a in rows]
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
    base = db.query(Avocat).filter(Avocat.code.isnot(None))
    total = base.count()
    actifs = base.filter(Avocat.actpass == "A").count()
    inactifs = base.filter(Avocat.actpass == "P").count()
    mega = base.filter(Avocat.mega == "O").count()
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    nouveaux = base.filter(Avocat.created_at >= cutoff).count()
    return StatsOut(total=total, actifs=actifs, inactifs=inactifs, mega=mega, nouveaux_30j=nouveaux)


@router.get("/{avocat_id}", response_model=AvocatOut)
def get_avocat(avocat_id: str, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    # `avocat_id` dans les URLs représente désormais le `code` legacy (PK).
    a = db.query(Avocat).filter_by(code=avocat_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    return AvocatOut(**avocat_to_dict(a, db))


@router.get("/{avocat_id}/taxes")
def get_avocat_taxes(
    avocat_id: str,
    user: dict = Depends(get_current_user),
):
    """Retourne les numéros de taxes (TPS/TVQ) de l'avocat depuis Fvi.Avocats.

    Source : serveur CSJ-WEB01, base Fvi, table `avocats`.
    Lookup : `cart52uid = code` (mapping legacy depuis le VB).

    Colonnes :
      - cnotax1 = TPS
      - cnotax2 = TVQ
      - cfirme  = nom de la firme (info supplémentaire)

    Retourne `{tps, tvq, firme, found}`. Si l'avocat n'a pas d'entrée Fvi,
    found=false et les champs sont vides (pas d'erreur).
    """
    try:
        fvi = get_secondary_engine("Fvi")
    except Exception as e:  # noqa: BLE001
        # Fvi non configurée → on retourne un état vide, pas une 500.
        return {
            "tps": "", "tvq": "", "firme": "",
            "found": False, "error": f"Fvi non disponible : {e}",
        }

    sql = text("""
        SELECT cfirme, cnotax1, cnotax2
        FROM avocats
        WHERE RTRIM(LTRIM(cart52uid)) = :code
    """)
    try:
        with fvi.connect() as conn:
            row = conn.execute(sql, {"code": avocat_id}).first()
    except Exception as e:  # noqa: BLE001
        logger.warning("Lecture Fvi.avocats échouée pour %s : %s", avocat_id, e)
        return {
            "tps": "", "tvq": "", "firme": "",
            "found": False, "error": str(e)[:200],
        }

    if not row:
        return {"tps": "", "tvq": "", "firme": "", "found": False}

    return {
        "tps": (row[1] or "").strip() if row[1] else "",
        "tvq": (row[2] or "").strip() if row[2] else "",
        "firme": (row[0] or "").strip() if row[0] else "",
        "found": True,
    }



@router.post("", response_model=AvocatOut, status_code=201)
def create_avocat(payload: AvocatCreate,
                  user: dict = Depends(require_role("admin", "editeur")),
                  db: Session = Depends(get_db)):
    if payload.nas and not funcValidNoAssSoc(payload.nas):
        raise HTTPException(status_code=422, detail="Numéro NAS invalide (algorithme Luhn)")
    type_code = (payload.type_code or "A").upper()
    if type_code not in {"A", "N", "P"}:
        raise HTTPException(status_code=422, detail="type_code invalide (A/N/P)")

    now = now_local()
    factweb_on = bool(payload.factweb)

    last_err: Optional[Exception] = None
    for _ in range(5):
        code = _generate_avocat_code(db, type_code)
        codeusager_value = code if factweb_on else (payload.codeusager or "")
        a = Avocat(
            code=code, type_code=type_code,
            nom=payload.nom, prenom=payload.prenom,
            sectbar=payload.sectbar or "",
            mega=bool_to_yn(payload.mega),
            actpass="A" if payload.actif else "P",
            dateinscbarr=(payload.annee_barreau or payload.dateinscbarr or ""),
            payable=bool_to_yn(payload.payable),
            codebar=payload.codebar or "", comm=payload.comm or "",
            nas=payload.nas or "",
            depodirect=bool_to_yn(payload.depodirect),
            factweb=bool_to_yn(payload.factweb),
            confweb=bool_to_yn(payload.confweb),
            villeref=payload.villerref or "",
            surveil=bool_to_yn(payload.surveil),
            neq=payload.neq or "", codeusager=codeusager_value,
            created_at=now, updated_at=now, datemodif=now,
            usermodif=user.get("email", ""),
        )
        try:
            db.add(a)
            db.commit()
            db.refresh(a)
            if payload.adresse and any(payload.adresse.model_dump().values()):
                _create_or_update_main_address(db, a, payload.adresse.model_dump(), user.get("email", ""))
            # L'identifiant logique d'un avocat est désormais son `code`.
            write_audit(db, code, "create", user.get("email", ""),
                        f"Création de la fiche {code} — {payload.nom}, {payload.prenom}")
            return AvocatOut(**avocat_to_dict(a, db))
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
    a = db.query(Avocat).filter_by(code=avocat_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Avocat introuvable")

    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="Aucun champ à mettre à jour")

    yn_fields = {"mega", "payable", "depodirect", "factweb", "confweb", "surveil"}
    changed = []
    for k, v in data.items():
        if k == "adresse" and v is not None:
            _create_or_update_main_address(db, a, v if isinstance(v, dict) else v.model_dump(),
                                            user.get("email", ""))
            changed.append("adresse")
        elif k == "factweb":
            # Sync legacy : factweb=O → codeusager = code avocat ; factweb=N → codeusager = ""
            a.factweb = bool_to_yn(v)
            a.codeusager = a.code if v else ""
            changed.append("factweb")
        elif k == "codeusager":
            # codeusager n'est jamais modifié manuellement : il suit factweb.
            # On ignore silencieusement ce champ s'il est envoyé par le client.
            continue
        elif k in yn_fields:
            setattr(a, k, bool_to_yn(v))
            changed.append(k)
        elif k == "actif":
            a.actpass = "A" if v else "P"
            changed.append("actif")
        elif k == "annee_barreau":
            # alias front-end → colonne legacy
            a.dateinscbarr = v or ""
            changed.append("annee_barreau")
        elif k == "villerref":
            a.villeref = v or ""
            changed.append("villerref")
        elif k == "taxes":
            # Taxes (cNoTax1 / cNoTax2) — informations en lecture seule provenant
            # d'une autre BDD (autre serveur). Pas stockées dans CardAvo.
            continue
        else:
            setattr(a, k, v)
            changed.append(k)

    now = now_local()
    a.updated_at = now
    a.datemodif = now
    a.usermodif = user.get("email", "")
    db.commit()
    db.refresh(a)
    if changed:
        write_audit(db, avocat_id, "update", user.get("email", ""),
                    f"Modification : {', '.join(sorted(changed))}")
    return AvocatOut(**avocat_to_dict(a, db))


@router.delete("/{avocat_id}")
def delete_avocat(avocat_id: str, user: dict = Depends(require_role("admin")),
                  db: Session = Depends(get_db)):
    a = db.query(Avocat).filter_by(code=avocat_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    summary = f"Suppression de {a.code or ''} — {a.nom}, {a.prenom}"
    code = a.code
    if code:
        db.query(Adresse).filter_by(code=code).delete()
        db.query(InfoMega).filter_by(code=code).delete()
        db.query(Inhpra).filter_by(code=code).delete()
        db.query(InfoDistrict).filter_by(code=code).delete()
        # Mandats = table app web ; depuis ce refactor, `avocat_id` y stocke le code.
        db.query(Mandat).filter_by(avocat_id=code).delete()
    db.delete(a)
    db.commit()
    write_audit(db, code, "delete", user.get("email", ""), summary)
    return {"ok": True}
