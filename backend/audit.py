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
from security import now_local

logger = logging.getLogger("gestioncardex")


def _s(v) -> str:
    """Coerce une valeur legacy en string « propre ».

    SQL Server CHAR(N) padding the values with trailing spaces (et parfois
    leading) → on supprime systématiquement les espaces périphériques pour
    éviter d'afficher des cellules « pleines d'espaces » dans le front.
    """
    if v is None:
        return ""
    return str(v).strip()


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
            timestamp=now_local(),
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
        "address": _s(adr.address),
        "adresse2": _s(adr.adresse2),
        "adresse3": _s(adr.adresse3),
        "ville": _s(adr.ville),
        "province": _s(adr.province),
        "codepostal": _s(adr.codepostal),
        "telephone": _s(adr.telephone),
        "telephone2": _s(adr.telephone2),
        "fax": _s(adr.fax),
        "email": _s(adr.adremail),
    }


def avocat_to_dict(a: Avocat, db: Optional[Session] = None) -> dict:
    """Sérialise un avocat ORM vers le format JSON attendu par le frontend.

    Le frontend attend des clés modernes (`actif`, `annee_barreau`, `adresse`...)
    qui n'existent pas en base. On les déduit ici des colonnes legacy.
    """
    # type_code legacy : pour les fiches anciennes la colonne `type_code` peut
    # être vide (CHAR(1) jamais renseigné) → on déduit le type à partir du
    # préfixe du `code` (P00963 → "P", A00012 → "A", N20001 → "N").
    raw_type = _s(a.type_code)
    if not raw_type and a.code:
        first = str(a.code).strip().upper()[:1]
        raw_type = first if first in ("A", "P", "N") else "A"
    elif not raw_type:
        raw_type = "A"
    return {
        # Pas de colonne `id` en legacy — on expose le `code` sous ce nom pour
        # garder l'API stable côté frontend.
        "id": _s(a.code),
        "code": _s(a.code),
        "type_code": raw_type,
        "nom": _s(a.nom),
        "prenom": _s(a.prenom),
        "sectbar": _s(a.sectbar),
        "mega": yn_to_bool(a.mega),
        # actpass 'A'/'P' → bool actif
        "actif": actpass_to_bool(a.actpass),
        # surveil 'O'/'N' → bool (champ de surveillance legacy `Surveil`)
        "surveil": yn_to_bool(a.surveil),
        # Année d'inscription au barreau (champ legacy `dateinscbarr`,
        # contient juste l'année ex "2010"). On expose aussi `annee_barreau`
        # comme alias pour le frontend existant.
        "dateinscbarr": _s(a.dateinscbarr),
        "annee_barreau": _s(a.dateinscbarr),
        "payable": yn_to_bool(a.payable),
        "codebar": _s(a.codebar),
        "comm": _s(a.comm),
        "nas": _s(a.nas),
        # taxes : lecture seule, viendra d'une autre BDD (cNoTax1 TPS / cNoTax2 TVQ)
        "taxes": "",
        "depodirect": yn_to_bool(a.depodirect),
        "factweb": yn_to_bool(a.factweb),
        "confweb": yn_to_bool(a.confweb),
        # villerref (web) = villeref (legacy)
        "villerref": _s(a.villeref),
        "neq": _s(a.neq),
        "codeusager": _s(a.codeusager),
        # Indicateurs : motpasse1/motpasse2 sont définis ? (valeurs jamais exposées ici)
        "motpasse1_set": bool(_s(a.motpasse1)),
        "motpasse2_set": bool(_s(a.motpasse2)),
        # Adresse principale : jointure si db fourni, sinon dict vide
        "adresse": _fetch_adresse_courante(db, a),
        "created_at": a.created_at or "",
        "updated_at": a.updated_at or a.datemodif or "",
        "usermodif": _s(a.usermodif),
    }


def adresse_to_dict(adr: Adresse) -> dict:
    return {
        # Le frontend attend `id` ; on expose RowId legacy sous ce nom pour
        # garder l'API REST stable sans dupliquer de colonne.
        "id": adr.RowId,
        "code": _s(adr.code),
        "address": _s(adr.address),
        "adresse2": _s(adr.adresse2),
        "adresse3": _s(adr.adresse3),
        "ville": _s(adr.ville),
        "province": _s(adr.province),
        "codepostal": _s(adr.codepostal),
        "telephone": _s(adr.telephone),
        "telephone2": _s(adr.telephone2),
        "fax": _s(adr.fax),
        "email": _s(adr.adremail),
        "courant": yn_to_bool(adr.courant),
        "created_at": adr.created_at or "",
        "updated_at": adr.updated_at or "",
    }


def mega_to_dict(m: InfoMega, districts: list[int], avocat_id: str = "",
                 tous_districts: bool = False) -> dict:
    return {
        # Pas d'`id` propre — le profil Méga est identifié par `code` (1↔1 avocat).
        "id": _s(m.code),
        "avocat_id": avocat_id,
        "code": _s(m.code),
        "sectbar": _s(m.sectbar),
        "districthab": _s(m.districthab),
        "francais": yn_to_bool(m.francais),
        "anglais": yn_to_bool(m.anglais),
        "autres": _s(m.autres),
        "experience": m.experience or 0,
        "details": _s(m.details),
        "art486": yn_to_bool(m.art486),
        "art672": yn_to_bool(m.art672),
        "art684": yn_to_bool(m.art684),
        "commentaire": _s(m.commentaire),
        "dateinsc": m.dateinsc or "",
        "districts": districts,
        "tous_districts": tous_districts,
        "updated_at": m.datemodif or "",
        "usermodif": _s(m.usermodif),
    }


def inhab_to_dict(i: Inhpra, avocat_id: str = "") -> dict:
    return {
        # `Id` INT legacy sérialisé en string pour l'API REST
        "id": str(i.Id) if i.Id is not None else "",
        "avocat_id": avocat_id,
        "code": _s(i.code),
        "datedeb": i.datedeb or "",
        "datefin": i.datefin or "",
        "comm": _s(i.comm),
    }


def mandat_to_dict(m: Mandat) -> dict:
    return {
        "id": m.id, "avocat_id": m.avocat_id, "requerant": _s(m.requerant),
        "article": m.article, "date_ordonnance": m.date_ordonnance or "",
        "date_emission": m.date_emission or "", "numero": _s(m.numero),
        "groupe": m.groupe, "commentaire": _s(m.commentaire),
        "created_at": m.created_at, "updated_at": m.updated_at,
        "usermodif": _s(m.usermodif),
    }
