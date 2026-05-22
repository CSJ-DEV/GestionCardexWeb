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


# ============================================================
#         Mapping legacy ↔ web (Avocats)
# ============================================================
# actpass : 'A' = Actif, 'P' = Passif (legacy VB).
# L'API web expose `actif` (bool) pour ne pas casser le frontend.
def actpass_to_bool(v) -> bool:
    return (v or "A").upper() != "P"


def bool_to_actpass(v) -> str:
    return "A" if v else "P"


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
def _fetch_adresse_courante(db: Optional[Session], a: Avocat) -> dict:
    """Récupère l'adresse principale via jointure Avocats.adrcour = Adresses.noseq.

    Si `db` n'est pas fourni, retourne {} (les callers qui veulent l'adresse
    doivent passer la session pour éviter d'oublier la jointure).
    """
    if db is None or not a.adrcour or not a.code:
        return {}
    adr = (db.query(Adresse)
             .filter(Adresse.code == a.code, Adresse.noseq == a.adrcour)
             .first())
    if not adr:
        return {}
    return {
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
    }


def avocat_to_dict(a: Avocat, db: Optional[Session] = None) -> dict:
    """Sérialise un avocat ORM vers le format JSON attendu par le frontend.

    Le frontend attend des clés modernes (`actif`, `annee_barreau`, `adresse`...)
    qui n'existent pas en base. On les déduit ici des colonnes legacy.
    """
    return {
        "id": a.id or "",
        "code": a.code or "",
        "type_code": a.type_code or "A",
        "nom": a.nom or "",
        "prenom": a.prenom or "",
        "sectbar": a.sectbar or "",
        "mega": yn_to_bool(a.mega),
        # actpass 'A'/'P' → bool actif
        "actif": actpass_to_bool(a.actpass),
        # surveil 'O'/'N' → bool (champ surveillance, distinct de attente)
        "surveil": yn_to_bool(a.surveil),
        # Année d'inscription au barreau (champ legacy `dateinscbarr`,
        # contient juste l'année ex "2010"). On expose aussi `annee_barreau`
        # comme alias pour le frontend existant.
        "dateinscbarr": a.dateinscbarr or "",
        "annee_barreau": a.dateinscbarr or "",
        "payable": yn_to_bool(a.payable),
        "codebar": a.codebar or "",
        "comm": a.comm or "",
        "nas": a.nas or "",
        # taxes : à revoir, viendra d'une autre BDD (cNoTax1/cNoTax2)
        "taxes": "",
        "depodirect": yn_to_bool(a.depodirect),
        "factweb": yn_to_bool(a.factweb),
        "confweb": yn_to_bool(a.confweb),
        # villerref (web) = villeref (legacy)
        "villerref": a.villeref or "",
        "neq": a.neq or "",
        "codeusager": a.codeusager or "",
        # Adresse principale : jointure si db fourni, sinon dict vide
        "adresse": _fetch_adresse_courante(db, a),
        "created_at": a.created_at or "",
        "updated_at": a.updated_at or a.datemodif or "",
        "usermodif": a.usermodif or "",
    }


def adresse_to_dict(adr: Adresse) -> dict:
    return {
        # Le frontend attend `id` ; on expose RowId legacy sous ce nom pour
        # garder l'API REST stable sans dupliquer de colonne.
        "id": adr.RowId,
        "code": adr.code or "",
        "address": adr.address or "",
        "adresse2": adr.adresse2 or "",
        "adresse3": adr.adresse3 or "",
        "ville": adr.ville or "",
        "province": adr.province or "",
        "codepostal": adr.codepostal or "",
        "telephone": adr.telephone or "",
        "telephone2": adr.telephone2 or "",
        "fax": adr.fax or "",
        "email": adr.adremail or "",
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
