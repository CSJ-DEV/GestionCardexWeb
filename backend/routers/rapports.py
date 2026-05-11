"""Routes Rapports PDF : Registre97, Registre98, ListeDetBar/Dist/Reg, ListeSom."""
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

router = APIRouter(prefix="/rapports", tags=["rapports"])


def _avo_for_mandat(db: Session, avocat_id: str) -> dict:
    a = db.query(Avocat).filter_by(id=avocat_id).first()
    if not a:
        return {}
    return {"code": a.code or "", "nom": a.nom, "prenom": a.prenom, "type_code": a.type_code or "P"}


def _avocats_actifs_with_mega(db: Session) -> list[dict]:
    avos = (db.query(Avocat).filter(Avocat.actif.is_(True), Avocat.id.isnot(None))
              .order_by(asc(Avocat.nom), asc(Avocat.prenom)).all())
    out = []
    for a in avos:
        d = avocat_to_dict(a)
        m = db.query(InfoMega).filter_by(avocat_id=a.id).first()
        districts = []
        if m and a.code:
            districts = [r.nodist for r in db.query(InfoDistrict).filter_by(code=a.code).all()]
        d["_mega"] = mega_to_dict(m, districts) if m else {}
        out.append(d)
    return out


@router.get("/registre97")
def rapport_registre97(date_debut: str, date_fin: str,
                       user: dict = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    rows = db.query(Mandat).filter(Mandat.date_ordonnance >= date_debut,
                                   Mandat.date_ordonnance <= date_fin).all()
    avo_cache: dict[str, dict] = {}
    rows_par_article: dict[str, list[dict]] = {}
    for m in rows:
        if m.avocat_id not in avo_cache:
            avo_cache[m.avocat_id] = _avo_for_mandat(db, m.avocat_id)
        a = avo_cache[m.avocat_id]
        d = mandat_to_dict(m)
        d["avocat_nom"] = f"{a.get('code','')}  {a.get('nom','')}, {a.get('prenom','')}".strip() if a else "—"
        d["avocat_type"] = a.get("type_code", "P") if a else "P"
        rows_par_article.setdefault(d.get("article", "486.3"), []).append(d)
    pdf = build_registre97(date_debut, date_fin, rows_par_article)
    return StreamingResponse(iter([pdf]), media_type="application/pdf",
                             headers={"Content-Disposition": f'attachment; filename="registre97_{date_debut}_{date_fin}.pdf"'})


@router.get("/registre98")
def rapport_registre98(date_debut: str, date_fin: str,
                       user: dict = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    rows = db.query(Mandat).filter(Mandat.date_ordonnance >= date_debut,
                                   Mandat.date_ordonnance <= date_fin).all()
    avo_cache: dict[str, dict] = {}
    rows_par_article: dict[str, list[dict]] = {}
    for m in rows:
        if m.avocat_id not in avo_cache:
            avo_cache[m.avocat_id] = _avo_for_mandat(db, m.avocat_id)
        a = avo_cache[m.avocat_id]
        d = mandat_to_dict(m)
        d["avocat_code"] = a.get("code", "") if a else ""
        d["avocat_nom"] = f"{a.get('nom','')}, {a.get('prenom','')}" if a else ""
        rows_par_article.setdefault(d.get("article", "486.3"), []).append(d)
    pdf = build_registre98(date_debut, date_fin, rows_par_article)
    return StreamingResponse(iter([pdf]), media_type="application/pdf",
                             headers={"Content-Disposition": f'attachment; filename="registre98_{date_debut}_{date_fin}.pdf"'})


@router.get("/liste-det-bar")
def rapport_liste_det_bar(user: dict = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    avos = _avocats_actifs_with_mega(db)
    groups: dict[str, list[dict]] = {}
    for a in avos:
        key = a.get("sectbar") or "(Sans section)"
        groups.setdefault(key, []).append(a)
    groups = {k: groups[k] for k in sorted(groups.keys())}
    pdf = build_liste_det_bar(groups)
    return StreamingResponse(iter([pdf]), media_type="application/pdf",
                             headers={"Content-Disposition": 'attachment; filename="liste_det_bar.pdf"'})


@router.get("/liste-det-dist")
def rapport_liste_det_dist(user: dict = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    avos = _avocats_actifs_with_mega(db)
    groups: dict[str, list[dict]] = {}
    for a in avos:
        ville = (a.get("adresse") or {}).get("ville") or "(Sans district)"
        groups.setdefault(ville, []).append(a)
    groups = {k: groups[k] for k in sorted(groups.keys())}
    pdf = build_liste_det_dist(groups)
    return StreamingResponse(iter([pdf]), media_type="application/pdf",
                             headers={"Content-Disposition": 'attachment; filename="liste_det_dist.pdf"'})


@router.get("/liste-det-reg")
def rapport_liste_det_reg(user: dict = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    avos = (db.query(Avocat).filter(Avocat.id.isnot(None))
              .order_by(asc(Avocat.annee_barreau), asc(Avocat.nom)).all())
    groups: dict[str, list[dict]] = {}
    for a in avos:
        d = avocat_to_dict(a)
        m = db.query(InfoMega).filter_by(avocat_id=a.id).first()
        districts = [r.nodist for r in db.query(InfoDistrict).filter_by(code=a.code).all()] if a.code else []
        d["_mega"] = mega_to_dict(m, districts) if m else {}
        annee = d.get("annee_barreau") or ""
        if annee and str(annee).isdigit():
            decade = (int(annee) // 10) * 10
            key = f"Année barreau {decade}"
        else:
            key = "Année barreau (n.d.)"
        groups.setdefault(key, []).append(d)
    groups = {k: groups[k] for k in sorted(groups.keys())}
    pdf = build_liste_det_reg(groups)
    return StreamingResponse(iter([pdf]), media_type="application/pdf",
                             headers={"Content-Disposition": 'attachment; filename="liste_det_reg.pdf"'})


@router.get("/liste-som")
def rapport_liste_som(date_debut: Optional[str] = None, date_fin: Optional[str] = None,
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    if not date_debut:
        date_debut = datetime.now().strftime("%Y-%m-01")
    if not date_fin:
        date_fin = datetime.now().strftime("%Y-%m-%d")
    avos = _avocats_actifs_with_mega(db)
    pdf = build_liste_som(date_debut, date_fin, avos)
    return StreamingResponse(iter([pdf]), media_type="application/pdf",
                             headers={"Content-Disposition": 'attachment; filename="liste_som.pdf"'})
