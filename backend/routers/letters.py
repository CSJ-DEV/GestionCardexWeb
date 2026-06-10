"""Routes pour la lettre officielle CSJ + configuration du signataire.

- GET  /api/avocats/{code}/letter-preview  → PDF stream (admin/editeur/ti)
- GET  /api/letter-config                  → lit la config singleton (TI)
- PUT  /api/letter-config                  → MAJ signataire + signature image (TI)
"""
from __future__ import annotations

import base64
import logging
from io import BytesIO
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from audit import write_audit
from database import get_db
from models import Avocat, Adresse, LetterConfig
from security import now_local, require_role
import mailer

logger = logging.getLogger("gestioncardex.letters")


# ============================================================
#  Template de courriel (sujet + corps HTML) — stocké en BDD
# ============================================================
# Valeurs PAR DÉFAUT utilisées tant que le DBA n'a pas exécuté l'ALTER
# TABLE ajoutant les colonnes email_subject / email_body. Le code
# fonctionne dans les 2 cas via raw SQL avec try/except.
DEFAULT_EMAIL_SUBJECT = (
    "Réinitialisation de vos mots de passe — Aide juridique du Québec"
)
DEFAULT_EMAIL_BODY = (
    "Bonjour Me {nom},\n\n"
    "Vos mots de passe Web de l'application GestionCardex ont été "
    "réinitialisés à votre demande.\n\n"
    "Vous trouverez en pièce jointe (PDF) vos nouveaux identifiants "
    "(Mot de passe 1 et Mot de passe 2).\n\n"
    "Pour des raisons de sécurité, conservez ce document en lieu sûr et "
    "ne le transférez pas par courriel.\n\n"
    "Ceci est un message automatique — merci de ne pas y répondre."
)


def _get_email_template_raw(db: Session) -> tuple[str, str]:
    """Lit (subject, body) depuis LetterConfig via raw SQL.

    Retourne les valeurs par défaut si :
      - les colonnes n'existent pas encore (prod sans ALTER) → SQL error
      - les colonnes sont NULL ou vides
    """
    try:
        row = db.execute(
            text("SELECT email_subject, email_body FROM LetterConfig WHERE id = 1")
        ).first()
        if row is not None:
            return (row[0] or DEFAULT_EMAIL_SUBJECT, row[1] or DEFAULT_EMAIL_BODY)
    except Exception as e:  # noqa: BLE001
        logger.info("Colonnes email_subject/email_body absentes (fallback) : %s", e)
    return (DEFAULT_EMAIL_SUBJECT, DEFAULT_EMAIL_BODY)


def _set_email_template_raw(db: Session, subject: str, body: str) -> bool:
    """Écrit (subject, body) dans LetterConfig via raw SQL.

    Retourne True si succès, False si les colonnes n'existent pas encore.
    Ne lève pas — l'appelant décide quoi faire de l'échec.
    """
    try:
        db.execute(
            text(
                "UPDATE LetterConfig "
                "SET email_subject = :s, email_body = :b "
                "WHERE id = 1"
            ),
            {"s": subject, "b": body},
        )
        return True
    except Exception as e:  # noqa: BLE001
        logger.warning("Écriture email_subject/email_body impossible : %s", e)
        return False

# Routes /avocats/{code}/letter-preview (mêmes droits que le reset)
router_avocat = APIRouter(prefix="/avocats", tags=["letters"])
# Routes /letter-config (réservées TI)
router_config = APIRouter(prefix="/letter-config", tags=["letter-config"])


# ============================================================
#                      Lettre PDF (preview)
# ============================================================
@router_avocat.get("/{avocat_id}/letter-preview")
def letter_preview(
    avocat_id: str,
    user: dict = Depends(require_role("admin", "editeur")),
    db: Session = Depends(get_db),
):
    """Génère le PDF de la lettre officielle (Code utilisateur + mots de passe).
    Utilise les motpasse1/motpasse2 actuellement en BDD — n'en génère pas de
    nouveaux. Le PDF est streamé inline (s'ouvre dans le navigateur)."""
    avo = db.query(Avocat).filter_by(code=avocat_id).first()
    if not avo:
        raise HTTPException(status_code=404, detail="Avocat introuvable")

    # Adresse courante via Avocat.adrcour (FK Adresses.noseq)
    adresse = None
    if avo.adrcour:
        adresse = db.query(Adresse).filter_by(noseq=avo.adrcour).first()

    config = db.query(LetterConfig).filter_by(id=1).first()

    pdf_bytes = mailer.generate_letter_pdf(
        avocat_code=avo.code,
        avocat_nom=avo.nom or "",
        avocat_prenom=avo.prenom or "",
        motpasse1=avo.motpasse1 or "",
        motpasse2=avo.motpasse2 or "",
        adresse=adresse,
        config=config,
    )

    write_audit(db, avocat_id, "letter_preview", user.get("email", ""),
                "Aperçu de la lettre officielle (code utilisateur + mdp)")

    filename = f"lettre_{avo.code}_{now_local().strftime('%Y%m%d')}.pdf"
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


# ============================================================
#                  Configuration de la lettre (TI)
# ============================================================
class LetterConfigOut(BaseModel):
    signataire_nom: str
    signataire_titre: str
    signataire_affiliation: str
    has_signature: bool
    signature_mime: Optional[str] = None
    email_subject: str
    email_body: str
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None


class LetterConfigIn(BaseModel):
    signataire_nom: str
    signataire_titre: str
    signataire_affiliation: str = "Commission des services juridiques"
    # base64 sans le préfixe "data:image/...;base64," (envoyé séparément via mime)
    signature_image_base64: Optional[str] = None
    signature_mime: Optional[str] = None  # "image/png" ou "image/jpeg"
    clear_signature: bool = False  # si True : efface l'image existante
    # Template de courriel (optionnel — défaut si absent ou colonnes non créées)
    email_subject: Optional[str] = None
    email_body: Optional[str] = None


def _serialize_config(c: LetterConfig, db: Session) -> LetterConfigOut:
    subject, body = _get_email_template_raw(db)
    return LetterConfigOut(
        signataire_nom=c.signataire_nom or "",
        signataire_titre=c.signataire_titre or "",
        signataire_affiliation=c.signataire_affiliation or "",
        has_signature=bool(c.signature_image_base64),
        signature_mime=c.signature_mime,
        email_subject=subject,
        email_body=body,
        updated_at=c.updated_at.isoformat() if c.updated_at else None,
        updated_by=c.updated_by,
    )


@router_config.get("", response_model=LetterConfigOut)
def get_letter_config(
    user: dict = Depends(require_role("ti")),
    db: Session = Depends(get_db),
):
    """Retourne la config singleton (id=1). La crée avec des valeurs vides si
    elle n'existe pas (cas dev local)."""
    c = db.query(LetterConfig).filter_by(id=1).first()
    if c is None:
        c = LetterConfig(
            id=1,
            signataire_nom="M. Yves Boisvert, CPA, CGA",
            signataire_titre="Directeur des services financiers",
            signataire_affiliation="Commission des services juridiques",
            updated_at=now_local(),
            updated_by="system",
        )
        db.add(c)
        db.commit()
        db.refresh(c)
    return _serialize_config(c, db)


@router_config.get("/signature-image")
def get_signature_image(
    user: dict = Depends(require_role("ti")),
    db: Session = Depends(get_db),
):
    """Retourne l'image signature courante en bytes (pour aperçu dans l'UI TI)."""
    c = db.query(LetterConfig).filter_by(id=1).first()
    if not c or not c.signature_image_base64:
        raise HTTPException(status_code=404, detail="Aucune signature configurée")
    try:
        img_bytes = base64.b64decode(c.signature_image_base64)
    except Exception:
        raise HTTPException(status_code=500, detail="Signature image corrompue")
    return StreamingResponse(
        BytesIO(img_bytes),
        media_type=c.signature_mime or "image/png",
    )


@router_config.put("", response_model=LetterConfigOut)
def update_letter_config(
    payload: LetterConfigIn,
    user: dict = Depends(require_role("ti")),
    db: Session = Depends(get_db),
):
    """MAJ de la config singleton (TI uniquement). Si `clear_signature=True`,
    la signature est effacée. Sinon, si `signature_image_base64` est fournie,
    elle écrase l'ancienne. Sinon, l'image existante reste inchangée."""
    c = db.query(LetterConfig).filter_by(id=1).first()
    if c is None:
        c = LetterConfig(id=1, updated_at=now_local())
        db.add(c)

    c.signataire_nom = payload.signataire_nom.strip()
    c.signataire_titre = payload.signataire_titre.strip()
    c.signataire_affiliation = payload.signataire_affiliation.strip() \
        or "Commission des services juridiques"

    if payload.clear_signature:
        c.signature_image_base64 = None
        c.signature_mime = None
    elif payload.signature_image_base64:
        # Validation basique : taille max 200 KB de base64 (~150 KB binaire)
        if len(payload.signature_image_base64) > 200_000:
            raise HTTPException(
                status_code=400,
                detail="Signature trop volumineuse (max ~150 KB binaire).",
            )
        if payload.signature_mime not in ("image/png", "image/jpeg"):
            raise HTTPException(
                status_code=400,
                detail="Format de signature invalide (PNG ou JPEG uniquement).",
            )
        c.signature_image_base64 = payload.signature_image_base64
        c.signature_mime = payload.signature_mime

    c.updated_at = now_local()
    c.updated_by = user.get("email", "")
    db.commit()
    db.refresh(c)

    # Template email — écriture séparée (peut échouer si colonnes absentes)
    if payload.email_subject is not None or payload.email_body is not None:
        subject = (payload.email_subject or DEFAULT_EMAIL_SUBJECT).strip()
        body = (payload.email_body or DEFAULT_EMAIL_BODY).strip()
        if not _set_email_template_raw(db, subject, body):
            # En prod sans ALTER : ne bloque pas la sauvegarde du signataire
            logger.warning(
                "Sauvegarde signataire OK mais template email NON sauvegardé "
                "(colonnes email_subject/email_body absentes)."
            )
        else:
            db.commit()

    return _serialize_config(c, db)
