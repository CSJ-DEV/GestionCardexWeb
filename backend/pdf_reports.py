"""
Crystal Reports legacy reproduction — fidèle à la mise en forme des rapports
historiques GestionCardex (Registre97, Registre98, ListeDetBar, ListeDetDist,
ListeDetReg, ListeSom).

Choix visuels (basés sur les PDF legacy fournis) :
- Page Letter portrait, marges 1.5 cm latérales / 3.5 cm haut (header) / 2.0 cm bas (footer)
- Police Helvetica (équiv. Arial / Calibri du Crystal d'origine)
- Header répété sur chaque page : pavé "AIDE JURIDIQUE" en haut-gauche +
  titre centré "Commission des services juridiques" + sous-titre spécifique
- Footer répété sur chaque page : "AAAA/MM/JJ | nomrapport.rpt | Page X de Y"
- Aucun gris alterné, aucun GRID Excel-style — tableaux fins type Crystal
"""
from __future__ import annotations

from datetime import datetime
from io import BytesIO
from typing import Iterable

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


# ---------- Districts (référence statique, alignée sur le frontend) ----------
QC_DISTRICTS: dict[int, str] = {
    1: "Montréal", 2: "Québec", 3: "Laval", 4: "Longueuil", 5: "Gatineau",
    6: "Sherbrooke", 7: "Trois-Rivières", 8: "Saguenay", 9: "Lévis",
    10: "Terrebonne", 11: "Saint-Jean-sur-Richelieu", 12: "Repentigny",
    13: "Drummondville", 14: "Saint-Jérôme", 15: "Granby", 16: "Beauharnois",
    17: "Mirabel", 18: "Joliette",
}

GROUP_LABEL = {
    "P": "Avocats Pratique Privée",
    "A": "Avocats Permanents",
    "N": "Notaires",
}


# ---------- Styles communs ----------
def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "period": ParagraphStyle(
            "period", parent=base["Normal"], fontName="Helvetica-Oblique",
            fontSize=10, alignment=TA_CENTER, leading=12, spaceBefore=4, spaceAfter=10,
        ),
        "section": ParagraphStyle(
            "section", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=11, leading=14, spaceBefore=12, spaceAfter=6,
        ),
        "subsection": ParagraphStyle(
            "subsection", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=9.5, spaceBefore=4, spaceAfter=2,
        ),
        "subtotal": ParagraphStyle(
            "subtotal", parent=base["Normal"], fontName="Helvetica-Oblique",
            fontSize=9, alignment=TA_RIGHT, spaceBefore=2, spaceAfter=2,
        ),
        "total": ParagraphStyle(
            "total", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=10, alignment=TA_RIGHT, spaceBefore=4, spaceAfter=10,
        ),
        "n": ParagraphStyle(
            "n", parent=base["Normal"], fontName="Helvetica", fontSize=9, leading=11,
        ),
        "small": ParagraphStyle(
            "small", parent=base["Normal"], fontName="Helvetica", fontSize=7.5, leading=9.5,
        ),
        "block_name": ParagraphStyle(
            "block_name", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=10, leading=12, spaceBefore=6, spaceAfter=2,
        ),
        "block_label": ParagraphStyle(
            "block_label", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=8, leading=10, textColor=colors.HexColor("#444444"),
        ),
    }


# ---------- Header / Footer ----------
def _draw_legacy_chrome(canv, doc, *, footer_filename: str, branded_title: str, branded_subtitle: str):
    """Dessine le bandeau 'AIDE JURIDIQUE' + le titre + le pied de page sur chaque page."""
    canv.saveState()
    page_w, page_h = doc.pagesize

    # --- Pavé brand AIDE JURIDIQUE en haut-gauche (rappel du logo Crystal d'origine) ---
    brand_x = doc.leftMargin
    brand_y = page_h - 1.55 * cm
    brand_w = 3.0 * cm
    brand_h = 1.05 * cm
    canv.setFillColor(colors.HexColor("#0B3D91"))
    canv.rect(brand_x, brand_y, brand_w, brand_h, stroke=0, fill=1)
    # Filet jaune façon plaque officielle
    canv.setStrokeColor(colors.HexColor("#F2C200"))
    canv.setLineWidth(0.8)
    canv.line(brand_x, brand_y - 0.05 * cm, brand_x + brand_w, brand_y - 0.05 * cm)

    canv.setFillColor(colors.white)
    canv.setFont("Helvetica-Bold", 10)
    canv.drawCentredString(brand_x + brand_w / 2, brand_y + brand_h - 0.45 * cm, "AIDE")
    canv.drawCentredString(brand_x + brand_w / 2, brand_y + brand_h - 0.85 * cm, "JURIDIQUE")

    # --- Titre + sous-titre centrés ---
    canv.setFillColor(colors.black)
    canv.setFont("Helvetica-Bold", 13)
    canv.drawCentredString(page_w / 2, page_h - 1.0 * cm, branded_title)

    canv.setFont("Helvetica", 9.5)
    y = page_h - 1.55 * cm
    for line in (branded_subtitle or "").split("\n"):
        if line.strip():
            canv.drawCentredString(page_w / 2, y, line)
        y -= 0.42 * cm

    # --- Footer : date | nom_rapport.rpt | Page X ---
    today = datetime.now().strftime("%Y/%m/%d")
    canv.setFont("Helvetica", 8)
    canv.setFillColor(colors.HexColor("#444444"))
    canv.drawString(doc.leftMargin, 1.1 * cm, today)
    canv.drawCentredString(page_w / 2, 1.1 * cm, footer_filename)
    canv.drawRightString(page_w - doc.rightMargin, 1.1 * cm, f"Page {doc.page}")
    # Filet de séparation discret
    canv.setStrokeColor(colors.HexColor("#888888"))
    canv.setLineWidth(0.3)
    canv.line(doc.leftMargin, 1.45 * cm, page_w - doc.rightMargin, 1.45 * cm)

    canv.restoreState()


def _make_doc(buf: BytesIO, *, footer_filename: str, branded_title: str, branded_subtitle: str,
              top_margin_cm: float = 3.6, landscape_orient: bool = False) -> BaseDocTemplate:
    pagesize = landscape(letter) if landscape_orient else letter

    def _on_page(canv, doc):
        _draw_legacy_chrome(canv, doc, footer_filename=footer_filename,
                            branded_title=branded_title, branded_subtitle=branded_subtitle)

    doc = BaseDocTemplate(
        buf, pagesize=pagesize,
        leftMargin=1.5 * cm, rightMargin=1.5 * cm,
        topMargin=top_margin_cm * cm, bottomMargin=2.0 * cm,
        title=branded_title,
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
                  id="main", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=_on_page)])
    return doc


# ---------- Style commun pour les tableaux Crystal ----------
def _table_style(*, header_row: bool = True) -> TableStyle:
    cmds = [
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    if header_row:
        cmds += [
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("LINEABOVE", (0, 0), (-1, 0), 0.5, colors.black),
            ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
        ]
    return TableStyle(cmds)


# ============================================================================
# REGISTRE 97 — Mandats par article (486.3, 486.7, 672.5, 684)
# ============================================================================
def build_registre97(date_debut: str, date_fin: str, rows_par_article: dict[str, list[dict]]) -> bytes:
    """
    rows_par_article[article] = list of mandate dicts with keys:
      avocat_nom, avocat_type ("P"/"A"/"N"), requerant, date_ordonnance,
      date_emission, numero
    """
    s = _styles()
    buf = BytesIO()
    doc = _make_doc(
        buf,
        footer_filename="registre97.rpt",
        branded_title="Commission des services juridiques",
        branded_subtitle=(
            "Registre tenu en vertu de l'article 97 du Règlement d'application\n"
            "sur l'aide juridique et sur la prestation de certains autres services juridiques\n"
            "L.R.Q. chapitre A-14"
        ),
        top_margin_cm=4.0,
    )

    el: list = [Paragraph(f"pour la période du {date_debut} au {date_fin}", s["period"])]

    headers = ["Nom avocat", "Nom du requérant", "Date ordonnance ou décision", "Date émission", "Mandat"]
    col_w = [4.6 * cm, 4.6 * cm, 3.6 * cm, 2.4 * cm, 2.6 * cm]

    for article in ["486.3", "486.7", "672.5", "684"]:
        rows = rows_par_article.get(article, [])
        el.append(Paragraph(f"Article {article} C.cr.", s["section"]))

        if not rows:
            el.append(Paragraph("<i>Aucun mandat pour la période</i>", s["n"]))
            el.append(Paragraph(f"Total Article {article} C.cr.    0 mandat(s)", s["total"]))
            continue

        by_type: dict[str, list[dict]] = {}
        for r in rows:
            by_type.setdefault(r.get("avocat_type") or "P", []).append(r)

        article_total = 0
        for tcode in ["P", "A", "N"]:
            items = by_type.get(tcode, [])
            if not items:
                continue
            label = GROUP_LABEL[tcode]
            data = [headers] + [
                [
                    r.get("avocat_nom", ""),
                    r.get("requerant", ""),
                    r.get("date_ordonnance", ""),
                    r.get("date_emission", ""),
                    r.get("numero", ""),
                ]
                for r in items
            ]
            tbl = Table(data, colWidths=col_w, repeatRows=1)
            style = _table_style()
            style.add("ALIGN", (2, 0), (-1, -1), "CENTER")
            tbl.setStyle(style)
            el.append(KeepTogether([Paragraph(label, s["subsection"]), tbl]))
            el.append(Paragraph(f"Sous-total {label}    {len(items)} mandat(s)", s["subtotal"]))
            article_total += len(items)

        el.append(Paragraph(f"Total Article {article} C.cr.    {article_total} mandat(s)", s["total"]))

    doc.build(el)
    return buf.getvalue()


# ============================================================================
# REGISTRE 98 — Mandats par article (long listing détaillé)
# ============================================================================
def build_registre98(date_debut: str, date_fin: str, rows_par_article: dict[str, list[dict]]) -> bytes:
    """
    rows_par_article[article] = list with keys :
      avocat_code, avocat_nom, numero, ordonnance, date_ordonnance, date_emission, date_fermeture
    """
    s = _styles()
    buf = BytesIO()
    doc = _make_doc(
        buf,
        footer_filename="registre98.rpt",
        branded_title="Commission des services juridiques",
        branded_subtitle=(
            "Registre tenu en vertu de l'article 98 du Règlement d'application\n"
            "sur l'aide juridique et sur la prestation de certains autres services juridiques\n"
            "L.R.Q. chapitre A-14"
        ),
        top_margin_cm=4.0,
    )

    el: list = [Paragraph(f"pour la période du {date_debut} au {date_fin}", s["period"])]
    headers = ["Avocat", "Mandat", "Ordonnance ou décision",
               "Date ordonnance ou décision", "Date d'émission", "Date de fermeture"]
    col_w = [4.0 * cm, 3.4 * cm, 3.0 * cm, 2.6 * cm, 2.2 * cm, 2.2 * cm]

    if not rows_par_article:
        el.append(Paragraph("<i>Aucun mandat pour la période</i>", s["n"]))
    else:
        # Tri explicite pour reproductibilité entre exécutions
        ARTICLES_ORDER = ["486.3", "486.7", "672.5", "684"]
        ordered = [(a, rows_par_article[a]) for a in ARTICLES_ORDER if a in rows_par_article]
        ordered += [(a, items) for a, items in rows_par_article.items() if a not in ARTICLES_ORDER]
        for article, items in ordered:
            el.append(Paragraph(f"Article {article} C.cr.", s["section"]))
            data = [headers] + [
                [
                    f"{r.get('avocat_code','')} {r.get('avocat_nom','')}".strip(),
                    r.get("numero", ""),
                    r.get("ordonnance", "") or article,
                    r.get("date_ordonnance", ""),
                    r.get("date_emission", ""),
                    r.get("date_fermeture", ""),
                ]
                for r in items
            ]
            tbl = Table(data, colWidths=col_w, repeatRows=1)
            style = _table_style()
            style.add("ALIGN", (2, 0), (-1, -1), "CENTER")
            tbl.setStyle(style)
            el.append(tbl)

    doc.build(el)
    return buf.getvalue()


# ============================================================================
# Listes détaillées (Bar / District / Région) — bloc par avocat
# ============================================================================
_LISTE_SUBTITLE = (
    "Avocats inscrits à la liste dressée en vertu de l'article 83.10\n"
    "de la Loi sur l'aide juridique et sur la prestation de certains autres services juridiques\n"
    "L.R.Q. chapitre A-14"
)


def _avocat_block(avo: dict, styles: dict) -> Table:
    """Bloc compact pour un avocat (4 lignes type fiche Crystal)."""
    nom = f"{avo.get('code','')}  —  {avo.get('nom','')}, {avo.get('prenom','')}"
    adr = avo.get("adresse") or {}
    adresse_full = " ".join(filter(None, [adr.get("address", ""),
                                          adr.get("ville", ""),
                                          adr.get("province", ""),
                                          adr.get("codepostal", "")]))
    tels = " ".join(filter(None, [adr.get("telephone", ""), adr.get("telephone2", "")]))
    email = adr.get("email", "") or ""
    sectbar = avo.get("sectbar") or "—"
    annee = str(avo.get("annee_barreau", "") or "—")
    mega = avo.get("_mega") or {}
    exp = mega.get("experience", 0) or "—"
    langs = []
    if mega.get("francais"):
        langs.append("français")
    if mega.get("anglais"):
        langs.append("anglais")
    if mega.get("autres"):
        langs.append(str(mega["autres"]))
    langs_txt = ", ".join(langs) if langs else "—"
    districts_ids = mega.get("districts") or []
    if mega.get("tous_districts"):
        districts_txt = "Tous les districts"
    elif districts_ids:
        districts_txt = ", ".join(QC_DISTRICTS.get(i, str(i)) for i in districts_ids)
    else:
        districts_txt = "—"

    L = lambda t: Paragraph(t, styles["block_label"])  # noqa: E731
    V = lambda t: Paragraph(t or "—", styles["n"])     # noqa: E731

    body = [
        [Paragraph(nom, styles["block_name"]), "", "", ""],
        [L("Adresse"), V(adresse_full), L("Année barreau"), V(annee)],
        [L("Téléphones"), V(tels), L("Expérience"), V(f"{exp} an(s)")],
        [L("Adresse courriel"), V(email), L("Section(s) du barreau"), V(sectbar)],
        [L("Langue(s) parlée(s)"), V(langs_txt), L("Districts"), V(districts_txt)],
    ]
    tbl = Table(body, colWidths=[3.3 * cm, 6.4 * cm, 3.3 * cm, 4.7 * cm])
    tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("SPAN", (0, 0), (3, 0)),
        ("LINEBELOW", (0, 0), (-1, 0), 0.4, colors.HexColor("#999999")),
        ("LINEBELOW", (0, -1), (-1, -1), 0.25, colors.HexColor("#CCCCCC")),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 6),
    ]))
    return tbl


def _build_detail_list(*, footer_filename: str, period_line: str | None,
                        groups: dict[str, list[dict]], group_label_format: str) -> bytes:
    s = _styles()
    buf = BytesIO()
    doc = _make_doc(
        buf,
        footer_filename=footer_filename,
        branded_title="Commission des services juridiques",
        branded_subtitle=_LISTE_SUBTITLE,
        top_margin_cm=3.8,
    )
    el: list = []
    if period_line:
        el.append(Paragraph(period_line, s["period"]))

    if not groups:
        el.append(Paragraph("<i>Aucun avocat actif.</i>", s["n"]))
    else:
        for grp, avos in groups.items():
            el.append(Paragraph(group_label_format.format(grp=grp, n=len(avos)), s["section"]))
            for avo in avos:
                el.append(_avocat_block(avo, s))
                el.append(Spacer(1, 0.15 * cm))

    doc.build(el)
    return buf.getvalue()


def build_liste_det_bar(groups: dict[str, list[dict]]) -> bytes:
    """Liste détaillée par section barreau (groupé par sectbar)."""
    return _build_detail_list(
        footer_filename="ListeDetBar.rpt",
        period_line="par section du barreau",
        groups=groups,
        group_label_format="Section : {grp}    ({n} avocat(s))",
    )


def build_liste_det_dist(groups: dict[str, list[dict]]) -> bytes:
    """Liste détaillée par district (groupé par ville/district)."""
    return _build_detail_list(
        footer_filename="ListeDetDist.rpt",
        period_line="par district",
        groups=groups,
        group_label_format="District : {grp}    ({n} avocat(s))",
    )


def build_liste_det_reg(groups: dict[str, list[dict]]) -> bytes:
    """Liste détaillée par région (regroupement actif/inactif faute de table région)."""
    return _build_detail_list(
        footer_filename="ListeDetReg.rpt",
        period_line="par registre",
        groups=groups,
        group_label_format="{grp}    ({n} avocat(s))",
    )


def build_liste_som(date_debut: str, date_fin: str, avocats: list[dict]) -> bytes:
    """Liste sommaire — un tableau alphabétique de tous les avocats."""
    s = _styles()
    buf = BytesIO()
    doc = _make_doc(
        buf,
        footer_filename="ListeSom.rpt",
        branded_title="Commission des services juridiques",
        branded_subtitle=_LISTE_SUBTITLE,
        top_margin_cm=3.8,
    )
    el: list = [Paragraph(
        f"pour la période du {date_debut} au {date_fin} — par ordre alphabétique",
        s["period"],
    )]

    headers = ["Code", "Nom, Prénom", "Adresse", "Téléphones",
               "Adresse courriel", "Année barreau", "Section(s) du barreau"]
    col_w = [1.6 * cm, 3.6 * cm, 4.0 * cm, 2.8 * cm, 3.4 * cm, 1.4 * cm, 2.4 * cm]

    if not avocats:
        el.append(Paragraph("<i>Aucun avocat actif.</i>", s["n"]))
    else:
        rows = [headers]
        for a in avocats:
            adr = a.get("adresse") or {}
            tels = " / ".join(filter(None, [adr.get("telephone", ""), adr.get("telephone2", "")]))
            ville = adr.get("ville") or ""
            address = adr.get("address") or ""
            adr_line = ", ".join(filter(None, [address, ville]))
            rows.append([
                a.get("code", ""),
                f"{a.get('nom','')}, {a.get('prenom','')}",
                adr_line or "—",
                tels or "—",
                adr.get("email") or "—",
                str(a.get("annee_barreau", "") or "—"),
                a.get("sectbar") or "—",
            ])
        tbl = Table(rows, colWidths=col_w, repeatRows=1)
        style = _table_style()
        style.add("ALIGN", (5, 1), (5, -1), "CENTER")
        style.add("FONTSIZE", (0, 0), (-1, -1), 8)
        tbl.setStyle(style)
        el.append(tbl)

    doc.build(el)
    return buf.getvalue()
