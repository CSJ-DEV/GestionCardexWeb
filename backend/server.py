"""GestionCardex API — backend FastAPI + SQLAlchemy + SQLite (CardAvo).

Stack :
- FastAPI (HTTP) avec routes synchrones (compatibles thread pool).
- SQLAlchemy 2.0 ORM sur SQLite local (`sqlite_dbs/CardAvo.db`).
- Compatible SQL Server : il suffit de pointer `DATABASE_URL` vers
  `mssql+pymssql://...` pour basculer (pas de changement de code).

Ce module remplace l'ancienne implémentation MongoDB/Motor.
"""
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

import os
import json
import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional

import bcrypt
import jwt
from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends, Query
from fastapi.responses import StreamingResponse, FileResponse
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from sqlalchemy import or_, func, and_, desc, asc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from models import (
    Avocat, Adresse, InfoMega, InfoDistrict, Inhpra,
    AppUser, AuditLog, Connexion, Mandat,
    yn_to_bool, bool_to_yn,
)


# ---------- Setup ----------
JWT_ALGORITHM = "HS256"

app = FastAPI(title="GestionCardex API")
api_router = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("gestioncardex")


# ---------- Helpers ----------
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def get_jwt_secret() -> str:
    return os.environ["JWT_SECRET"]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_access_token(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id, "email": email, "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=60 * 8),
    }
    return jwt.encode(payload, get_jwt_secret(), algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    payload = {
        "sub": user_id, "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }
    return jwt.encode(payload, get_jwt_secret(), algorithm=JWT_ALGORITHM)


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    secure = os.environ.get("COOKIE_SECURE", "false").lower() == "true"
    response.set_cookie("access_token", access_token, httponly=True, secure=secure, samesite="lax",
                        max_age=60 * 60 * 8, path="/")
    response.set_cookie("refresh_token", refresh_token, httponly=True, secure=secure, samesite="lax",
                        max_age=60 * 60 * 24 * 7, path="/")


def get_current_user(request: Request, db: Session = Depends(get_db)) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Non authentifié")
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Type de jeton invalide")
        u = db.query(AppUser).filter_by(id=payload["sub"]).first()
        if not u:
            raise HTTPException(status_code=401, detail="Utilisateur introuvable")
        return {"id": u.id, "email": u.email, "name": u.name, "role": u.role}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Jeton expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Jeton invalide")


# Le rôle TI a tous les droits de l'admin (super-utilisateur technique).
ADMIN_LIKE = {"admin", "ti"}


def require_role(*allowed_roles):
    expanded = set(allowed_roles)
    if "admin" in expanded:
        expanded.add("ti")

    def checker(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role") not in expanded:
            raise HTTPException(status_code=403, detail="Accès refusé")
        return user
    return checker


def funcValidNoAssSoc(no: str) -> bool:
    """Validation Luhn du NAS canadien (port direct du VB legacy)."""
    if not no:
        return True
    no = no.strip()
    if len(no) != 9 or not no.isdigit():
        return False
    tot = 0
    for i, ch in enumerate(no[:-1], start=1):
        c = int(ch)
        if i % 2 == 0:
            c = c * 2
            if c > 9:
                c = (c // 10) + (c % 10)
        tot += c
    v = (10 - (tot % 10)) % 10
    return v == int(no[-1])


def _audit(db: Session, avocat_id: str, action: str, user_email: str, summary: str) -> None:
    """Trace une modification d'avocat dans AuditLog. Best-effort."""
    try:
        entry = AuditLog(
            id=str(uuid.uuid4()),
            avocat_id=avocat_id,
            action=action,
            user_email=user_email or "système",
            summary=summary,
            timestamp=now_iso(),
        )
        db.add(entry)
        db.commit()
    except Exception as e:
        logger.warning(f"audit_log insert failed: {e}")
        db.rollback()


# ---------- Modèles Pydantic ----------
class UserOut(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: str = "admin"


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str = Field(..., min_length=6)
    role: str = Field("editeur", pattern="^(admin|ti|editeur|lecteur)$")


class UserUpdate(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = Field(None, pattern="^(admin|ti|editeur|lecteur)$")


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class AdresseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    address: Optional[str] = ""
    adresse2: Optional[str] = ""
    adresse3: Optional[str] = ""
    ville: Optional[str] = ""
    province: Optional[str] = ""
    codepostal: Optional[str] = ""
    telephone: Optional[str] = ""
    telephone2: Optional[str] = ""
    fax: Optional[str] = ""
    email: Optional[str] = ""


class AvocatBase(BaseModel):
    model_config = ConfigDict(extra="ignore")
    code: Optional[str] = Field(None, max_length=10)
    type_code: str = Field("A")
    nom: str = Field(..., min_length=1, max_length=80)
    prenom: str = Field(..., min_length=1, max_length=80)
    sectbar: Optional[str] = ""
    mega: bool = False
    actif: bool = True
    attente: bool = False
    annee_barreau: Optional[str] = ""
    dateinscbarr: Optional[str] = ""
    payable: bool = True
    codebar: Optional[str] = ""
    comm: Optional[str] = ""
    nas: Optional[str] = ""
    taxes: Optional[str] = ""
    depodirect: bool = False
    factweb: bool = False
    confweb: bool = False
    villerref: Optional[str] = ""
    surveil: bool = False
    neq: Optional[str] = ""
    codeusager: Optional[str] = ""
    adresse: AdresseModel = Field(default_factory=AdresseModel)


class AvocatCreate(AvocatBase):
    pass


class AvocatUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type_code: Optional[str] = None
    nom: Optional[str] = None
    prenom: Optional[str] = None
    sectbar: Optional[str] = None
    mega: Optional[bool] = None
    actif: Optional[bool] = None
    attente: Optional[bool] = None
    annee_barreau: Optional[str] = None
    taxes: Optional[str] = None
    dateinscbarr: Optional[str] = None
    payable: Optional[bool] = None
    codebar: Optional[str] = None
    comm: Optional[str] = None
    nas: Optional[str] = None
    depodirect: Optional[bool] = None
    factweb: Optional[bool] = None
    confweb: Optional[bool] = None
    villerref: Optional[str] = None
    surveil: Optional[bool] = None
    neq: Optional[str] = None
    codeusager: Optional[str] = None
    adresse: Optional[AdresseModel] = None


class AvocatOut(AvocatBase):
    id: str
    created_at: str
    updated_at: str
    usermodif: Optional[str] = ""


class AvocatsListOut(BaseModel):
    items: List[AvocatOut]
    total: int
    page: int
    page_size: int


class StatsOut(BaseModel):
    total: int
    actifs: int
    inactifs: int
    mega: int
    nouveaux_30j: int


# ---------- Sérialisation ORM → Pydantic ----------
def avocat_to_dict(a: Avocat) -> dict:
    """Convertit un ORM Avocat → dict prêt pour AvocatOut."""
    adr_data = {}
    if a.adresse_courante:
        try:
            adr_data = json.loads(a.adresse_courante)
        except (json.JSONDecodeError, TypeError):
            adr_data = {}
    return {
        "id": a.id or "",
        "code": a.code or "",
        "type_code": a.type_code or "A",
        "nom": a.nom or "",
        "prenom": a.prenom or "",
        "sectbar": a.sectbar or "",
        "mega": yn_to_bool(a.mega),
        "actif": bool(a.actif) if a.actif is not None else True,
        "attente": bool(a.attente) if a.attente is not None else False,
        "annee_barreau": a.annee_barreau or "",
        "dateinscbarr": a.dateinscbarr or "",
        "payable": yn_to_bool(a.payable),
        "codebar": a.codebar or "",
        "comm": a.comm or "",
        "nas": a.nas or "",
        "taxes": a.taxes or "",
        "depodirect": yn_to_bool(a.depodirect),
        "factweb": yn_to_bool(a.factweb),
        "confweb": yn_to_bool(a.confweb),
        "villerref": a.villerref or a.villeref or "",
        "surveil": yn_to_bool(a.surveil),
        "neq": a.neq or "",
        "codeusager": a.codeusager or "",
        "adresse": adr_data or {},
        "created_at": a.created_at or "",
        "updated_at": a.updated_at or "",
        "usermodif": a.usermodif or "",
    }


def adresse_to_dict(adr: Adresse) -> dict:
    return {
        "id": adr.id,
        "avocat_id": adr.avocat_id or "",
        "address": adr.address or "",
        "adresse2": adr.adresse2 or "",
        "adresse3": adr.adresse3 or "",
        "ville": adr.ville or "",
        "province": adr.province or "",
        "codepostal": adr.codepostal or "",
        "telephone": adr.telephone or "",
        "telephone2": adr.telephone2 or "",
        "fax": adr.fax or "",
        "email": adr.email or adr.adremail or "",
        "courant": yn_to_bool(adr.courant),
        "created_at": adr.created_at or "",
        "updated_at": adr.updated_at or "",
    }


def mega_to_dict(m: InfoMega, districts: list[int]) -> dict:
    return {
        "id": m.id,
        "avocat_id": m.avocat_id or "",
        "sectbar": m.sectbar or "",
        "districthab": m.districthab or "",
        "francais": yn_to_bool(m.francais),
        "anglais": yn_to_bool(m.anglais),
        "autres": m.autres or "",
        "experience": m.experience or 0,
        "details": m.details or "",
        "art486": yn_to_bool(m.art486),
        "art672": yn_to_bool(m.art672),
        "art684": yn_to_bool(m.art684),
        "commentaire": m.commentaire or "",
        "dateinsc": m.dateinsc or "",
        "districts": districts,
        "tous_districts": bool(m.tous_districts),
        "updated_at": m.updated_at or "",
        "usermodif": m.usermodif or "",
    }


def inhab_to_dict(i: Inhpra) -> dict:
    return {
        "id": i.uuid or str(i.Id),
        "avocat_id": i.avocat_id or "",
        "datedeb": i.datedeb or "",
        "datefin": i.datefin or "",
        "comm": i.comm or "",
        "created_at": i.created_at or "",
        "updated_at": i.updated_at or "",
    }


# ---------- Auth Endpoints ----------
@api_router.post("/auth/login", response_model=UserOut)
def login(payload: LoginIn, response: Response, db: Session = Depends(get_db)):
    email = payload.email.lower()
    u = db.query(AppUser).filter_by(email=email).first()
    if not u or not verify_password(payload.password, u.password_hash):
        raise HTTPException(status_code=401, detail="Identifiants invalides")
    access = create_access_token(u.id, u.email)
    refresh = create_refresh_token(u.id)
    set_auth_cookies(response, access, refresh)
    return UserOut(id=u.id, email=u.email, name=u.name or "", role=u.role or "admin")


@api_router.post("/auth/logout")
def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return {"ok": True}


@api_router.post("/auth/refresh", response_model=UserOut)
def refresh_token_endpoint(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Aucun jeton de rafraîchissement")
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Type de jeton invalide")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expirée — veuillez vous reconnecter")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Jeton invalide")
    u = db.query(AppUser).filter_by(id=payload["sub"]).first()
    if not u:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable")
    set_auth_cookies(response, create_access_token(u.id, u.email), create_refresh_token(u.id))
    return UserOut(id=u.id, email=u.email, name=u.name or "", role=u.role or "admin")


@api_router.get("/auth/me", response_model=UserOut)
def me(user: dict = Depends(get_current_user)):
    return UserOut(id=user["id"], email=user["email"], name=user.get("name") or "", role=user.get("role") or "admin")


# ---------- Avocats Endpoints ----------
@api_router.get("/avocats", response_model=AvocatsListOut)
def list_avocats(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None),
    statut: Optional[str] = Query(None),
    mega: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
):
    query = db.query(Avocat).filter(Avocat.id.isnot(None))
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Avocat.code.ilike(like), Avocat.nom.ilike(like), Avocat.prenom.ilike(like)))
    if statut == "actif":
        query = query.filter(Avocat.actif.is_(True))
    elif statut == "inactif":
        query = query.filter(Avocat.actif.is_(False))
    if mega is not None:
        query = query.filter(Avocat.mega == ("O" if mega else "N"))
    total = query.count()
    rows = (query.order_by(asc(Avocat.nom), asc(Avocat.prenom))
                 .offset((page - 1) * page_size).limit(page_size).all())
    items = [AvocatOut(**avocat_to_dict(a)) for a in rows]
    return AvocatsListOut(items=items, total=total, page=page, page_size=page_size)


def _generate_avocat_code(db: Session, type_code: str) -> str:
    """Calcule le prochain code séquentiel (format <type><5 chiffres>)."""
    type_code = (type_code or "A").upper()
    rows = (db.query(Avocat.code)
              .filter(Avocat.code.like(f"{type_code}%"))
              .order_by(desc(Avocat.code)).limit(50).all())
    next_num = 1
    for (c,) in rows:
        try:
            n = int(c[1:])
            if n >= next_num:
                next_num = n + 1
        except (ValueError, TypeError):
            continue
    return f"{type_code}{next_num:05d}"


@api_router.get("/avocats/next-code")
def next_avocat_code(
    type: str = Query("A", pattern="^[ANP]$"),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return {"code": _generate_avocat_code(db, type)}


@api_router.get("/avocats/stats", response_model=StatsOut)
def avocats_stats(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    base = db.query(Avocat).filter(Avocat.id.isnot(None))
    total = base.count()
    actifs = base.filter(Avocat.actif.is_(True)).count()
    inactifs = base.filter(Avocat.actif.is_(False)).count()
    mega = base.filter(Avocat.mega == "O").count()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    nouveaux = base.filter(Avocat.created_at >= cutoff).count()
    return StatsOut(total=total, actifs=actifs, inactifs=inactifs, mega=mega, nouveaux_30j=nouveaux)


@api_router.get("/avocats/{avocat_id}", response_model=AvocatOut)
def get_avocat(avocat_id: str, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    a = db.query(Avocat).filter_by(id=avocat_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    return AvocatOut(**avocat_to_dict(a))


@api_router.post("/avocats", response_model=AvocatOut, status_code=201)
def create_avocat(payload: AvocatCreate, user: dict = Depends(require_role("admin", "editeur")),
                  db: Session = Depends(get_db)):
    if payload.nas and not funcValidNoAssSoc(payload.nas):
        raise HTTPException(status_code=422, detail="Numéro NAS invalide (algorithme Luhn)")
    type_code = (payload.type_code or "A").upper()
    if type_code not in {"A", "N", "P"}:
        raise HTTPException(status_code=422, detail="type_code invalide (A/N/P)")

    new_id = str(uuid.uuid4())
    now = now_iso()
    adr_json = json.dumps(payload.adresse.model_dump()) if payload.adresse else "{}"

    # Retry sur conflit d'unicité du code
    last_err: Optional[Exception] = None
    for _ in range(5):
        code = _generate_avocat_code(db, type_code)
        a = Avocat(
            code=code, id=new_id, type_code=type_code,
            nom=payload.nom, prenom=payload.prenom,
            sectbar=payload.sectbar or "",
            mega=bool_to_yn(payload.mega), actpass="A" if payload.actif else "P",
            actif=payload.actif, attente=payload.attente,
            annee_barreau=payload.annee_barreau or "",
            dateinscbarr=payload.dateinscbarr or "",
            payable=bool_to_yn(payload.payable),
            codebar=payload.codebar or "", comm=payload.comm or "",
            nas=payload.nas or "", taxes=payload.taxes or "",
            depodirect=bool_to_yn(payload.depodirect),
            factweb=bool_to_yn(payload.factweb),
            confweb=bool_to_yn(payload.confweb),
            villerref=payload.villerref or "", villeref=payload.villerref or "",
            surveil=bool_to_yn(payload.surveil),
            neq=payload.neq or "", codeusager=payload.codeusager or "",
            adresse_courante=adr_json,
            created_at=now, updated_at=now,
            usermodif=user.get("email", ""),
        )
        try:
            db.add(a)
            db.commit()
            db.refresh(a)
            _audit(db, new_id, "create", user.get("email", ""),
                   f"Création de la fiche {code} — {payload.nom}, {payload.prenom}")
            return AvocatOut(**avocat_to_dict(a))
        except IntegrityError as e:
            db.rollback()
            last_err = e
            continue
    logger.error(f"Avocat code generation failed: {last_err}")
    raise HTTPException(status_code=500, detail="Impossible de générer un code unique. Réessayez.")


@api_router.put("/avocats/{avocat_id}", response_model=AvocatOut)
def update_avocat(avocat_id: str, payload: AvocatUpdate,
                  user: dict = Depends(require_role("admin", "editeur")),
                  db: Session = Depends(get_db)):
    a = db.query(Avocat).filter_by(id=avocat_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Avocat introuvable")

    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="Aucun champ à mettre à jour")

    yn_fields = {"mega", "payable", "depodirect", "factweb", "confweb", "surveil"}
    bool_fields = {"actif", "attente"}

    changed = []
    for k, v in data.items():
        if k == "adresse" and v is not None:
            a.adresse_courante = json.dumps(v if isinstance(v, dict) else v.model_dump())
            changed.append("adresse")
        elif k in yn_fields:
            setattr(a, k, bool_to_yn(v))
            changed.append(k)
        elif k in bool_fields:
            setattr(a, k, bool(v))
            if k == "actif":
                a.actpass = "A" if v else "P"
            changed.append(k)
        elif k == "villerref":
            a.villerref = v or ""
            a.villeref = v or ""  # garde la colonne legacy synchronisée
            changed.append(k)
        else:
            setattr(a, k, v)
            changed.append(k)

    a.updated_at = now_iso()
    a.usermodif = user.get("email", "")
    db.commit()
    db.refresh(a)
    if changed:
        _audit(db, avocat_id, "update", user.get("email", ""),
               f"Modification : {', '.join(sorted(changed))}")
    return AvocatOut(**avocat_to_dict(a))


@api_router.delete("/avocats/{avocat_id}")
def delete_avocat(avocat_id: str, user: dict = Depends(require_role("admin")),
                  db: Session = Depends(get_db)):
    a = db.query(Avocat).filter_by(id=avocat_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    summary = f"Suppression de {a.code or ''} — {a.nom}, {a.prenom}"
    code = a.code
    db.query(Adresse).filter_by(avocat_id=avocat_id).delete()
    db.query(InfoMega).filter_by(avocat_id=avocat_id).delete()
    db.query(Inhpra).filter_by(avocat_id=avocat_id).delete()
    db.query(Mandat).filter_by(avocat_id=avocat_id).delete()
    if code:
        db.query(InfoDistrict).filter_by(code=code).delete()
    db.delete(a)
    db.commit()
    _audit(db, avocat_id, "delete", user.get("email", ""), summary)
    return {"ok": True}


# ---------- Adresses ----------
@api_router.get("/avocats/{avocat_id}/adresses")
def list_adresses(avocat_id: str, user: dict = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    rows = (db.query(Adresse).filter_by(avocat_id=avocat_id)
              .order_by(desc(Adresse.created_at)).limit(200).all())
    return [adresse_to_dict(a) for a in rows]


@api_router.post("/avocats/{avocat_id}/adresses", status_code=201)
def create_adresse(avocat_id: str, payload: AdresseModel, courant: bool = False,
                   user: dict = Depends(require_role("admin", "editeur")),
                   db: Session = Depends(get_db)):
    avo = db.query(Avocat).filter_by(id=avocat_id).first()
    if not avo:
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    now = now_iso()
    new_id = str(uuid.uuid4())
    if courant:
        # désactive les autres
        db.query(Adresse).filter_by(avocat_id=avocat_id).update({"courant": "N"})
        avo.adresse_courante = json.dumps(payload.model_dump())
        avo.updated_at = now
    adr = Adresse(
        id=new_id, RowId=new_id, avocat_id=avocat_id, code=avo.code,
        address=payload.address or "", adresse2=payload.adresse2 or "",
        adresse3=payload.adresse3 or "", ville=payload.ville or "",
        province=payload.province or "", codepostal=payload.codepostal or "",
        telephone=payload.telephone or "", telephone2=payload.telephone2 or "",
        fax=payload.fax or "", email=payload.email or "", adremail=payload.email or "",
        courant=bool_to_yn(courant),
        created_at=now, updated_at=now,
    )
    db.add(adr)
    db.commit()
    db.refresh(adr)
    _audit(db, avocat_id, "adresse_create", user.get("email", ""),
           f"Adresse ajoutée : {payload.address or '?'}, {payload.ville or ''}".strip(", "))
    return adresse_to_dict(adr)


@api_router.put("/avocats/{avocat_id}/adresses/{adresse_id}")
def update_adresse(avocat_id: str, adresse_id: str, payload: AdresseModel, courant: bool = False,
                   user: dict = Depends(require_role("admin", "editeur")),
                   db: Session = Depends(get_db)):
    adr = db.query(Adresse).filter_by(id=adresse_id, avocat_id=avocat_id).first()
    if not adr:
        raise HTTPException(status_code=404, detail="Adresse introuvable")
    now = now_iso()
    for f in ("address", "adresse2", "adresse3", "ville", "province", "codepostal",
              "telephone", "telephone2", "fax", "email"):
        setattr(adr, f, getattr(payload, f) or "")
    adr.adremail = payload.email or ""
    adr.courant = bool_to_yn(courant)
    adr.updated_at = now
    if courant:
        # désactive les autres
        (db.query(Adresse).filter(Adresse.avocat_id == avocat_id, Adresse.id != adresse_id)
           .update({"courant": "N"}))
        avo = db.query(Avocat).filter_by(id=avocat_id).first()
        if avo:
            avo.adresse_courante = json.dumps(payload.model_dump())
            avo.updated_at = now
    db.commit()
    _audit(db, avocat_id, "adresse_update", user.get("email", ""),
           f"Adresse modifiée : {payload.address or '?'}, {payload.ville or ''}".strip(", "))
    return {"ok": True}


@api_router.delete("/avocats/{avocat_id}/adresses/{adresse_id}")
def delete_adresse(avocat_id: str, adresse_id: str,
                   user: dict = Depends(require_role("admin", "editeur")),
                   db: Session = Depends(get_db)):
    adr = db.query(Adresse).filter_by(id=adresse_id, avocat_id=avocat_id).first()
    if not adr:
        raise HTTPException(status_code=404, detail="Adresse introuvable")
    label = f"{adr.address or '?'}, {adr.ville or ''}"
    db.delete(adr)
    db.commit()
    _audit(db, avocat_id, "adresse_delete", user.get("email", ""),
           f"Adresse supprimée : {label}".strip(", "))
    return {"ok": True}


# ---------- Users CRUD ----------
@api_router.get("/users")
def list_users(user: dict = Depends(require_role("admin")), db: Session = Depends(get_db)):
    q = db.query(AppUser)
    # Cloisonnement : un admin (non-TI) ne voit pas les comptes TI.
    if user.get("role") != "ti":
        q = q.filter(AppUser.role != "ti")
    rows = q.limit(500).all()
    return [{"id": u.id, "email": u.email, "name": u.name or "", "role": u.role,
             "created_at": u.created_at} for u in rows]


@api_router.post("/users", status_code=201)
def create_user(payload: UserCreate, user: dict = Depends(require_role("admin")),
                db: Session = Depends(get_db)):
    # Cloisonnement : seul un TI peut créer un autre TI.
    if payload.role == "ti" and user.get("role") != "ti":
        raise HTTPException(status_code=403, detail="Seul un Technicien TI peut créer un compte TI")
    email = payload.email.lower()
    if db.query(AppUser).filter_by(email=email).first():
        raise HTTPException(status_code=409, detail="Courriel déjà utilisé")
    u = AppUser(id=str(uuid.uuid4()), email=email, name=payload.name, role=payload.role,
                password_hash=hash_password(payload.password), created_at=now_iso())
    db.add(u)
    db.commit()
    return {"id": u.id, "email": email, "name": payload.name, "role": payload.role}


@api_router.put("/users/{user_id}")
def update_user(user_id: str, payload: UserUpdate, user: dict = Depends(require_role("admin")),
                db: Session = Depends(get_db)):
    u = db.query(AppUser).filter_by(id=user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    # Cloisonnement : un admin (non-TI) ne peut ni voir ni modifier un compte TI.
    if u.role == "ti" and user.get("role") != "ti":
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    # Cloisonnement : un admin (non-TI) ne peut pas promouvoir quelqu'un au rôle TI.
    if payload.role == "ti" and user.get("role") != "ti":
        raise HTTPException(status_code=403, detail="Seul un Technicien TI peut attribuer le rôle TI")
    if payload.name is not None:
        u.name = payload.name
    if payload.role is not None:
        u.role = payload.role
    if payload.password:
        u.password_hash = hash_password(payload.password)
    db.commit()
    return {"ok": True}


@api_router.delete("/users/{user_id}")
def delete_user(user_id: str, user: dict = Depends(require_role("admin")),
                db: Session = Depends(get_db)):
    if user_id == user["id"]:
        raise HTTPException(status_code=400, detail="Impossible de supprimer son propre compte")
    u = db.query(AppUser).filter_by(id=user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    # Cloisonnement : un admin (non-TI) ne peut pas supprimer un compte TI.
    if u.role == "ti" and user.get("role") != "ti":
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    db.delete(u)
    db.commit()
    return {"ok": True}


# ---------- Connexions (admin + ti) ----------
from connexions import (  # noqa: E402
    ConnexionCreate, ConnexionUpdate, ConnexionOut,
    encrypt_password, decrypt_password, test_connection,
)


def _conn_to_out(c: Connexion) -> dict:
    return ConnexionOut(
        id=c.id, name=c.name, type=c.type, server=c.server, port=c.port,
        database=c.database or "", user=c.user or "", description=c.description or "",
        has_password=bool(c.password_enc), is_primary=bool(c.is_primary),
        created_at=c.created_at or "", updated_at=c.updated_at or "",
    ).model_dump()


@api_router.get("/connexions")
def list_connexions(user: dict = Depends(require_role("admin")), db: Session = Depends(get_db)):
    rows = db.query(Connexion).order_by(asc(Connexion.name)).all()
    return [_conn_to_out(c) for c in rows]


@api_router.get("/connexions/{conn_id}")
def get_connexion(conn_id: str, user: dict = Depends(require_role("admin")),
                  db: Session = Depends(get_db)):
    c = db.query(Connexion).filter_by(id=conn_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Connexion introuvable")
    return _conn_to_out(c)


@api_router.post("/connexions", status_code=201)
def create_connexion(payload: ConnexionCreate, user: dict = Depends(require_role("admin")),
                     db: Session = Depends(get_db)):
    now = now_iso()
    pwd = (payload.password or "").strip()
    c = Connexion(
        id=str(uuid.uuid4()), name=payload.name, type=payload.type, server=payload.server,
        port=payload.port, user=payload.user or "", database=payload.database or "",
        description=payload.description or "",
        password_enc=encrypt_password(pwd) if pwd else "",
        is_primary=False, created_at=now, updated_at=now,
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return _conn_to_out(c)


@api_router.put("/connexions/{conn_id}")
def update_connexion(conn_id: str, payload: ConnexionUpdate,
                     user: dict = Depends(require_role("admin")),
                     db: Session = Depends(get_db)):
    c = db.query(Connexion).filter_by(id=conn_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Connexion introuvable")
    update = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if c.is_primary:
        update = {k: v for k, v in update.items() if k == "description"}
        if not update:
            raise HTTPException(status_code=403, detail="La connexion principale est en lecture seule (sauf description)")
    pwd = update.pop("password", None)
    if pwd:
        c.password_enc = encrypt_password(pwd)
    for k, v in update.items():
        setattr(c, k, v)
    c.updated_at = now_iso()
    db.commit()
    db.refresh(c)
    return _conn_to_out(c)


@api_router.delete("/connexions/{conn_id}")
def delete_connexion(conn_id: str, user: dict = Depends(require_role("admin")),
                     db: Session = Depends(get_db)):
    c = db.query(Connexion).filter_by(id=conn_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Connexion introuvable")
    if c.is_primary:
        raise HTTPException(status_code=403, detail="La connexion principale ne peut pas être supprimée")
    db.delete(c)
    db.commit()
    return {"ok": True}


@api_router.get("/connexions/{conn_id}/download")
def download_sqlite_file(conn_id: str, user: dict = Depends(require_role("admin")),
                        db: Session = Depends(get_db)):
    c = db.query(Connexion).filter_by(id=conn_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Connexion introuvable")
    if c.type != "sqlite":
        raise HTTPException(status_code=400, detail="Téléchargement réservé aux connexions SQLite")
    file_rel = c.database or ""
    file_path = ROOT_DIR / file_rel
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail=f"Fichier introuvable : {file_rel}")
    return FileResponse(path=str(file_path), media_type="application/x-sqlite3", filename=file_path.name)


@api_router.post("/connexions/{conn_id}/test")
def test_existing_connexion(conn_id: str, user: dict = Depends(require_role("admin")),
                            db: Session = Depends(get_db)):
    c = db.query(Connexion).filter_by(id=conn_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Connexion introuvable")
    pwd = decrypt_password(c.password_enc or "")
    return test_connection(c_type=c.type, server=c.server, port=c.port,
                           user=c.user or "", password=pwd, database=c.database or "")


class ConnexionTestPayload(BaseModel):
    type: str
    server: str
    port: Optional[int] = None
    user: Optional[str] = ""
    password: Optional[str] = ""
    database: Optional[str] = ""


@api_router.post("/connexions/test")
def test_arbitrary_connexion(payload: ConnexionTestPayload,
                             user: dict = Depends(require_role("admin"))):
    return test_connection(
        c_type=payload.type, server=payload.server, port=payload.port,
        user=payload.user or "", password=payload.password or "", database=payload.database or "",
    )


# ---------- Méga ----------
class InfoMegaIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    sectbar: Optional[str] = ""
    districthab: Optional[str] = ""
    francais: bool = True
    anglais: bool = False
    autres: Optional[str] = ""
    experience: Optional[int] = 0
    details: Optional[str] = ""
    art486: bool = False
    art672: bool = False
    art684: bool = False
    commentaire: Optional[str] = ""
    dateinsc: Optional[str] = ""
    districts: List[int] = Field(default_factory=list)
    tous_districts: bool = False


class InhabIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    datedeb: str
    datefin: Optional[str] = ""
    comm: Optional[str] = ""


@api_router.get("/avocats/{avocat_id}/mega")
def get_mega(avocat_id: str, user: dict = Depends(get_current_user),
             db: Session = Depends(get_db)):
    m = db.query(InfoMega).filter_by(avocat_id=avocat_id).first()
    if not m:
        return {}
    avo = db.query(Avocat).filter_by(id=avocat_id).first()
    districts = []
    if avo and avo.code:
        districts = [d.nodist for d in db.query(InfoDistrict).filter_by(code=avo.code).all()]
    return mega_to_dict(m, districts)


@api_router.put("/avocats/{avocat_id}/mega")
def upsert_mega(avocat_id: str, payload: InfoMegaIn,
                user: dict = Depends(require_role("admin", "editeur")),
                db: Session = Depends(get_db)):
    avo = db.query(Avocat).filter_by(id=avocat_id).first()
    if not avo:
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    now = now_iso()
    m = db.query(InfoMega).filter_by(avocat_id=avocat_id).first()
    if not m:
        m = InfoMega(id=str(uuid.uuid4()), avocat_id=avocat_id, code=avo.code,
                     created_at=now)
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
    m.dateinsc = payload.dateinsc or ""
    m.tous_districts = bool(payload.tous_districts)
    m.mega = "O"
    m.updated_at = now
    m.usermodif = user.get("email", "")

    # Districts : delete-and-reinsert
    if avo.code:
        db.query(InfoDistrict).filter_by(code=avo.code).delete()
        for nodist in (payload.districts or []):
            db.add(InfoDistrict(code=avo.code, nodist=int(nodist)))

    avo.mega = "O"
    avo.updated_at = now
    db.commit()
    _audit(db, avocat_id, "mega_update", user.get("email", ""),
           f"Profil Méga mis à jour (sectbar={payload.sectbar or '—'}, exp={payload.experience or 0} an(s), districts={len(payload.districts or [])})")
    return {"ok": True}


@api_router.delete("/avocats/{avocat_id}/mega")
def delete_mega(avocat_id: str, user: dict = Depends(require_role("admin", "editeur")),
                db: Session = Depends(get_db)):
    avo = db.query(Avocat).filter_by(id=avocat_id).first()
    db.query(InfoMega).filter_by(avocat_id=avocat_id).delete()
    if avo and avo.code:
        db.query(InfoDistrict).filter_by(code=avo.code).delete()
    if avo:
        avo.mega = "N"
    db.commit()
    _audit(db, avocat_id, "mega_delete", user.get("email", ""), "Profil Méga supprimé")
    return {"ok": True}


# ---------- Inhabilité ----------
@api_router.get("/avocats/{avocat_id}/inhabilites")
def list_inhab(avocat_id: str, user: dict = Depends(get_current_user),
               db: Session = Depends(get_db)):
    rows = (db.query(Inhpra).filter_by(avocat_id=avocat_id)
              .order_by(desc(Inhpra.datedeb)).limit(200).all())
    return [inhab_to_dict(i) for i in rows]


@api_router.post("/avocats/{avocat_id}/inhabilites", status_code=201)
def create_inhab(avocat_id: str, payload: InhabIn,
                 user: dict = Depends(require_role("admin", "editeur")),
                 db: Session = Depends(get_db)):
    avo = db.query(Avocat).filter_by(id=avocat_id).first()
    if not avo:
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    now = now_iso()
    i = Inhpra(uuid=str(uuid.uuid4()), avocat_id=avocat_id, code=avo.code,
               datedeb=payload.datedeb, datefin=payload.datefin or "",
               comm=payload.comm or "", created_at=now, updated_at=now)
    db.add(i)
    db.commit()
    db.refresh(i)
    _audit(db, avocat_id, "inhab_create", user.get("email", ""),
           f"Période d'inhabilité ajoutée : {payload.datedeb} → {payload.datefin or 'en cours'}")
    return inhab_to_dict(i)


@api_router.put("/avocats/{avocat_id}/inhabilites/{inhab_id}")
def update_inhab(avocat_id: str, inhab_id: str, payload: InhabIn,
                 user: dict = Depends(require_role("admin", "editeur")),
                 db: Session = Depends(get_db)):
    i = db.query(Inhpra).filter_by(uuid=inhab_id, avocat_id=avocat_id).first()
    if not i:
        raise HTTPException(status_code=404, detail="Période introuvable")
    i.datedeb = payload.datedeb
    i.datefin = payload.datefin or ""
    i.comm = payload.comm or ""
    i.updated_at = now_iso()
    db.commit()
    _audit(db, avocat_id, "inhab_update", user.get("email", ""),
           f"Période d'inhabilité modifiée : {payload.datedeb} → {payload.datefin or 'en cours'}")
    return {"ok": True}


@api_router.delete("/avocats/{avocat_id}/inhabilites/{inhab_id}")
def delete_inhab(avocat_id: str, inhab_id: str,
                 user: dict = Depends(require_role("admin", "editeur")),
                 db: Session = Depends(get_db)):
    i = db.query(Inhpra).filter_by(uuid=inhab_id, avocat_id=avocat_id).first()
    if not i:
        raise HTTPException(status_code=404, detail="Période introuvable")
    summary = f"Période supprimée : {i.datedeb or '?'} → {i.datefin or 'en cours'}"
    db.delete(i)
    db.commit()
    _audit(db, avocat_id, "inhab_delete", user.get("email", ""), summary)
    return {"ok": True}


# ---------- Web password ----------
@api_router.put("/avocats/{avocat_id}/web-password")
def set_web_password(avocat_id: str, payload: dict,
                     user: dict = Depends(require_role("admin", "editeur")),
                     db: Session = Depends(get_db)):
    pwd = (payload or {}).get("password", "")
    if len(pwd) < 6:
        raise HTTPException(status_code=400, detail="Mot de passe trop court (min 6)")
    avo = db.query(Avocat).filter_by(id=avocat_id).first()
    if not avo:
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    avo.web_password_hash = hash_password(pwd)
    avo.updated_at = now_iso()
    db.commit()
    _audit(db, avocat_id, "web_password_set", user.get("email", ""), "Mot de passe web défini")
    return {"ok": True}


@api_router.delete("/avocats/{avocat_id}/web-password")
def clear_web_password(avocat_id: str, user: dict = Depends(require_role("admin", "editeur")),
                      db: Session = Depends(get_db)):
    avo = db.query(Avocat).filter_by(id=avocat_id).first()
    if not avo:
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    avo.web_password_hash = None
    avo.updated_at = now_iso()
    db.commit()
    _audit(db, avocat_id, "web_password_clear", user.get("email", ""), "Mot de passe web réinitialisé")
    return {"ok": True}


# ---------- Audit log ----------
@api_router.get("/avocats/{avocat_id}/audit")
def list_audit(avocat_id: str, user: dict = Depends(require_role("admin")),
               db: Session = Depends(get_db),
               page: int = Query(1, ge=1),
               page_size: int = Query(20, ge=1, le=200)):
    base = db.query(AuditLog).filter_by(avocat_id=avocat_id)
    total = base.count()
    rows = (base.order_by(desc(AuditLog.timestamp))
                .offset((page - 1) * page_size).limit(page_size).all())
    items = [{"id": r.id, "avocat_id": r.avocat_id, "action": r.action,
              "user_email": r.user_email, "summary": r.summary or "",
              "timestamp": r.timestamp} for r in rows]
    return {"items": items, "total": total, "page": page, "page_size": page_size}


# ---------- Mandats CRUD ----------
class MandatBase(BaseModel):
    model_config = ConfigDict(extra="ignore")
    avocat_id: str
    requerant: str = ""
    article: str = "486.3"
    date_ordonnance: Optional[str] = ""
    date_emission: Optional[str] = ""
    numero: str = ""
    groupe: str = "Pratique Privée"
    commentaire: Optional[str] = ""


class MandatUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    requerant: Optional[str] = None
    article: Optional[str] = None
    date_ordonnance: Optional[str] = None
    date_emission: Optional[str] = None
    numero: Optional[str] = None
    groupe: Optional[str] = None
    commentaire: Optional[str] = None


def _mandat_to_dict(m: Mandat) -> dict:
    return {
        "id": m.id, "avocat_id": m.avocat_id, "requerant": m.requerant or "",
        "article": m.article, "date_ordonnance": m.date_ordonnance or "",
        "date_emission": m.date_emission or "", "numero": m.numero or "",
        "groupe": m.groupe, "commentaire": m.commentaire or "",
        "created_at": m.created_at, "updated_at": m.updated_at,
        "usermodif": m.usermodif or "",
    }


@api_router.get("/mandats")
def list_mandats(user: dict = Depends(get_current_user),
                 db: Session = Depends(get_db),
                 avocat_id: Optional[str] = None,
                 article: Optional[str] = None,
                 date_debut: Optional[str] = None,
                 date_fin: Optional[str] = None):
    q = db.query(Mandat)
    if avocat_id: q = q.filter(Mandat.avocat_id == avocat_id)
    if article: q = q.filter(Mandat.article == article)
    if date_debut and date_fin:
        q = q.filter(Mandat.date_ordonnance >= date_debut, Mandat.date_ordonnance <= date_fin)
    rows = q.order_by(desc(Mandat.date_ordonnance)).limit(2000).all()
    return [_mandat_to_dict(m) for m in rows]


@api_router.post("/mandats", status_code=201)
def create_mandat(payload: MandatBase, user: dict = Depends(require_role("admin", "editeur")),
                  db: Session = Depends(get_db)):
    if not db.query(Avocat).filter_by(id=payload.avocat_id).first():
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    now = now_iso()
    m = Mandat(id=str(uuid.uuid4()), avocat_id=payload.avocat_id,
               requerant=payload.requerant, article=payload.article,
               date_ordonnance=payload.date_ordonnance or "",
               date_emission=payload.date_emission or "",
               numero=payload.numero, groupe=payload.groupe,
               commentaire=payload.commentaire or "",
               usermodif=user.get("email", ""), created_at=now, updated_at=now)
    db.add(m)
    db.commit()
    db.refresh(m)
    return _mandat_to_dict(m)


@api_router.put("/mandats/{mandat_id}")
def update_mandat(mandat_id: str, payload: MandatUpdate,
                  user: dict = Depends(require_role("admin", "editeur")),
                  db: Session = Depends(get_db)):
    m = db.query(Mandat).filter_by(id=mandat_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Mandat introuvable")
    for k, v in payload.model_dump(exclude_unset=True).items():
        if v is not None:
            setattr(m, k, v)
    m.updated_at = now_iso()
    db.commit()
    return {"ok": True}


@api_router.delete("/mandats/{mandat_id}")
def delete_mandat(mandat_id: str, user: dict = Depends(require_role("admin")),
                  db: Session = Depends(get_db)):
    m = db.query(Mandat).filter_by(id=mandat_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Mandat introuvable")
    db.delete(m)
    db.commit()
    return {"ok": True}


# ---------- Rapports PDF ----------
from pdf_reports import (  # noqa: E402
    build_registre97, build_registre98, build_liste_det_bar,
    build_liste_det_dist, build_liste_det_reg, build_liste_som,
)


def _avo_for_mandat(db: Session, avocat_id: str) -> dict:
    a = db.query(Avocat).filter_by(id=avocat_id).first()
    if not a:
        return {}
    return {"code": a.code or "", "nom": a.nom, "prenom": a.prenom, "type_code": a.type_code or "P"}


@api_router.get("/rapports/registre97")
def rapport_registre97(date_debut: str, date_fin: str,
                       user: dict = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    rows = (db.query(Mandat).filter(Mandat.date_ordonnance >= date_debut,
                                     Mandat.date_ordonnance <= date_fin).all())
    avo_cache: dict[str, dict] = {}
    rows_par_article: dict[str, list[dict]] = {}
    for m in rows:
        if m.avocat_id not in avo_cache:
            avo_cache[m.avocat_id] = _avo_for_mandat(db, m.avocat_id)
        a = avo_cache[m.avocat_id]
        d = _mandat_to_dict(m)
        d["avocat_nom"] = f"{a.get('code','')}  {a.get('nom','')}, {a.get('prenom','')}".strip() if a else "—"
        d["avocat_type"] = a.get("type_code", "P") if a else "P"
        rows_par_article.setdefault(d.get("article", "486.3"), []).append(d)
    pdf = build_registre97(date_debut, date_fin, rows_par_article)
    return StreamingResponse(iter([pdf]), media_type="application/pdf",
                             headers={"Content-Disposition": f'attachment; filename="registre97_{date_debut}_{date_fin}.pdf"'})


@api_router.get("/rapports/registre98")
def rapport_registre98(date_debut: str, date_fin: str,
                       user: dict = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    rows = (db.query(Mandat).filter(Mandat.date_ordonnance >= date_debut,
                                     Mandat.date_ordonnance <= date_fin).all())
    avo_cache: dict[str, dict] = {}
    rows_par_article: dict[str, list[dict]] = {}
    for m in rows:
        if m.avocat_id not in avo_cache:
            avo_cache[m.avocat_id] = _avo_for_mandat(db, m.avocat_id)
        a = avo_cache[m.avocat_id]
        d = _mandat_to_dict(m)
        d["avocat_code"] = a.get("code", "") if a else ""
        d["avocat_nom"] = f"{a.get('nom','')}, {a.get('prenom','')}" if a else ""
        rows_par_article.setdefault(d.get("article", "486.3"), []).append(d)
    pdf = build_registre98(date_debut, date_fin, rows_par_article)
    return StreamingResponse(iter([pdf]), media_type="application/pdf",
                             headers={"Content-Disposition": f'attachment; filename="registre98_{date_debut}_{date_fin}.pdf"'})


def _avocats_actifs_with_mega(db: Session) -> list[dict]:
    avos = (db.query(Avocat).filter(Avocat.actif.is_(True), Avocat.id.isnot(None))
              .order_by(asc(Avocat.nom), asc(Avocat.prenom)).all())
    if not avos:
        return []
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


@api_router.get("/rapports/liste-det-bar")
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


@api_router.get("/rapports/liste-det-dist")
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


@api_router.get("/rapports/liste-det-reg")
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


@api_router.get("/rapports/liste-som")
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


@api_router.get("/")
def root():
    return {"app": "GestionCardex", "version": "2.0.0", "backend": "SQLAlchemy/SQLite"}


# ---------- App wiring ----------
app.include_router(api_router)

frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Initialise tables (idempotent), seed admin/TI/connexions."""
    Base.metadata.create_all(bind=engine)

    db = next(get_db())
    try:
        # ----- Seed admin -----
        admin_email = os.environ.get("ADMIN_EMAIL", "admin@gestioncardex.qc").lower()
        admin_password = os.environ.get("ADMIN_PASSWORD", "Admin2026!")
        existing = db.query(AppUser).filter_by(email=admin_email).first()
        if not existing:
            db.add(AppUser(id=str(uuid.uuid4()), email=admin_email,
                           password_hash=hash_password(admin_password),
                           name="Administrateur", role="admin", created_at=now_iso()))
            db.commit()
            logger.info(f"Admin créé: {admin_email}")
        elif not verify_password(admin_password, existing.password_hash):
            existing.password_hash = hash_password(admin_password)
            db.commit()
            logger.info(f"Mot de passe admin mis à jour: {admin_email}")

        # ----- Seed TI -----
        ti_email = os.environ.get("TI_EMAIL", "ti@gestioncardex.qc").lower()
        ti_password = os.environ.get("TI_PASSWORD", "Ti2026!")
        ti_existing = db.query(AppUser).filter_by(email=ti_email).first()
        if not ti_existing:
            db.add(AppUser(id=str(uuid.uuid4()), email=ti_email,
                           password_hash=hash_password(ti_password),
                           name="Technicien TI", role="ti", created_at=now_iso()))
            db.commit()
            logger.info(f"Compte TI créé: {ti_email}")

        # ----- Seed connexions SQLite -----
        sqlite_seeds = [
            {"name": "CardAvo (SQLite local)", "file": "sqlite_dbs/CardAvo.db",
             "description": "Base principale de l'app — tables Avocats, Adresses, infomega, inhpra, Mandats, AppUsers, AuditLog, Connexions."},
            {"name": "StaticPc (SQLite local)", "file": "sqlite_dbs/StaticPc.db",
             "description": "Base de référence — 84 tables (codes, listes, paramètres)."},
            {"name": "Art52 (SQLite local)", "file": "sqlite_dbs/Art52.db",
             "description": "Base Article 52 — 126 tables (paiements et règlements)."},
        ]
        for s in sqlite_seeds:
            if not db.query(Connexion).filter_by(name=s["name"]).first():
                now = now_iso()
                db.add(Connexion(id=str(uuid.uuid4()), name=s["name"], type="sqlite",
                                 server="(fichier local)", port=None, user="",
                                 database=s["file"], description=s["description"],
                                 password_enc="", is_primary=(s["name"].startswith("CardAvo")),
                                 created_at=now, updated_at=now))
                db.commit()
                logger.info(f"SQLite seed: {s['name']}")

        # Nettoyage anciens enregistrements MongoDB / sCardAvo* qui pourraient persister
        old_names = ["MongoDB principal (en service)", "sCardAvo (SQLite local)",
                     "sStaticPc (SQLite local)", "sArt52 (SQLite local)"]
        for name in old_names:
            old = db.query(Connexion).filter_by(name=name).first()
            if old:
                db.delete(old)
        db.commit()
    finally:
        db.close()


# (pas de shutdown explicite : SQLAlchemy gère le pool tout seul)
