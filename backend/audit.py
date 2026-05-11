"""Helpers d'audit + sérialisation pour les ORM."""
from __future__ import annotations

import json
import logging
import uuid
from typing import Optional

from sqlalchemy.orm import Session

from models import (
    Avocat, Adresse, InfoMega, InfoDistrict, Inhpra, AuditLog, Mandat,
    yn_to_bool,
)
from security import now_iso

logger = logging.getLogger("gestioncardex")


def write_audit(db: Session, avocat_id: str, action: str, user_email: str, summary: str) -> None:
    """Trace une modification d'avocat dans AuditLog. Best-effort."""
    try:
        entry = AuditLog(
            id=str(uuid.uuid4()),
            avocat_id=avocat_id,
            action=action,
            user_email=user_email or "système",
            summary=summary,
            timestamp=now_iso(),
        )
        db.add(entry)
        db.commit()
    except Exception as e:
        logger.warning(f"audit_log insert failed: {e}")
        db.rollback()


# ============================================================
#         Sérialisations ORM → dict (réutilisées partout)
# ============================================================
def avocat_to_dict(a: Avocat) -> dict:
    adr_data = {}
    if a.adresse_courante:
        try:
            adr_data = json.loads(a.adresse_courante)
        except (json.JSONDecodeError, TypeError):
            adr_data = {}
    return {
        "id": a.id or "",
        "code": a.code or "",
        "type_code": a.type_code or "A",
        "nom": a.nom or "",
        "prenom": a.prenom or "",
        "sectbar": a.sectbar or "",
        "mega": yn_to_bool(a.mega),
        "actif": bool(a.actif) if a.actif is not None else True,
        "attente": bool(a.attente) if a.attente is not None else False,
        "annee_barreau": a.annee_barreau or "",
        "dateinscbarr": a.dateinscbarr or "",
        "payable": yn_to_bool(a.payable),
        "codebar": a.codebar or "",
        "comm": a.comm or "",
        "nas": a.nas or "",
        "taxes": a.taxes or "",
        "depodirect": yn_to_bool(a.depodirect),
        "factweb": yn_to_bool(a.factweb),
        "confweb": yn_to_bool(a.confweb),
        "villerref": a.villerref or a.villeref or "",
        "surveil": yn_to_bool(a.surveil),
        "neq": a.neq or "",
        "codeusager": a.codeusager or "",
        "adresse": adr_data or {},
        "created_at": a.created_at or "",
        "updated_at": a.updated_at or "",
        "usermodif": a.usermodif or "",
    }


def adresse_to_dict(adr: Adresse) -> dict:
    return {
        "id": adr.id,
        "avocat_id": adr.avocat_id or "",
        "address": adr.address or "",
        "adresse2": adr.adresse2 or "",
        "adresse3": adr.adresse3 or "",
        "ville": adr.ville or "",
        "province": adr.province or "",
        "codepostal": adr.codepostal or "",
        "telephone": adr.telephone or "",
        "telephone2": adr.telephone2 or "",
        "fax": adr.fax or "",
        "email": adr.email or adr.adremail or "",
        "courant": yn_to_bool(adr.courant),
        "created_at": adr.created_at or "",
        "updated_at": adr.updated_at or "",
    }


def mega_to_dict(m: InfoMega, districts: list[int]) -> dict:
    return {
        "id": m.id,
        "avocat_id": m.avocat_id or "",
        "sectbar": m.sectbar or "",
        "districthab": m.districthab or "",
        "francais": yn_to_bool(m.francais),
        "anglais": yn_to_bool(m.anglais),
        "autres": m.autres or "",
        "experience": m.experience or 0,
        "details": m.details or "",
        "art486": yn_to_bool(m.art486),
        "art672": yn_to_bool(m.art672),
        "art684": yn_to_bool(m.art684),
        "commentaire": m.commentaire or "",
        "dateinsc": m.dateinsc or "",
        "districts": districts,
        "tous_districts": bool(m.tous_districts),
        "updated_at": m.updated_at or "",
        "usermodif": m.usermodif or "",
    }


def inhab_to_dict(i: Inhpra) -> dict:
    return {
        "id": i.uuid or str(i.Id),
        "avocat_id": i.avocat_id or "",
        "datedeb": i.datedeb or "",
        "datefin": i.datefin or "",
        "comm": i.comm or "",
        "created_at": i.created_at or "",
        "updated_at": i.updated_at or "",
    }


def mandat_to_dict(m: Mandat) -> dict:
    return {
        "id": m.id, "avocat_id": m.avocat_id, "requerant": m.requerant or "",
        "article": m.article, "date_ordonnance": m.date_ordonnance or "",
        "date_emission": m.date_emission or "", "numero": m.numero or "",
        "groupe": m.groupe, "commentaire": m.commentaire or "",
        "created_at": m.created_at, "updated_at": m.updated_at,
        "usermodif": m.usermodif or "",
    }
