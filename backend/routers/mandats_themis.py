"""Routes pour le module Mandats (TI uniquement).

Source de vérité : base Themis (sur le même serveur que CardAvo/Art52).
Vérification de présence Web : base Fvi (sur le serveur séparé CSJ-WEB01).

Tables Themis utilisées :
  - atattest      : SELECT (mandats AJ standards)
  - megaattest    : SELECT (mandats Méga)
  - atattdaj      : SELECT (vérif existence noref AJ)
  - megaattdaj    : SELECT (vérif existence noref Méga)
  - atattest      : UPDATE (pseudo-update pour armer le trigger lors de Réinit)

Tables Fvi utilisées :
  - Mandats       : SELECT batch pour calcul des badges Web

Port fidèle du formulaire VB.NET frmMandat avec corrections :
  - Requêtes paramétrées (anti-injection SQL)
  - UNION ALL côté SQL (fixe le bug DataSource écrasé du VB)
  - TOP 500 pour limiter le volume
  - Badge Web hybride (un seul roundtrip réseau)
"""
from __future__ import annotations

import logging
import re
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db, get_secondary_engine
from security import require_role

logger = logging.getLogger("gestioncardex.mandats")
router = APIRouter(prefix="/mandats", tags=["mandats"])

# ============================================================
#                           Schémas
# ============================================================
MANDAT_REGEX = re.compile(r"^(\d{2})-(\d{2})-(\d{8})-(\d{2})$")


class MandatSearchIn(BaseModel):
    mandat: Optional[str] = Field(None, description="Format RR-BB-NNNNNNNN-NN")
    code_avocat: Optional[str] = None
    nom_client: Optional[str] = None


class MandatRow(BaseModel):
    source: str  # "atattest" ou "megaattest"
    noreg: str
    nobur: str
    noref: str
    code_avocat: str = ""
    nom_avocat: str = ""
    date_emis: Optional[str] = None
    date_retro: Optional[str] = None
    conditionnel: str = "N"  # 'O' ou 'N'
    nom_requerant: str = ""
    prenom_requerant: str = ""
    # Sera rempli côté serveur si Fvi est configuré
    sur_web: Optional[bool] = None
    # True si noref absent de atattdaj/megaattdaj (alerte du VB)
    daj_manquant: bool = False


class MandatSearchOut(BaseModel):
    items: List[MandatRow]
    total: int
    limited: bool  # True si on a hit le TOP 500
    fvi_checked: bool


class ReinitIn(BaseModel):
    noreg: str
    nobur: str
    noref: str
    confirmation_code: str  # doit matcher "noreg-nobur-noref" pour double confirmation


# ============================================================
#                       Recherche mandats
# ============================================================
@router.post("/search", response_model=MandatSearchOut)
def search_mandats(
    payload: MandatSearchIn,
    user: dict = Depends(require_role("ti")),
    db: Session = Depends(get_db),
):
    """Recherche unifiée des mandats Themis (atattest + megaattest via UNION ALL).

    4 modes (équivalents au VB) :
      - mandat: filtre noreg + nobur + noref (LIKE pour noref partiel)
      - avoreq: code avocat + nom client (LIKE)
      - avo:    code avocat seul
      - req:    nom client seul (LIKE)

    Si Fvi est configurée, ajoute le badge sur_web pour chaque ligne (1 seule
    requête batch vers CSJ-WEB01).
    """
    mandat = (payload.mandat or "").strip()
    code_avo = (payload.code_avocat or "").strip()
    nom = (payload.nom_client or "").strip()

    # Validation : au moins un critère
    if not mandat and not code_avo and not nom:
        raise HTTPException(
            status_code=400,
            detail="Vous n'avez rien inscrit dans les cases Mandat, code avocat ou nom client !",
        )

    # Décodage du champ Mandat (parsing positionnel fidèle au VB)
    noreg = nobur = noref_filter = ""
    if mandat:
        m = MANDAT_REGEX.match(mandat)
        if not m:
            raise HTTPException(
                status_code=400,
                detail="Format du mandat invalide. Attendu : RR-BB-NNNNNNNN-NN (ex : 02-15-12345678-99).",
            )
        noreg = m.group(1)
        nobur = m.group(2)
        # IMPORTANT : le VB utilise Mid(noref, 1, 8) pour la recherche dans atattest,
        # c'est-à-dire UNIQUEMENT les 8 chiffres avant le dernier tiret (les 2 derniers
        # chiffres "NN" sont une sous-référence absente de atattest.noref).
        noref_filter = m.group(3)  # Les 8 chiffres "NNNNNNNN"

    # Construction WHERE paramétré pour chaque table (atattest et megaattest).
    # On utilise LIKE partout + RTRIM pour gérer le cas où les colonnes sont
    # CHAR(n) padded par des espaces dans Themis (cas legacy VB).
    where_parts = []
    params = {}

    if mandat:
        where_parts.append(
            "RTRIM(LTRIM(noreg)) = :noreg "
            "AND RTRIM(LTRIM(nobur)) = :nobur "
            "AND (RTRIM(LTRIM(noref)) LIKE :noref_with_dash "
            "     OR RTRIM(LTRIM(noref)) LIKE :noref_no_dash)"
        )
        params["noreg"] = noreg
        params["nobur"] = nobur
        # On essaie les deux formats : avec tiret central (NNNNNNNN-NN)
        # et sans tiret (NNNNNNNNNN) selon comment Themis stocke
        params["noref_with_dash"] = f"%{noref_filter}%"
        params["noref_no_dash"] = f"%{noref_filter.replace('-', '')}%"
    elif code_avo and nom:
        where_parts.append(
            "RTRIM(LTRIM(adatcodeavomand)) = :code_avo "
            "AND adatreqnom LIKE :nom"
        )
        params["code_avo"] = code_avo
        params["nom"] = f"%{nom}%"
    elif code_avo:
        where_parts.append("RTRIM(LTRIM(adatcodeavomand)) = :code_avo")
        params["code_avo"] = code_avo
    else:  # nom seul
        where_parts.append("adatreqnom LIKE :nom")
        params["nom"] = f"%{nom}%"

    where_clause = where_parts[0]

    # UNION ALL des 2 tables (corrige le bug du VB où DataSource était écrasé).
    # On limite à 500 lignes globalement pour éviter les freezes UI.
    # TOP est SQL Server, LIMIT est SQLite/MySQL — on adapte selon le dialect.
    themis = get_secondary_engine("Themis")
    is_sqlserver = themis.dialect.name in ("mssql", "pyodbc", "pymssql")
    top_clause = "TOP 500" if is_sqlserver else ""
    limit_clause = "" if is_sqlserver else "LIMIT 500"

    sql = text(f"""
        SELECT {top_clause} * FROM (
            SELECT
                'atattest' AS source,
                noreg, nobur, noref,
                adatcodeavomand AS code_avocat,
                adatavonommand AS nom_avocat,
                adatdateemis AS date_emis,
                adatdateacceptdeb AS date_retro,
                CASE adatregcond WHEN 0 THEN 'O' ELSE 'N' END AS conditionnel,
                adatreqnom AS nom_requerant,
                adatreqprenom AS prenom_requerant
            FROM atattest
            WHERE {where_clause}
            UNION ALL
            SELECT
                'megaattest' AS source,
                noreg, nobur, noref,
                adatcodeavomand AS code_avocat,
                COALESCE(adatavoprenommand, '') + ' ' + COALESCE(adatavonommand, '') AS nom_avocat,
                adatdateemis AS date_emis,
                adatdateacceptdeb AS date_retro,
                'N' AS conditionnel,
                adatreqnom AS nom_requerant,
                adatreqprenom AS prenom_requerant
            FROM megaattest
            WHERE {where_clause}
        ) AS u
        ORDER BY u.nom_requerant, u.prenom_requerant
        {limit_clause}
    """)

    # Exécution sur Themis
    rows: List[MandatRow] = []
    try:
        with themis.connect() as conn:
            result = conn.execute(sql, params)
            for r in result.mappings():
                rows.append(MandatRow(
                    source=r["source"],
                    noreg=(r["noreg"] or "").strip(),
                    nobur=(r["nobur"] or "").strip(),
                    noref=(r["noref"] or "").strip(),
                    code_avocat=(r["code_avocat"] or "").strip(),
                    nom_avocat=(r["nom_avocat"] or "").strip(),
                    date_emis=r["date_emis"].isoformat() if r["date_emis"] else None,
                    date_retro=r["date_retro"].isoformat() if r["date_retro"] else None,
                    conditionnel=r["conditionnel"] or "N",
                    nom_requerant=(r["nom_requerant"] or "").strip(),
                    prenom_requerant=(r["prenom_requerant"] or "").strip(),
                ))
    except Exception as e:
        # En dev (SQLite vide), les tables n'existent pas → on retourne 0 résultat
        # sans planter, avec un message diagnostic dans les logs.
        msg = str(e).lower()
        if "no such table" in msg or "objet introuvable" in msg or "invalid object name" in msg:
            logger.warning("Tables Themis (atattest/megaattest) absentes — retour vide.")
            return MandatSearchOut(items=[], total=0, limited=False, fvi_checked=False)
        raise

    # Vérification existence des noref dans atattdaj/megaattdaj (alerte VB)
    if mandat and rows:
        for row in rows:
            row.daj_manquant = not _verif_atattdaj(themis, row)

    # Badges Web : un seul appel batch vers Fvi
    fvi_checked = False
    try:
        _enrich_with_fvi_status(rows)
        fvi_checked = True
    except Exception as e:
        logger.warning("Fvi check skipped : %s", e)
        fvi_checked = False

    return MandatSearchOut(
        items=rows,
        total=len(rows),
        limited=len(rows) >= 500,
        fvi_checked=fvi_checked,
    )


def _verif_atattdaj(themis_engine, row: MandatRow) -> bool:
    """Vérifie qu'une référence existe dans atattdaj (ou megaattdaj) selon la source."""
    table = "megaattdaj" if row.source == "megaattest" else "atattdaj"
    sql = text(f"""
        SELECT TOP 1 1 FROM {table}
        WHERE noreg = :noreg AND nobur = :nobur AND noref = :noref
    """)
    try:
        with themis_engine.connect() as conn:
            result = conn.execute(sql, {
                "noreg": row.noreg, "nobur": row.nobur, "noref": row.noref,
            }).first()
            return result is not None
    except Exception as e:
        logger.warning("VerifAtattdaj err sur %s/%s/%s : %s", row.noreg, row.nobur, row.noref, e)
        return True  # En cas d'erreur, on ne marque pas comme manquant


def _enrich_with_fvi_status(rows: List[MandatRow]) -> None:
    """Renseigne `sur_web` pour chaque ligne via 1 seule requête vers Fvi."""
    if not rows:
        return
    try:
        fvi = get_secondary_engine("Fvi")
    except Exception as e:
        raise RuntimeError(f"Fvi non disponible : {e}")

    # Construit une clause IN dynamique avec paramètres nommés
    conditions = []
    params = {}
    for i, r in enumerate(rows):
        conditions.append(
            f"(cnoreg = :nor{i} AND cnobur = :nob{i} AND cnoref = :ref{i})"
        )
        params[f"nor{i}"] = r.noreg
        params[f"nob{i}"] = r.nobur
        params[f"ref{i}"] = r.noref

    sql = text(f"""
        SELECT cnoreg, cnobur, cnoref FROM Mandats
        WHERE {' OR '.join(conditions)}
    """)

    found = set()
    with fvi.connect() as conn:
        for fr in conn.execute(sql, params):
            found.add((str(fr[0]).strip(), str(fr[1]).strip(), str(fr[2]).strip()))

    for row in rows:
        row.sur_web = (row.noreg, row.nobur, row.noref) in found


# ============================================================
#                       Réinitialisation
# ============================================================
@router.post("/reinit")
def reinit_mandat(
    payload: ReinitIn,
    user: dict = Depends(require_role("ti")),
    _: Session = Depends(get_db),
):
    """Réinitialise un mandat (UPDATE atattest avec noregbur = noregbur).

    Cette pseudo-update arme un trigger SQL Server qui relance la synchronisation
    Themis → CardAvo. Source : VB `subReinitMandat`.

    Sécurité :
      - TI uniquement
      - Double confirmation : `confirmation_code` doit matcher exactement
        "noreg-nobur-noref" (l'utilisateur retape le code complet)
    """
    expected = f"{payload.noreg}-{payload.nobur}-{payload.noref}"
    if payload.confirmation_code.strip() != expected:
        raise HTTPException(
            status_code=400,
            detail=f"Code de confirmation incorrect. Attendu : {expected}",
        )

    sql = text("""
        UPDATE atattest
        SET noregbur = noregbur
        WHERE noreg = :noreg AND nobur = :nobur AND noref = :noref
    """)

    themis = get_secondary_engine("Themis")
    with themis.begin() as conn:
        result = conn.execute(sql, {
            "noreg": payload.noreg,
            "nobur": payload.nobur,
            "noref": payload.noref,
        })
        rows_affected = result.rowcount

    if rows_affected == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Mandat {expected} introuvable dans atattest",
        )

    logger.info("Mandat %s réinitialisé par %s", expected, user.get("email", ""))
    return {
        "ok": True,
        "mandat": expected,
        "message": (
            f"Mandat {expected} réinitialisé, n'oubliez pas de lancer "
            "l'importation afin de vider le trigger !"
        ),
    }
