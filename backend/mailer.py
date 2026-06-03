"""Helpers Azure Communication Services (ACS) Email.

Expose une API minimaliste :
    send_email(to, subject, body_html, body_text=None, attachments=None)

Le reste du code (routers) ne dépend que de cette fonction et ignore les
détails ACS. Le client est construit en lazy à partir de la connection
string en variable d'env ACS_CONNECTION_STRING.

Génération PDF via ReportLab pour la pièce jointe du reset de mots de passe.
"""
from __future__ import annotations

import os
import base64
import logging
from io import BytesIO
from typing import Optional, List, Dict, Any

from azure.communication.email import EmailClient
from azure.core.exceptions import HttpResponseError
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from security import now_local

logger = logging.getLogger("gestioncardex.mailer")

ACS_CONNECTION_STRING_ENV = "ACS_CONNECTION_STRING"
ACS_SENDER_EMAIL_ENV = "ACS_SENDER_EMAIL"

_email_client: Optional[EmailClient] = None


def is_email_enabled() -> bool:
    """True si la config ACS est complète (connection string + sender)."""
    return bool(os.getenv(ACS_CONNECTION_STRING_ENV) and os.getenv(ACS_SENDER_EMAIL_ENV))


def get_email_client() -> EmailClient:
    """Construit (lazy) et cache le client ACS. Lève RuntimeError si non configuré."""
    global _email_client
    if _email_client is None:
        conn_str = os.getenv(ACS_CONNECTION_STRING_ENV)
        if not conn_str:
            raise RuntimeError(
                f"{ACS_CONNECTION_STRING_ENV} non défini — impossible d'initialiser ACS Email."
            )
        _email_client = EmailClient.from_connection_string(conn_str)
        logger.info("Client ACS Email initialisé.")
    return _email_client


# ========================== PDF Generation ==========================
def generate_password_reset_pdf(
    avocat_code: str,
    avocat_nom: str,
    avocat_prenom: str,
    motpasse1: str,
    motpasse2: str,
) -> bytes:
    """Génère un PDF contenant les nouveaux mots de passe pour l'avocat."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin_x = 1 * inch
    y = height - 1.2 * inch

    # En-tête
    c.setFont("Helvetica-Bold", 16)
    c.setFillColorRGB(0.0, 0.2, 0.628)  # #0033A0
    c.drawString(margin_x, y, "Commission des services juridiques")
    y -= 0.3 * inch
    c.setFont("Helvetica", 11)
    c.setFillColorRGB(0.3, 0.3, 0.3)
    c.drawString(margin_x, y, "Aide juridique du Québec — GestionCardex")
    y -= 0.6 * inch

    # Titre
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin_x, y, "Réinitialisation de vos mots de passe Web")
    y -= 0.5 * inch

    # Date
    c.setFont("Helvetica", 10)
    c.drawString(margin_x, y, f"Date : {now_local().strftime('%Y-%m-%d %H:%M')}")
    y -= 0.4 * inch

    # Identité
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin_x, y, "Avocat :")
    c.setFont("Helvetica", 11)
    c.drawString(margin_x + 1.2 * inch, y, f"{avocat_nom}, {avocat_prenom}")
    y -= 0.25 * inch
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin_x, y, "Code :")
    c.setFont("Helvetica", 11)
    c.drawString(margin_x + 1.2 * inch, y, avocat_code)
    y -= 0.6 * inch

    # Mots de passe — encadré
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.setFillColorRGB(0.97, 0.97, 0.99)
    c.rect(margin_x, y - 1.3 * inch, width - 2 * margin_x, 1.4 * inch, fill=1, stroke=1)
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_x + 0.2 * inch, y - 0.2 * inch, "Nouveaux mots de passe")
    c.setFont("Courier-Bold", 14)
    c.drawString(margin_x + 0.2 * inch, y - 0.6 * inch, f"Mot de passe 1 : {motpasse1}")
    c.drawString(margin_x + 0.2 * inch, y - 0.95 * inch, f"Mot de passe 2 : {motpasse2}")
    y -= 1.7 * inch

    # Sécurité
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    msg = ("Pour des raisons de sécurité, veuillez conserver ce document en lieu sûr "
           "et ne pas le transférer par courriel. Ces mots de passe sont strictement "
           "personnels et confidentiels.")
    for line in _wrap_text(msg, 95):
        c.drawString(margin_x, y, line)
        y -= 0.18 * inch

    # Pied de page
    c.setFont("Helvetica", 8)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawString(margin_x, 0.7 * inch,
                 "Document généré automatiquement — Commission des services juridiques.")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def _wrap_text(text: str, max_chars: int) -> List[str]:
    """Word-wrap basique pour la note de sécurité du PDF."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= max_chars:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ========================== ACS Attachment helper ==========================
def build_pdf_attachment(pdf_bytes: bytes, filename: str) -> Dict[str, Any]:
    """Construit l'objet attachment ACS (PDF base64)."""
    return {
        "name": filename,
        "contentType": "application/pdf",
        "contentInBase64": base64.b64encode(pdf_bytes).decode("utf-8"),
    }


# ========================== Email send ==========================
def send_email(
    to_email: str,
    subject: str,
    body_html: str,
    body_text: Optional[str] = None,
    attachments: Optional[List[Dict[str, Any]]] = None,
    display_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Envoie un courriel via ACS. Bloque jusqu'à acceptation par le service.

    Lève HttpResponseError ou RuntimeError en cas d'échec.
    """
    sender = os.getenv(ACS_SENDER_EMAIL_ENV)
    if not sender:
        raise RuntimeError(f"{ACS_SENDER_EMAIL_ENV} non défini.")

    client = get_email_client()
    recipient: Dict[str, Any] = {"address": to_email}
    if display_name:
        recipient["displayName"] = display_name

    message: Dict[str, Any] = {
        "senderAddress": sender,
        "content": {
            "subject": subject,
            "plainText": body_text or "Veuillez consulter la version HTML de ce message.",
            "html": body_html,
        },
        "recipients": {"to": [recipient]},
    }
    if attachments:
        message["attachments"] = attachments

    try:
        logger.info("ACS Email — envoi à %s (sujet=%s)", to_email, subject)
        poller = client.begin_send(message)
        result = poller.result()
        logger.info("ACS Email — envoyé, id=%s status=%s",
                    getattr(result, "id", None), getattr(result, "status", None))
        return {"id": getattr(result, "id", None), "status": getattr(result, "status", "Sent")}
    except HttpResponseError as ex:
        logger.error("ACS Email — échec pour %s : %s", to_email, ex)
        raise


# ========================== High-level helper ==========================
def send_password_reset_email(
    to_email: str,
    avocat_code: str,
    avocat_nom: str,
    avocat_prenom: str,
    motpasse1: str,
    motpasse2: str,
) -> Dict[str, Any]:
    """Compose et envoie le courriel de réinit avec PDF en pièce jointe."""
    pdf = generate_password_reset_pdf(avocat_code, avocat_nom, avocat_prenom,
                                      motpasse1, motpasse2)
    attachment = build_pdf_attachment(pdf, f"mots_de_passe_{avocat_code}.pdf")

    full_name = f"{avocat_prenom} {avocat_nom}".strip()
    subject = "Réinitialisation de vos mots de passe — Aide juridique du Québec"

    html = f"""<!DOCTYPE html>
<html lang="fr">
  <body style="font-family: Arial, sans-serif; color:#222; line-height:1.5;">
    <p>Bonjour Me {avocat_nom},</p>
    <p>
      Vos mots de passe Web de l'application <strong>GestionCardex</strong> ont
      été réinitialisés à votre demande.
    </p>
    <p>
      Vous trouverez en pièce jointe (PDF) vos nouveaux identifiants
      (Mot de passe 1 et Mot de passe 2).
    </p>
    <p style="color:#b00; font-weight: bold;">
      Pour des raisons de sécurité, conservez ce document en lieu sûr et ne le
      transférez pas par courriel.
    </p>
    <p>
      Ceci est un message automatique — merci de ne pas y répondre.<br/>
      <em>Commission des services juridiques — Aide juridique du Québec</em>
    </p>
  </body>
</html>"""

    text = (
        f"Bonjour Me {avocat_nom},\n\n"
        "Vos mots de passe Web GestionCardex ont été réinitialisés.\n"
        "Veuillez consulter le PDF joint pour vos nouveaux identifiants.\n\n"
        "Conservez ce document en lieu sûr. Ne le transférez pas par courriel.\n\n"
        "— Commission des services juridiques"
    )

    return send_email(
        to_email=to_email,
        subject=subject,
        body_html=html,
        body_text=text,
        attachments=[attachment],
        display_name=full_name or None,
    )
