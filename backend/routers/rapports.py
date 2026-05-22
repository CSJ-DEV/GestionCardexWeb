"""Routes Rapports PDF : Registre97, Registre98, ListeDetBar/Dist/Reg, ListeSom.

Optimisations pour gros volumes :
- Lecture BDD par batches via SQLAlchemy `yield_per()` (économise la RAM Python)
- Réponse HTTP en streaming par chunks de 64 Ko (économise le buffer de réponse)
- Header `Content-Length` exposé → barre de progression navigateur
- Header `X-Accel-Buffering: no` → désactive le buffering du proxy nginx
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import asc
from sqlalchemy.orm import Session

from audit import avocat_to_dict, mandat_to_dict, mega_to_dict
from database import get_db
from models import Avocat, Mandat, InfoMega, InfoDistrict
from pdf_reports import (
    build_registre97, build_registre98, build_liste_det_bar,
    build_liste_det_dist, build_liste_det_reg, build_liste_som,
)
from security import get_current_user
from streaming import chunk_bytes, pdf_streaming_headers

router = APIRouter(prefix="/rapports", tags=["rapports"])

# Taille de batch pour la lecture BDD. yield_per permet à SQLAlchemy de ne
# matérialiser que `BATCH_SIZE` rangées en mémoire à la fois.
BATCH_SIZE = 500


def _stream_pdf(pdf_bytes: bytes, filename: str) -> StreamingResponse:
    """Renvoie un PDF en streaming chunked + headers de progression."""
    return StreamingResponse(
        chunk_bytes(pdf_bytes),
        media_type="application/pdf",
        headers=pdf_streaming_headers(filename, len(pdf_bytes)),
    )


def _avo_for_mandat(db: Session, avocat_id: str, cache: dict[str, dict]) -> dict:
    if avocat_id in cache:
        return cache[avocat_id]
    a = db.query(Avocat).filter_by(id=avocat_id).first()
    cache[avocat_id] = (
        {"code": a.code or "", "nom": a.nom, "prenom": a.prenom, "type_code": a.type_code or "P"}
        if a else {}
    )
    return cache[avocat_id]


def _iter_avocats_actifs_with_mega(db: Session):
    """Itère les avocats actifs avec leur méga, en batches BATCH_SIZE.

    Pour chaque code, on précharge les districts en un seul aller-retour SQL
    (groupe par batch) au lieu de N requêtes individuelles.
    """
    base_q = (db.query(Avocat).filter(Avocat.actif.is_(True), Avocat.id.isnot(None))
                .order_by(asc(Avocat.nom), asc(Avocat.prenom))
                .yield_per(BATCH_SIZE))

    batch: list[Avocat] = []
    for a in base_q:
        batch.append(a)
        if len(batch) >= BATCH_SIZE:
            yield from _hydrate_batch(db, batch)
            batch = []
    if batch:
        yield from _hydrate_batch(db, batch)


def _hydrate_batch(db: Session, batch: list[Avocat]):
    """Précharge méga + districts pour un batch d'avocats (2 requêtes au lieu de 2N)."""
    codes = [a.code for a in batch if a.code]
    ids = [a.id for a in batch if a.id]
    mega_map: dict[str, InfoMega] = {}
    districts_map: dict[str, list[int]] = {}
    if ids:
        for m in db.query(InfoMega).filter(InfoMega.avocat_id.in_(ids)):
            mega_map[m.avocat_id] = m
    if codes:
        for r in db.query(InfoDistrict).filter(InfoDistrict.code.in_(codes)):
            districts_map.setdefault(r.code, []).append(r.nodist)
    for a in batch:
        d = avocat_to_dict(a)
        m = mega_map.get(a.id)
        ds = districts_map.get(a.code or "", [])
        d["_mega"] = mega_to_dict(m, ds) if m else {}
        yield d


# ---------- Rapports ----------
def _parse_date_arg(s: str):
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


@router.get("/registre97")
def rapport_registre97(date_debut: str, date_fin: str,
                       user: dict = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    avo_cache: dict[str, dict] = {}
    rows_par_article: dict[str, list[dict]] = {}
    d1, d2 = _parse_date_arg(date_debut), _parse_date_arg(date_fin)
    # Mandats : yield_per pour ne pas charger tout en RAM si > 10k mandats
    q = (db.query(Mandat).filter(Mandat.date_ordonnance >= d1,
                                  Mandat.date_ordonnance <= d2)
                          .yield_per(BATCH_SIZE))
    for m in q:
        a = _avo_for_mandat(db, m.avocat_id, avo_cache)
        d = mandat_to_dict(m)
        d["avocat_nom"] = f"{a.get('code','')}  {a.get('nom','')}, {a.get('prenom','')}".strip() if a else "—"
        d["avocat_type"] = a.get("type_code", "P") if a else "P"
        rows_par_article.setdefault(d.get("article", "486.3"), []).append(d)
    pdf = build_registre97(date_debut, date_fin, rows_par_article)
    return _stream_pdf(pdf, f"registre97_{date_debut}_{date_fin}.pdf")


@router.get("/registre98")
def rapport_registre98(date_debut: str, date_fin: str,
                       user: dict = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    avo_cache: dict[str, dict] = {}
    rows_par_article: dict[str, list[dict]] = {}
    d1, d2 = _parse_date_arg(date_debut), _parse_date_arg(date_fin)
    q = (db.query(Mandat).filter(Mandat.date_ordonnance >= d1,
                                  Mandat.date_ordonnance <= d2)
                          .yield_per(BATCH_SIZE))
    for m in q:
        a = _avo_for_mandat(db, m.avocat_id, avo_cache)
        d = mandat_to_dict(m)
        d["avocat_code"] = a.get("code", "") if a else ""
        d["avocat_nom"] = f"{a.get('nom','')}, {a.get('prenom','')}" if a else ""
        rows_par_article.setdefault(d.get("article", "486.3"), []).append(d)
    pdf = build_registre98(date_debut, date_fin, rows_par_article)
    return _stream_pdf(pdf, f"registre98_{date_debut}_{date_fin}.pdf")


@router.get("/liste-det-bar")
def rapport_liste_det_bar(user: dict = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    groups: dict[str, list[dict]] = {}
    for a in _iter_avocats_actifs_with_mega(db):
        key = a.get("sectbar") or "(Sans section)"
        groups.setdefault(key, []).append(a)
    groups = {k: groups[k] for k in sorted(groups.keys())}
    pdf = build_liste_det_bar(groups)
    return _stream_pdf(pdf, "liste_det_bar.pdf")


@router.get("/liste-det-dist")
def rapport_liste_det_dist(user: dict = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    groups: dict[str, list[dict]] = {}
    for a in _iter_avocats_actifs_with_mega(db):
        ville = (a.get("adresse") or {}).get("ville") or "(Sans district)"
        groups.setdefault(ville, []).append(a)
    groups = {k: groups[k] for k in sorted(groups.keys())}
    pdf = build_liste_det_dist(groups)
    return _stream_pdf(pdf, "liste_det_dist.pdf")


@router.get("/liste-det-reg")
def rapport_liste_det_reg(user: dict = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    # Ce rapport inclut TOUS les avocats (actifs + inactifs)
    base_q = (db.query(Avocat).filter(Avocat.id.isnot(None))
                .order_by(asc(Avocat.annee_barreau), asc(Avocat.nom))
                .yield_per(BATCH_SIZE))
    groups: dict[str, list[dict]] = {}
    batch: list[Avocat] = []

    def flush():
        for d in _hydrate_batch(db, batch):
            annee = d.get("annee_barreau") or ""
            if annee and str(annee).isdigit():
                decade = (int(annee) // 10) * 10
                key = f"Année barreau {decade}"
            else:
                key = "Année barreau (n.d.)"
            groups.setdefault(key, []).append(d)

    for a in base_q:
        batch.append(a)
        if len(batch) >= BATCH_SIZE:
            flush()
            batch = []
    if batch:
        flush()

    groups = {k: groups[k] for k in sorted(groups.keys())}
    pdf = build_liste_det_reg(groups)
    return _stream_pdf(pdf, "liste_det_reg.pdf")


@router.get("/liste-som")
def rapport_liste_som(date_debut: Optional[str] = None, date_fin: Optional[str] = None,
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    if not date_debut:
        date_debut = datetime.now().strftime("%Y-%m-01")
    if not date_fin:
        date_fin = datetime.now().strftime("%Y-%m-%d")
    avos = list(_iter_avocats_actifs_with_mega(db))
    pdf = build_liste_som(date_debut, date_fin, avos)
    return _stream_pdf(pdf, "liste_som.pdf")
