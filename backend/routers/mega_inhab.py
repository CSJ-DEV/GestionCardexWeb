"""Routes Méga + Inhabilité + Web password (regroupées car liées à un avocat)."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import desc
from sqlalchemy.orm import Session

from audit import write_audit, mega_to_dict, inhab_to_dict
from database import get_db
from models import Avocat, Adresse, InfoMega, InfoDistrict, Inhpra, bool_to_yn
from schemas import InfoMegaIn, InhabIn
from security import get_current_user, now_local, require_role
import mailer


def _parse_date(value):
    """Convertit une string ISO en datetime. Renvoie None si vide/invalide."""
    if not value:
        return None
    if hasattr(value, "year"):  # déjà datetime/date
        return value
    from datetime import datetime as _dt
    s = str(value).strip()
    if not s:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return _dt.strptime(s, fmt)
        except ValueError:
            continue
    # Fallback ISO (gère les fuseaux)
    try:
        return _dt.fromisoformat(s.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return None

router = APIRouter(prefix="/avocats", tags=["mega-inhab-web"])


# ---------- Méga ----------
# Total des districts QC (référence pour déduire `tous_districts`).
# Voir frontend `QC_DISTRICTS` : 18 districts judiciaires.
_QC_DISTRICTS_TOTAL = 18


def _get_avocat_or_404(db: Session, avocat_id: str) -> Avocat:
    # `avocat_id` = `code` legacy depuis le refactor PK
    avo = db.query(Avocat).filter_by(code=avocat_id).first()
    if not avo:
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    return avo


@router.get("/{avocat_id}/mega")
def get_mega(avocat_id: str, user: dict = Depends(get_current_user),
             db: Session = Depends(get_db)):
    avo = _get_avocat_or_404(db, avocat_id)
    m = db.query(InfoMega).filter_by(code=avo.code).first()
    if not m:
        return {}
    districts = [d.nodist for d in db.query(InfoDistrict).filter_by(code=avo.code).all()]
    # Déduction : tous_districts si toutes les options du QC sont cochées
    tous = len(districts) >= _QC_DISTRICTS_TOTAL
    return mega_to_dict(m, districts, avocat_id, tous_districts=tous)


@router.put("/{avocat_id}/mega")
def upsert_mega(avocat_id: str, payload: InfoMegaIn,
                user: dict = Depends(require_role("admin", "editeur")),
                db: Session = Depends(get_db)):
    avo = _get_avocat_or_404(db, avocat_id)
    now = now_local()
    m = db.query(InfoMega).filter_by(code=avo.code).first()
    if not m:
        m = InfoMega(code=avo.code)
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
    m.dateinsc = _parse_date(payload.dateinsc)
    m.mega = "O"
    m.datemodif = now
    m.usermodif = user.get("email", "")

    if avo.code:
        db.query(InfoDistrict).filter_by(code=avo.code).delete()
        for nodist in (payload.districts or []):
            db.add(InfoDistrict(code=avo.code, nodist=int(nodist)))

    avo.mega = "O"
    avo.updated_at = now
    avo.datemodif = now
    db.commit()
    write_audit(db, avocat_id, "mega_update", user.get("email", ""),
                f"Profil Méga mis à jour (sectbar={payload.sectbar or '—'}, exp={payload.experience or 0} an(s), districts={len(payload.districts or [])})")
    return {"ok": True}


@router.delete("/{avocat_id}/mega")
def delete_mega(avocat_id: str, user: dict = Depends(require_role("admin", "editeur")),
                db: Session = Depends(get_db)):
    avo = db.query(Avocat).filter_by(code=avocat_id).first()
    if avo and avo.code:
        db.query(InfoMega).filter_by(code=avo.code).delete()
        db.query(InfoDistrict).filter_by(code=avo.code).delete()
        avo.mega = "N"
    db.commit()
    write_audit(db, avocat_id, "mega_delete", user.get("email", ""), "Profil Méga supprimé")
    return {"ok": True}


# ---------- Inhabilité ----------
@router.get("/{avocat_id}/inhabilites")
def list_inhab(avocat_id: str, user: dict = Depends(get_current_user),
               db: Session = Depends(get_db)):
    avo = _get_avocat_or_404(db, avocat_id)
    rows = (db.query(Inhpra).filter_by(code=avo.code)
              .order_by(desc(Inhpra.datedeb)).limit(200).all())
    return [inhab_to_dict(i, avocat_id) for i in rows]


@router.post("/{avocat_id}/inhabilites", status_code=201)
def create_inhab(avocat_id: str, payload: InhabIn,
                 user: dict = Depends(require_role("admin", "editeur")),
                 db: Session = Depends(get_db)):
    avo = _get_avocat_or_404(db, avocat_id)
    i = Inhpra(code=avo.code,
               datedeb=_parse_date(payload.datedeb),
               datefin=_parse_date(payload.datefin),
               comm=payload.comm or "")
    db.add(i)
    db.commit()
    db.refresh(i)
    write_audit(db, avocat_id, "inhab_create", user.get("email", ""),
                f"Période d'inhabilité ajoutée : {payload.datedeb} → {payload.datefin or 'en cours'}")
    return inhab_to_dict(i, avocat_id)


@router.put("/{avocat_id}/inhabilites/{inhab_id}")
def update_inhab(avocat_id: str, inhab_id: str, payload: InhabIn,
                 user: dict = Depends(require_role("admin", "editeur")),
                 db: Session = Depends(get_db)):
    avo = _get_avocat_or_404(db, avocat_id)
    # `inhab_id` est l'`Id` INT legacy (sérialisé en string côté API)
    try:
        legacy_id = int(inhab_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=404, detail="Période introuvable")
    i = db.query(Inhpra).filter_by(Id=legacy_id, code=avo.code).first()
    if not i:
        raise HTTPException(status_code=404, detail="Période introuvable")
    i.datedeb = _parse_date(payload.datedeb)
    i.datefin = _parse_date(payload.datefin)
    i.comm = payload.comm or ""
    db.commit()
    write_audit(db, avocat_id, "inhab_update", user.get("email", ""),
                f"Période d'inhabilité modifiée : {payload.datedeb} → {payload.datefin or 'en cours'}")
    return {"ok": True}


@router.delete("/{avocat_id}/inhabilites/{inhab_id}")
def delete_inhab(avocat_id: str, inhab_id: str,
                 user: dict = Depends(require_role("admin", "editeur")),
                 db: Session = Depends(get_db)):
    avo = _get_avocat_or_404(db, avocat_id)
    try:
        legacy_id = int(inhab_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=404, detail="Période introuvable")
    i = db.query(Inhpra).filter_by(Id=legacy_id, code=avo.code).first()
    if not i:
        raise HTTPException(status_code=404, detail="Période introuvable")
    summary = f"Période supprimée : {i.datedeb or '?'} → {i.datefin or 'en cours'}"
    db.delete(i)
    db.commit()
    write_audit(db, avocat_id, "inhab_delete", user.get("email", ""), summary)
    return {"ok": True}


# ---------- Mots de passe Web (legacy VB : motpasse1 + motpasse2) ----------
# Reproduit fidèlement `subCreerPwd()` de frmAvocat.vb :
#   Do
#       motpasse = Trim(Int((160000 * Rnd()) + 10000))
#   Loop Until VerifMotPasseWeb(motpasse, 1|2) = True And Len(motpasse) > 4
#
# Plage : 10000..169999 (5 ou 6 chiffres), stocké EN CLAIR dans CHAR(8).
# Le code legacy stocke les valeurs en clair pour interop avec les services
# externes (portails Barreau/factweb).
import random


def _generate_unique_motpasse(db: Session, column) -> str:
    """Génère un motpasse 5-6 chiffres unique sur la colonne donnée.

    Boucle anti-collision à l'identique du legacy : tire un entier dans
    [10000, 169999], vérifie l'unicité via SELECT, recommence sinon.
    """
    for _ in range(200):  # garde-fou : 200 tentatives max
        candidate = str(random.randint(10000, 169999))
        if len(candidate) <= 4:
            continue
        exists = db.query(Avocat).filter(column == candidate).first()
        if not exists:
            return candidate
    raise HTTPException(status_code=500, detail="Impossible de générer un mot de passe unique")


class ResetPasswordsIn(BaseModel):
    """Payload optionnel pour le reset. Si `send_email=True`, envoie un courriel
    à l'avocat avec un PDF des nouveaux identifiants en pièce jointe."""
    send_email: bool = False
    email: EmailStr | None = None  # Si None et send_email=True, on utilise adresse.adremail


def _send_pwd_email_task(to_email: str, code: str, nom: str, prenom: str,
                        mp1: str, mp2: str, db_url_hint: str = ""):
    """Tâche background — best-effort, ne lève jamais."""
    try:
        mailer.send_password_reset_email(to_email, code, nom, prenom, mp1, mp2)
    except Exception as e:
        # Logger uniquement — le reset principal a déjà commit en BDD.
        import logging
        logging.getLogger("gestioncardex.mailer").error(
            "Envoi du courriel de reset pour %s (avocat %s) échoué : %s",
            to_email, code, e,
        )


@router.post("/{avocat_id}/reset-passwords")
def reset_passwords(avocat_id: str,
                    background_tasks: BackgroundTasks,
                    payload: ResetPasswordsIn | None = None,
                    user: dict = Depends(require_role("admin", "editeur")),
                    db: Session = Depends(get_db)):
    """Régénère motpasse1 + motpasse2 (legacy `subCreerPwd` + `funcSavePwd`).

    Si `payload.send_email=True`, envoie un courriel à l'avocat (best-effort)
    avec un PDF contenant les nouveaux identifiants.
    """
    avo = db.query(Avocat).filter_by(code=avocat_id).first()
    if not avo:
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    mp1 = _generate_unique_motpasse(db, Avocat.motpasse1)
    mp2 = _generate_unique_motpasse(db, Avocat.motpasse2)
    now = now_local()
    avo.motpasse1 = mp1
    avo.motpasse2 = mp2
    avo.datemodif = now
    avo.updated_at = now
    avo.usermodif = user.get("email", "")
    db.commit()
    write_audit(db, avocat_id, "pwd_reset", user.get("email", ""),
                "Réinitialisation des mots de passe Web (motpasse1 + motpasse2)")

    # ----- Envoi courriel (best-effort, ne bloque pas la réponse) -----
    email_sent_to = None
    email_error = None
    if payload and payload.send_email:
        if not mailer.is_email_enabled():
            email_error = "Service courriel non configuré sur le serveur."
        else:
            # Détermine l'adresse cible : payload > adresse courante de l'avocat
            target = (payload.email or "").strip().lower() or None
            if not target and avo.adrcour:
                adr = db.query(Adresse).filter_by(noseq=avo.adrcour).first()
                if adr and adr.adremail:
                    target = adr.adremail.strip().lower()
            if not target:
                email_error = "Aucune adresse courriel disponible pour cet avocat."
            else:
                background_tasks.add_task(
                    _send_pwd_email_task,
                    to_email=target,
                    code=avo.code, nom=avo.nom or "", prenom=avo.prenom or "",
                    mp1=mp1, mp2=mp2,
                )
                email_sent_to = target
                write_audit(db, avocat_id, "pwd_email", user.get("email", ""),
                            f"Courriel de reset programmé vers {target}")

    return {
        "motpasse1": mp1,
        "motpasse2": mp2,
        "email_sent_to": email_sent_to,
        "email_error": email_error,
    }


@router.get("/email-status")
def email_status(_=Depends(get_current_user)):
    """Indique si le service courriel ACS est configuré côté serveur."""
    return {"enabled": mailer.is_email_enabled()}


@router.post("/{avocat_id}/clear-passwords")
def clear_passwords(avocat_id: str,
                    user: dict = Depends(require_role("admin", "editeur")),
                    db: Session = Depends(get_db)):
    """Efface les 2 mots de passe (équivalent du `objAvocat.motpasse1 = ""` VB)."""
    avo = db.query(Avocat).filter_by(code=avocat_id).first()
    if not avo:
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    avo.motpasse1 = ""
    avo.motpasse2 = ""
    avo.updated_at = now_local()
    avo.datemodif = avo.updated_at
    avo.usermodif = user.get("email", "")
    db.commit()
    write_audit(db, avocat_id, "pwd_clear", user.get("email", ""),
                "Effacement des mots de passe Web")
    return {"ok": True}


@router.get("/{avocat_id}/passwords")
def get_passwords(avocat_id: str,
                  user: dict = Depends(require_role("ti")),
                  db: Session = Depends(get_db)):
    """Retourne motpasse1 + motpasse2 en clair — réservé au rôle TI (audit-sensible)."""
    avo = db.query(Avocat).filter_by(code=avocat_id).first()
    if not avo:
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    write_audit(db, avocat_id, "pwd_view", user.get("email", ""),
                "Consultation des mots de passe Web par le TI")
    return {
        "motpasse1": (avo.motpasse1 or "").strip(),
        "motpasse2": (avo.motpasse2 or "").strip(),
    }


# ---------- Audit log (admin only) ----------
audit_router = APIRouter(prefix="/avocats", tags=["audit"])


@audit_router.get("/{avocat_id}/audit")
def list_audit(avocat_id: str, user: dict = Depends(require_role("admin")),
               db: Session = Depends(get_db),
               page: int = 1, page_size: int = 20,
               action: str = ""):
    from models import AuditLog
    page = max(page, 1)
    page_size = min(max(page_size, 1), 200)
    base = db.query(AuditLog).filter_by(avocat_id=avocat_id)
    if action:
        base = base.filter(AuditLog.action == action)
    total = base.count()
    rows = (base.order_by(desc(AuditLog.timestamp))
                .offset((page - 1) * page_size).limit(page_size).all())
    items = [{"id": r.id, "avocat_id": r.avocat_id, "action": r.action,
              "user_email": r.user_email, "summary": r.summary or "",
              "timestamp": r.timestamp} for r in rows]
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@audit_router.get("/{avocat_id}/audit/export.csv")
def export_audit_csv(avocat_id: str, user: dict = Depends(require_role("admin")),
                     db: Session = Depends(get_db), action: str = ""):
    """Export CSV de l'historique complet d'un avocat — streamé pour gros volumes.

    Format Excel-compatible : BOM UTF-8 + séparateur `;` (alternative `,` standard).
    Colonnes : Date, Action, Utilisateur, Résumé. Streaming via yield_per(500).
    """
    import csv
    import io
    from datetime import datetime
    from fastapi.responses import StreamingResponse
    from models import AuditLog, Avocat

    avo = db.query(Avocat).filter_by(code=avocat_id).first()
    label = f"{avo.code or 'NA'}_{avo.nom}" if avo else "inconnu"
    label = "".join(c if c.isalnum() or c in "._-" else "_" for c in label)

    action_label = {
        "create": "Création", "update": "Modification", "delete": "Suppression",
        "adresse_create": "Adresse ajoutée", "adresse_update": "Adresse modifiée",
        "adresse_delete": "Adresse supprimée",
        "mega_update": "Méga", "mega_delete": "Méga supprimé",
        "inhab_create": "Inhabilité ajoutée", "inhab_update": "Inhabilité modifiée",
        "inhab_delete": "Inhabilité supprimée",
        "web_password_set": "Mot de passe web défini",
        "web_password_clear": "Mot de passe web effacé",
        "pwd_reset": "Réinitialisation mots de passe Web",
        "pwd_clear": "Effacement mots de passe Web",
        "pwd_view": "Consultation mots de passe (TI)",
    }

    def gen():
        # BOM UTF-8 pour qu'Excel ouvre correctement les accents
        yield "\ufeff".encode("utf-8")
        buf = io.StringIO()
        w = csv.writer(buf, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        w.writerow(["Date", "Heure", "Action", "Code action", "Utilisateur", "Résumé"])
        yield buf.getvalue().encode("utf-8")
        buf.seek(0); buf.truncate(0)

        q = (db.query(AuditLog).filter_by(avocat_id=avocat_id)
                              .order_by(desc(AuditLog.timestamp))
                              .yield_per(500))
        if action:
            q = q.filter(AuditLog.action == action)
        count = 0
        for r in q:
            ts = r.timestamp or ""
            try:
                d = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                date_str = d.strftime("%Y-%m-%d")
                heure_str = d.strftime("%H:%M:%S")
            except (ValueError, AttributeError):
                date_str, heure_str = ts, ""
            w.writerow([
                date_str, heure_str,
                action_label.get(r.action, r.action),
                r.action,
                r.user_email or "système",
                (r.summary or "").replace("\n", " ").replace("\r", " "),
            ])
            count += 1
            if count % 100 == 0:
                yield buf.getvalue().encode("utf-8")
                buf.seek(0); buf.truncate(0)
        if buf.tell():
            yield buf.getvalue().encode("utf-8")

    filename = f"historique_{label}_{datetime.now().strftime('%Y%m%d')}.csv"
    return StreamingResponse(
        gen(),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
            "X-Accel-Buffering": "no",
        },
    )
