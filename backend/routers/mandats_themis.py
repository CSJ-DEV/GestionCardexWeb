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
  - Requêtes SÉPARÉES par table (atattest et megaattest) pour résilience :
    si une table échoue (colonnes manquantes, droits...), l'autre fonctionne quand même.
  - TOP 500 pour limiter le volume
  - Badge Web hybride (un seul roundtrip réseau)
  - Erreurs SQL réelles exposées dans la réponse pour debug TI.
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
    # Diagnostics : erreurs SQL par table (visible TI uniquement)
    errors: dict = Field(default_factory=dict)


class ReinitIn(BaseModel):
    noreg: str
    nobur: str
    noref: str
    confirmation_code: str  # doit matcher "noreg-nobur-noref" pour double confirmation


class ReinitBatchItem(BaseModel):
    source: str  # "atattest" ou "megaattest"
    noreg: str
    nobur: str
    noref: str


class ReinitBatchIn(BaseModel):
    items: List[ReinitBatchItem]
    confirmed: bool = False  # case à cocher "Je confirme la réinitialisation"


class ReinitBatchResultItem(BaseModel):
    mandat: str
    source: str
    ok: bool
    error: Optional[str] = None


class ReinitBatchOut(BaseModel):
    results: List[ReinitBatchResultItem]
    success_count: int
    error_count: int


# ============================================================
#                       Recherche mandats
# ============================================================
def _build_where_and_params(
    mandat: str, code_avo: str, nom: str, table_alias: str = ""
) -> tuple[str, dict]:
    """Construit la clause WHERE et les paramètres selon le mode de recherche.

    Identique pour atattest et megaattest (mêmes noms de colonnes utilisés).

    IMPORTANT pour noref :
    Le VB.NET utilise Mid(noref, 1, 8) pour générer la condition LIKE — autrement
    dit il prend les 8 chiffres "NNNNNNNN" (la partie avant le 2e tiret du format
    saisi RR-BB-NNNNNNNN-NN) et fait `noref LIKE '%NNNNNNNN%'`.

    Les colonnes noref sont CHAR(11) et stockent typiquement "72500038-01"
    (8 chiffres + tiret + 2 chiffres). Donc LIKE %72500038% matche bien.
    """
    where_parts = []
    params: dict = {}

    if mandat:
        m = MANDAT_REGEX.match(mandat)
        if not m:
            raise HTTPException(
                status_code=400,
                detail="Format du mandat invalide. Attendu : RR-BB-NNNNNNNN-NN (ex : 02-15-12345678-99).",
            )
        noreg = m.group(1)
        nobur = m.group(2)
        noref_8 = m.group(3)   # 8 chiffres
        noref_2 = m.group(4)   # 2 chiffres derniers (suffixe)
        # RTRIM/LTRIM pour gérer le padding éventuel des CHAR(n)
        where_parts.append(
            "RTRIM(LTRIM(noreg)) = :noreg "
            "AND RTRIM(LTRIM(nobur)) = :nobur "
            "AND ("
            "  RTRIM(LTRIM(noref)) LIKE :noref_p1 "    # %72500038%
            "  OR RTRIM(LTRIM(noref)) LIKE :noref_p2 " # 72500038-01
            "  OR RTRIM(LTRIM(noref)) LIKE :noref_p3 " # 7250003801 (sans tiret)
            ")"
        )
        params["noreg"] = noreg
        params["nobur"] = nobur
        params["noref_p1"] = f"%{noref_8}%"
        params["noref_p2"] = f"{noref_8}-{noref_2}"
        params["noref_p3"] = f"{noref_8}{noref_2}"
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

    return where_parts[0], params


def _query_one_table(
    themis_engine, table: str, is_megaattest: bool,
    where_clause: str, params: dict,
) -> tuple[list[MandatRow], Optional[str]]:
    """Exécute la requête sur UNE seule table et retourne (rows, error_message).

    Si la table n'existe pas ou échoue, retourne ([], "<message>").
    """
    is_sqlserver = themis_engine.dialect.name in ("mssql", "pyodbc", "pymssql")
    top_clause = "TOP 500" if is_sqlserver else ""
    limit_clause = "" if is_sqlserver else "LIMIT 500"

    # megaattest concatène prénom + nom pour le champ nom_avocat (legacy VB).
    # SQL Server utilise '+' pour concat ; SQLite/MySQL utilise '||'.
    if is_megaattest:
        if is_sqlserver:
            nom_avo_expr = (
                "COALESCE(adatavoprenommand, '') + ' ' + COALESCE(adatavonommand, '')"
            )
        else:
            nom_avo_expr = (
                "COALESCE(adatavoprenommand, '') || ' ' || COALESCE(adatavonommand, '')"
            )
        cond_expr = "'N'"  # megaattest n'a pas adatregcond
    else:
        nom_avo_expr = "adatavonommand"
        cond_expr = "CASE adatregcond WHEN 0 THEN 'O' ELSE 'N' END"

    sql = text(f"""
        SELECT {top_clause}
            noreg, nobur, noref,
            adatcodeavomand AS code_avocat,
            {nom_avo_expr} AS nom_avocat,
            adatdateemis AS date_emis,
            adatdateacceptdeb AS date_retro,
            {cond_expr} AS conditionnel,
            adatreqnom AS nom_requerant,
            adatreqprenom AS prenom_requerant
        FROM {table}
        WHERE {where_clause}
        ORDER BY adatreqnom, adatreqprenom
        {limit_clause}
    """)

    rows: list[MandatRow] = []
    try:
        with themis_engine.connect() as conn:
            result = conn.execute(sql, params)
            for r in result.mappings():
                rows.append(MandatRow(
                    source=table,
                    noreg=(r["noreg"] or "").strip() if r["noreg"] else "",
                    nobur=(r["nobur"] or "").strip() if r["nobur"] else "",
                    noref=(r["noref"] or "").strip() if r["noref"] else "",
                    code_avocat=(r["code_avocat"] or "").strip() if r["code_avocat"] else "",
                    nom_avocat=(r["nom_avocat"] or "").strip() if r["nom_avocat"] else "",
                    date_emis=r["date_emis"].isoformat() if r["date_emis"] else None,
                    date_retro=r["date_retro"].isoformat() if r["date_retro"] else None,
                    conditionnel=(r["conditionnel"] or "N"),
                    nom_requerant=(r["nom_requerant"] or "").strip() if r["nom_requerant"] else "",
                    prenom_requerant=(r["prenom_requerant"] or "").strip() if r["prenom_requerant"] else "",
                ))
        return rows, None
    except Exception as e:  # noqa: BLE001
        msg = str(e)
        logger.warning("Requête %s échouée : %s", table, msg)
        return [], msg


@router.post("/search", response_model=MandatSearchOut)
def search_mandats(
    payload: MandatSearchIn,
    user: dict = Depends(require_role("ti")),
    db: Session = Depends(get_db),
):
    """Recherche unifiée des mandats Themis (atattest + megaattest, requêtes séparées).

    4 modes (équivalents au VB) :
      - mandat: filtre noreg + nobur + noref (LIKE pour noref partiel sur 8 chiffres)
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

    # Construit la clause WHERE commune aux 2 tables
    where_clause, params = _build_where_and_params(mandat, code_avo, nom)

    themis = get_secondary_engine("Themis")

    # Exécution SÉPARÉE des 2 tables → si une échoue, l'autre marche quand même.
    errors: dict[str, str] = {}
    rows_atattest, err_a = _query_one_table(
        themis, "atattest", is_megaattest=False,
        where_clause=where_clause, params=params,
    )
    if err_a:
        errors["atattest"] = err_a

    rows_megaattest, err_m = _query_one_table(
        themis, "megaattest", is_megaattest=True,
        where_clause=where_clause, params=params,
    )
    if err_m:
        errors["megaattest"] = err_m

    rows = rows_atattest + rows_megaattest
    rows.sort(key=lambda r: (r.nom_requerant, r.prenom_requerant))
    if len(rows) > 500:
        rows = rows[:500]
        limited = True
    else:
        limited = False

    # Vérification existence des noref dans atattdaj/megaattdaj (alerte VB)
    if mandat and rows:
        for row in rows:
            row.daj_manquant = not _verif_atattdaj(themis, row)

    # Badges Web : un seul appel batch vers Fvi
    fvi_checked = False
    try:
        _enrich_with_fvi_status(rows)
        fvi_checked = True
    except Exception as e:  # noqa: BLE001
        logger.warning("Fvi check skipped : %s", e)
        errors["fvi"] = str(e)
        fvi_checked = False

    return MandatSearchOut(
        items=rows,
        total=len(rows),
        limited=limited,
        fvi_checked=fvi_checked,
        errors=errors,
    )


def _verif_atattdaj(themis_engine, row: MandatRow) -> bool:
    """Vérifie qu'une référence existe dans atattdaj (ou megaattdaj) selon la source."""
    table = "megaattdaj" if row.source == "megaattest" else "atattdaj"
    is_sqlserver = themis_engine.dialect.name in ("mssql", "pyodbc", "pymssql")
    top_clause = "TOP 1" if is_sqlserver else ""
    limit_clause = "" if is_sqlserver else "LIMIT 1"
    sql = text(f"""
        SELECT {top_clause} 1 FROM {table}
        WHERE noreg = :noreg AND nobur = :nobur AND noref = :noref
        {limit_clause}
    """)
    try:
        with themis_engine.connect() as conn:
            result = conn.execute(sql, {
                "noreg": row.noreg, "nobur": row.nobur, "noref": row.noref,
            }).first()
            return result is not None
    except Exception as e:  # noqa: BLE001
        logger.warning("VerifAtattdaj err sur %s/%s/%s : %s", row.noreg, row.nobur, row.noref, e)
        return True  # En cas d'erreur, on ne marque pas comme manquant


def _enrich_with_fvi_status(rows: List[MandatRow]) -> None:
    """Renseigne `sur_web` pour chaque ligne via 1 seule requête vers Fvi.

    Tolérance aux formats legacy :
      - cnoreg / cnobur peuvent être stockés en CHAR(2) avec padding espaces.
      - cnoref peut être stocké avec tiret ("72500038-01") ou sans ("7250003801").
      - Certaines bases Fvi utilisent juste la partie 8 chiffres (sans suffixe).
    On normalise tout côté SQL via RTRIM(LTRIM(...)) + REPLACE(..., '-', '')
    et on compare également avec les variantes sans tiret côté serveur.
    """
    if not rows:
        return
    try:
        fvi = get_secondary_engine("Fvi")
    except Exception as e:
        raise RuntimeError(f"Fvi non disponible : {e}")

    # Pour chaque ligne, on construit des paramètres avec plusieurs variantes
    # de noref : noref tel quel, noref sans tiret, et juste les 8 premiers chiffres.
    conditions = []
    params: dict = {}
    for i, r in enumerate(rows):
        noref = r.noref or ""
        noref_no_dash = noref.replace("-", "")
        # Si format "XXXXXXXX-XX", on garde aussi juste "XXXXXXXX"
        noref_8 = noref.split("-", 1)[0] if "-" in noref else noref[:8]

        conditions.append(
            f"("
            f"  RTRIM(LTRIM(cnoreg)) = :nor{i} "
            f"  AND RTRIM(LTRIM(cnobur)) = :nob{i} "
            f"  AND ("
            f"     RTRIM(LTRIM(cnoref)) = :ref{i}_full "
            f"     OR RTRIM(LTRIM(cnoref)) = :ref{i}_nodash "
            f"     OR RTRIM(LTRIM(cnoref)) = :ref{i}_8 "
            f"     OR RTRIM(LTRIM(cnoref)) LIKE :ref{i}_like "
            f"  )"
            f")"
        )
        params[f"nor{i}"] = r.noreg
        params[f"nob{i}"] = r.nobur
        params[f"ref{i}_full"] = noref
        params[f"ref{i}_nodash"] = noref_no_dash
        params[f"ref{i}_8"] = noref_8
        params[f"ref{i}_like"] = f"{noref_8}%"

    sql = text(f"""
        SELECT cnoreg, cnobur, cnoref FROM Mandats
        WHERE {' OR '.join(conditions)}
    """)

    # Normalisation pour comparer côté Python également
    def norm(s):
        return (s or "").strip().replace("-", "")

    found_norm: set[tuple[str, str, str]] = set()
    with fvi.connect() as conn:
        for fr in conn.execute(sql, params):
            found_norm.add((
                str(fr[0]).strip(),
                str(fr[1]).strip(),
                norm(str(fr[2])),
            ))

    for row in rows:
        # Test le couple (noreg, nobur, noref normalisé sans tiret)
        # avec plusieurs variantes possibles côté row
        keys = {
            (row.noreg, row.nobur, norm(row.noref)),
            (row.noreg, row.nobur, norm(row.noref.split("-", 1)[0] if "-" in row.noref else row.noref[:8])),
        }
        row.sur_web = any(k in found_norm for k in keys)


# ============================================================
#                       Diagnostic (TI uniquement)
# ============================================================
@router.get("/diagnostic")
def diagnostic(
    user: dict = Depends(require_role("ti")),
):
    """Diagnostic des bases Themis/Fvi pour aider à débuguer les recherches.

    Retourne :
      - Existence des tables atattest / megaattest / atattdaj / megaattdaj
      - Colonnes détectées
      - Sample row (premier enregistrement, censuré)
      - Compteur total par table
    """
    out: dict = {"themis": {}, "fvi": {}}

    themis = get_secondary_engine("Themis")
    is_sqlserver = themis.dialect.name in ("mssql", "pyodbc", "pymssql")

    for table in ("atattest", "megaattest", "atattdaj", "megaattdaj"):
        info: dict = {"exists": False}
        try:
            with themis.connect() as conn:
                if is_sqlserver:
                    cnt = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                    cols_q = text(
                        "SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH "
                        "FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = :t"
                    )
                    cols = [
                        {"name": r[0], "type": r[1], "len": r[2]}
                        for r in conn.execute(cols_q, {"t": table})
                    ]
                else:
                    cnt = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                    cols = []
                info["exists"] = True
                info["row_count"] = cnt
                info["columns"] = cols

                # Sample : premiers noreg/nobur/noref pour voir le format réel
                sample_sql = text(
                    f"SELECT {'TOP 3' if is_sqlserver else ''} "
                    "noreg, nobur, noref, adatcodeavomand "
                    f"FROM {table} {'' if is_sqlserver else 'LIMIT 3'}"
                )
                sample = []
                for r in conn.execute(sample_sql).mappings():
                    sample.append({
                        "noreg": repr(r["noreg"]),
                        "nobur": repr(r["nobur"]),
                        "noref": repr(r["noref"]),
                        "code_avocat": repr(r["adatcodeavomand"]),
                    })
                info["sample"] = sample
        except Exception as e:  # noqa: BLE001
            info["error"] = str(e)
        out["themis"][table] = info

    # Test Fvi
    try:
        fvi = get_secondary_engine("Fvi")
        fvi_is_sqlserver = fvi.dialect.name in ("mssql", "pyodbc", "pymssql")
        with fvi.connect() as conn:
            info: dict = {"exists": True}
            cnt = conn.execute(text("SELECT COUNT(*) FROM Mandats")).scalar()
            info["row_count"] = cnt

            # Colonnes réelles (SQL Server)
            if fvi_is_sqlserver:
                cols_q = text(
                    "SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH "
                    "FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Mandats'"
                )
                info["columns"] = [
                    {"name": r[0], "type": r[1], "len": r[2]}
                    for r in conn.execute(cols_q)
                ]
            else:
                info["columns"] = []

            # Sample : 3 premiers rows avec colonnes cnoreg/cnobur/cnoref
            try:
                sample_sql = text(
                    f"SELECT {'TOP 3' if fvi_is_sqlserver else ''} "
                    "cnoreg, cnobur, cnoref FROM Mandats "
                    f"{'' if fvi_is_sqlserver else 'LIMIT 3'}"
                )
                info["sample"] = [
                    {"cnoreg": repr(r["cnoreg"]),
                     "cnobur": repr(r["cnobur"]),
                     "cnoref": repr(r["cnoref"])}
                    for r in conn.execute(sample_sql).mappings()
                ]
            except Exception as e:  # noqa: BLE001
                info["sample_error"] = str(e)

            out["fvi"]["Mandats"] = info
    except Exception as e:  # noqa: BLE001
        out["fvi"]["Mandats"] = {"exists": False, "error": str(e)}

    return out


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



@router.post("/reinit-batch", response_model=ReinitBatchOut)
def reinit_mandats_batch(
    payload: ReinitBatchIn,
    user: dict = Depends(require_role("ti")),
    _: Session = Depends(get_db),
):
    """Réinitialise plusieurs mandats en une seule opération.

    Confirmation simplifiée : l'utilisateur a déjà sélectionné les mandats
    via checkboxes et coché la case "Je confirme" — pas besoin de retaper.

    UPDATE atattest pour les sources 'atattest', UPDATE megaattest pour 'megaattest'.
    Chaque mandat est réinitialisé indépendamment ; si l'un échoue, les autres
    continuent et on retourne le détail par mandat.
    """
    if not payload.confirmed:
        raise HTTPException(
            status_code=400,
            detail="Vous devez cocher la case de confirmation pour procéder.",
        )
    if not payload.items:
        raise HTTPException(
            status_code=400,
            detail="Aucun mandat sélectionné.",
        )
    if len(payload.items) > 100:
        raise HTTPException(
            status_code=400,
            detail="Maximum 100 mandats par lot.",
        )

    themis = get_secondary_engine("Themis")
    results: list[ReinitBatchResultItem] = []
    success_count = 0
    error_count = 0

    for item in payload.items:
        mandat_label = f"{item.noreg}-{item.nobur}-{item.noref}"
        table = "megaattest" if item.source == "megaattest" else "atattest"

        sql = text(f"""
            UPDATE {table}
            SET noregbur = noregbur
            WHERE noreg = :noreg AND nobur = :nobur AND noref = :noref
        """)

        try:
            with themis.begin() as conn:
                result = conn.execute(sql, {
                    "noreg": item.noreg,
                    "nobur": item.nobur,
                    "noref": item.noref,
                })
                rows_affected = result.rowcount

            if rows_affected == 0:
                results.append(ReinitBatchResultItem(
                    mandat=mandat_label,
                    source=item.source,
                    ok=False,
                    error=f"Mandat introuvable dans {table}",
                ))
                error_count += 1
            else:
                results.append(ReinitBatchResultItem(
                    mandat=mandat_label,
                    source=item.source,
                    ok=True,
                ))
                success_count += 1
                logger.info(
                    "Mandat %s (%s) réinitialisé par %s",
                    mandat_label, table, user.get("email", ""),
                )
        except Exception as e:  # noqa: BLE001
            logger.warning("Reinit batch err sur %s : %s", mandat_label, e)
            results.append(ReinitBatchResultItem(
                mandat=mandat_label,
                source=item.source,
                ok=False,
                error=str(e)[:200],
            ))
            error_count += 1

    return ReinitBatchOut(
        results=results,
        success_count=success_count,
        error_count=error_count,
    )
