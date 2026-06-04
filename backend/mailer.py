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
from datetime import datetime

from azure.communication.email import EmailClient
from azure.core.exceptions import HttpResponseError
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, KeepTogether,
)
from reportlab.lib.colors import HexColor
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


# ========================== Lettre officielle CSJ ==========================
_MOIS_FR = ["", "janvier", "février", "mars", "avril", "mai", "juin",
            "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "logo-ajq.jpg")
GUIDE_URL = "https://www.csj.qc.ca/facturation-mandats-aj/aide.aspx?lang=fr"


def _format_date_fr(dt: datetime) -> str:
    """Retourne 'Le 14 juillet 2025' à partir d'un datetime."""
    return f"Le {dt.day} {_MOIS_FR[dt.month]} {dt.year}"


def _build_address_lines(adresse: Optional[Any]) -> List[str]:
    """Construit les lignes d'adresse à partir d'un objet Adresse legacy.
    Retourne 1-4 lignes selon ce qui est renseigné. L'objet peut être None."""
    if adresse is None:
        return []
    lines: List[str] = []
    # Ligne(s) 1-3 : adresse + adresse2 + adresse3 (multi-lignes legacy)
    for attr in ("address", "adresse", "adresse2", "adresse3"):
        val = getattr(adresse, attr, None)
        if val and str(val).strip():
            lines.append(str(val).strip())
    # Ligne finale : ville, province codepostal
    last_parts = []
    ville = getattr(adresse, "ville", None)
    prov = getattr(adresse, "province", None)
    cp = getattr(adresse, "codepostal", None)
    if ville and str(ville).strip():
        if prov and str(prov).strip():
            last_parts.append(f"{str(ville).strip()}, {str(prov).strip()}")
        else:
            last_parts.append(str(ville).strip())
    if cp and str(cp).strip():
        last_parts.append(str(cp).strip())
    if last_parts:
        lines.append("  ".join(last_parts))
    return lines


def generate_letter_pdf(
    avocat_code: str,
    avocat_nom: str,
    avocat_prenom: str,
    motpasse1: str,
    motpasse2: str,
    adresse: Optional[Any] = None,
    config: Optional[Any] = None,
) -> bytes:
    """Génère la lettre officielle CSJ (Code d'utilisateur et mots de passe).

    Reproduit fidèlement le modèle Visual Basic / Word historique :
      - En-tête avec logo CSJ + mention CONFIDENTIEL
      - Date du jour en français long
      - Adresse destinataire
      - Objet
      - Corps de la lettre (texte officiel)
      - Formule de politesse
      - Signature (image si configurée) + nom/titre/affiliation
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        leftMargin=0.85 * inch, rightMargin=0.85 * inch,
        topMargin=0.4 * inch, bottomMargin=0.4 * inch,
    )
    styles = getSampleStyleSheet()
    body_style = ParagraphStyle(
        "body", parent=styles["Normal"],
        fontName="Helvetica", fontSize=10, leading=12.5, alignment=TA_JUSTIFY,
        spaceAfter=4,
    )
    body_left = ParagraphStyle(
        "body_left", parent=body_style, alignment=TA_LEFT, spaceAfter=2,
    )
    signature_style = ParagraphStyle(
        "sig", parent=body_left, fontSize=10, leading=12, spaceAfter=0,
    )

    story = []

    # ---- En-tête : logo (gauche) + CONFIDENTIEL (droite) ----
    if os.path.exists(LOGO_PATH):
        try:
            img = RLImage(LOGO_PATH, width=1.5 * inch, height=0.65 * inch, kind="proportional")
            img.hAlign = "LEFT"
            story.append(img)
        except Exception:
            pass

    confidential = ParagraphStyle(
        "conf", parent=styles["Normal"], fontName="Helvetica-Bold",
        fontSize=10, alignment=2, textColor=HexColor("#666666"),  # 2 = TA_RIGHT
    )
    story.append(Paragraph("CONFIDENTIEL", confidential))
    story.append(Spacer(1, 0.1 * inch))

    # ---- Date ----
    story.append(Paragraph(_format_date_fr(now_local()), body_left))
    story.append(Spacer(1, 0.12 * inch))

    # ---- Destinataire ----
    full_name = f"Me {avocat_prenom} {avocat_nom}".strip()
    story.append(Paragraph(full_name, body_left))
    for line in _build_address_lines(adresse):
        story.append(Paragraph(line, body_left))
    story.append(Spacer(1, 0.14 * inch))

    # ---- Objet ----
    story.append(Paragraph(
        "<b>Objet : Code d'utilisateur et mots de passe</b>", body_left,
    ))
    story.append(Spacer(1, 0.12 * inch))

    # ---- Salutation ----
    story.append(Paragraph("Maître,", body_left))
    story.append(Spacer(1, 0.04 * inch))

    # ---- Corps ----
    story.append(Paragraph(
        "Votre demande d'inscription à la facturation des mandats d'aide "
        "juridique en ligne de la Commission des services juridiques a été "
        "acceptée.", body_style,
    ))

    # Bloc identifiants — chaque ligne en gras simple
    creds_block = (
        f"<b>Code d'utilisateur :</b> {avocat_code}<br/>"
        f"<b>Mot de passe 1 :</b> {motpasse1 or '—'}<br/>"
        f"<b>Mot de passe 2 :</b> {motpasse2 or '—'}"
    )
    story.append(Paragraph(creds_block, body_left))
    story.append(Spacer(1, 0.08 * inch))

    story.append(Paragraph(
        "Le mot de passe 1 donne un accès limité vous permettant seulement de "
        "traiter des données de facturation, aucun accès aux relevés et au "
        "formulaire d'adhésion au dépôt direct;", body_style,
    ))
    story.append(Paragraph(
        "Le mot de passe 2 vous donne un accès illimité vous permettant "
        "d'accéder à votre relevé de compte, au relevé 27, au formulaire "
        "d'adhésion au dépôt direct et à la facturation en ligne. Il est de "
        "votre responsabilité de conserver la confidentialité de ce mot de "
        "passe.", body_style,
    ))
    story.append(Paragraph(
        "Lors de votre première connexion, vous devrez confirmer avoir lu la "
        "Convention de l'utilisateur en cochant la case concernée et en "
        "cliquant sur 'Confirmer'. Vous serez ensuite dirigé vers 'Votre "
        "profil' afin d'y compléter les informations nécessaires à la "
        "sécurité de votre compte (NAS, question secrète et autres). Prévoyez "
        "quelques jours ouvrables pour la mise à jour de votre profil de "
        "facturation dans la base de données.", body_style,
    ))
    story.append(Paragraph(
        "Les paiements des relevés d'honoraires et de débours se font par "
        "dépôt direct. Une fois 'Votre profil' mis à jour, vous pourrez "
        "accéder au formulaire d'inscription au dépôt direct.", body_style,
    ))
    story.append(Paragraph(
        "Pour obtenir davantage d'informations concernant le fonctionnement "
        "de la facturation des mandats d'aide juridique, vous pouvez "
        "rejoindre le soutien technique au 514 873-3562 p.245, consulter "
        "l'Aide en ligne sur notre site Web ou cliquer sur le lien suivant :",
        body_style,
    ))

    # Lien hypertexte vers le guide
    link_style = ParagraphStyle(
        "link", parent=body_left, textColor=HexColor("#0033A0"),
    )
    story.append(Paragraph(
        f'<link href="{GUIDE_URL}"><u>Guide d\'utilisation</u></link>',
        link_style,
    ))
    story.append(Spacer(1, 0.06 * inch))

    # ---- Formule de politesse ----
    story.append(Paragraph(
        "Nous vous prions de recevoir, Maître, l'expression de nos sentiments "
        "distingués.", body_style,
    ))
    story.append(Spacer(1, 0.08 * inch))

    # ---- Signature (image si présente) ----
    sig_nom = getattr(config, "signataire_nom", "") or "M. Yves Boisvert, CPA, CGA"
    sig_titre = getattr(config, "signataire_titre", "") or "Directeur des services financiers"
    sig_aff = getattr(config, "signataire_affiliation", "") or "Commission des services juridiques"

    sig_b64 = getattr(config, "signature_image_base64", None)
    if sig_b64:
        try:
            sig_bytes = base64.b64decode(sig_b64)
            sig_img = RLImage(BytesIO(sig_bytes), width=1.4 * inch, height=0.45 * inch,
                              kind="proportional")
            sig_img.hAlign = "LEFT"
            story.append(sig_img)
        except Exception as e:
            logger.warning("Impossible d'inclure la signature image : %s", e)
            story.append(Spacer(1, 0.25 * inch))
    else:
        story.append(Spacer(1, 0.25 * inch))

    story.append(Paragraph(sig_nom, signature_style))
    story.append(Paragraph(sig_titre, signature_style))
    story.append(Paragraph(sig_aff, signature_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


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
