from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

import os
import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional

import bcrypt
import jwt
from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends, Query
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, EmailStr, ConfigDict


# ---------- Setup ----------
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

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


def create_access_token(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=60 * 8),
    }
    return jwt.encode(payload, get_jwt_secret(), algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }
    return jwt.encode(payload, get_jwt_secret(), algorithm=JWT_ALGORITHM)


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    secure = os.environ.get("COOKIE_SECURE", "false").lower() == "true"
    response.set_cookie("access_token", access_token, httponly=True, secure=secure, samesite="lax",
                        max_age=60 * 60 * 8, path="/")
    response.set_cookie("refresh_token", refresh_token, httponly=True, secure=secure, samesite="lax",
                        max_age=60 * 60 * 24 * 7, path="/")


async def get_current_user(request: Request) -> dict:
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
        user = await db.users.find_one({"id": payload["sub"]}, {"_id": 0, "password_hash": 0})
        if not user:
            raise HTTPException(status_code=401, detail="Utilisateur introuvable")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Jeton expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Jeton invalide")


# ---------- Models ----------
class UserOut(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: str = "admin"


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str = Field(..., min_length=6)
    role: str = Field("editeur", pattern="^(admin|editeur|lecteur)$")


class UserUpdate(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = Field(None, pattern="^(admin|editeur|lecteur)$")


def require_role(*allowed_roles):
    async def checker(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role") not in allowed_roles:
            raise HTTPException(status_code=403, detail="Accès refusé")
        return user
    return checker


def funcValidNoAssSoc(no: str) -> bool:
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


async def _audit(avocat_id: str, action: str, user_email: str, summary: str) -> None:
    """Trace une modification d'avocat (ou entité enfant) dans audit_log.
    Best-effort : ne fait jamais échouer l'opération principale.
    Le timestamp est stocké en datetime BSON natif (tri/index plus robuste).
    """
    try:
        await db.audit_log.insert_one({
            "id": str(uuid.uuid4()),
            "avocat_id": avocat_id,
            "action": action,
            "user_email": user_email or "système",
            "summary": summary,
            "timestamp": datetime.now(timezone.utc),
        })
    except Exception as e:
        logger.warning(f"audit_log insert failed: {e}")


def _audit_to_out(doc: dict) -> dict:
    """Sérialise une entrée d'audit pour réponse HTTP (datetime → ISO)."""
    ts = doc.get("timestamp")
    if isinstance(ts, datetime):
        doc["timestamp"] = ts.isoformat()
    return doc


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class Adresse(BaseModel):
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
    code: str = Field(..., min_length=1, max_length=10)
    type_code: str = Field("A", description="A=Avocat permanent, P=Avocat privé, N=Notaire")
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
    adresse: Adresse = Field(default_factory=Adresse)


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
    adresse: Optional[Adresse] = None


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


# ---------- Auth Endpoints ----------
@api_router.post("/auth/login", response_model=UserOut)
async def login(payload: LoginIn, response: Response):
    email = payload.email.lower()
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Identifiants invalides")
    access = create_access_token(user["id"], user["email"])
    refresh = create_refresh_token(user["id"])
    set_auth_cookies(response, access, refresh)
    return UserOut(id=user["id"], email=user["email"], name=user.get("name", ""), role=user.get("role", "admin"))


@api_router.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return {"ok": True}


@api_router.get("/auth/me", response_model=UserOut)
async def me(user: dict = Depends(get_current_user)):
    return UserOut(id=user["id"], email=user["email"], name=user.get("name", ""), role=user.get("role", "admin"))


# ---------- Avocats Endpoints ----------
def _avocat_to_out(doc: dict) -> AvocatOut:
    doc.pop("_id", None)
    return AvocatOut(**doc)


@api_router.get("/avocats", response_model=AvocatsListOut)
async def list_avocats(
    user: dict = Depends(get_current_user),
    q: Optional[str] = Query(None, description="Recherche code/nom/prénom"),
    statut: Optional[str] = Query(None, description="actif|inactif|all"),
    mega: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
):
    query: dict = {}
    if q:
        regex = {"$regex": q, "$options": "i"}
        query["$or"] = [{"code": regex}, {"nom": regex}, {"prenom": regex}]
    if statut == "actif":
        query["actif"] = True
    elif statut == "inactif":
        query["actif"] = False
    if mega is not None:
        query["mega"] = mega

    total = await db.avocats.count_documents(query)
    cursor = db.avocats.find(query, {"_id": 0}).sort([("nom", 1), ("prenom", 1)]).skip((page - 1) * page_size).limit(page_size)
    items = [_avocat_to_out(doc) for doc in await cursor.to_list(length=page_size)]
    return AvocatsListOut(items=items, total=total, page=page, page_size=page_size)


@api_router.get("/avocats/next-code")
async def next_avocat_code(
    type: str = Query("A", pattern="^[ANP]$"),
    user: dict = Depends(get_current_user),
):
    """Génère le prochain code séquentiel selon le type (A/N/P)."""
    cursor = db.avocats.find(
        {"code": {"$regex": f"^{type}\\d+$"}},
        {"_id": 0, "code": 1},
    ).sort("code", -1).limit(1)
    docs = await cursor.to_list(length=1)
    next_num = 1
    if docs:
        try:
            next_num = int(docs[0]["code"][1:]) + 1
        except (ValueError, IndexError):
            next_num = 1
    return {"code": f"{type}{next_num:04d}"}


@api_router.get("/avocats/stats", response_model=StatsOut)
async def avocats_stats(user: dict = Depends(get_current_user)):
    total = await db.avocats.count_documents({})
    actifs = await db.avocats.count_documents({"actif": True})
    inactifs = await db.avocats.count_documents({"actif": False})
    mega = await db.avocats.count_documents({"mega": True})
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    nouveaux = await db.avocats.count_documents({"created_at": {"$gte": cutoff}})
    return StatsOut(total=total, actifs=actifs, inactifs=inactifs, mega=mega, nouveaux_30j=nouveaux)


@api_router.get("/avocats/{avocat_id}", response_model=AvocatOut)
async def get_avocat(avocat_id: str, user: dict = Depends(get_current_user)):
    doc = await db.avocats.find_one({"id": avocat_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    return _avocat_to_out(doc)


@api_router.post("/avocats", response_model=AvocatOut, status_code=201)
async def create_avocat(payload: AvocatCreate, user: dict = Depends(require_role("admin", "editeur"))):
    if payload.nas and not funcValidNoAssSoc(payload.nas):
        raise HTTPException(status_code=422, detail="Numéro NAS invalide (algorithme Luhn)")
    existing = await db.avocats.find_one({"code": payload.code})
    if existing:
        raise HTTPException(status_code=409, detail=f"Le code '{payload.code}' existe déjà")
    now = datetime.now(timezone.utc).isoformat()
    doc = payload.model_dump()
    doc.update({
        "id": str(uuid.uuid4()),
        "created_at": now,
        "updated_at": now,
        "usermodif": user.get("email", ""),
    })
    await db.avocats.insert_one(doc.copy())
    doc.pop("_id", None)
    await _audit(doc["id"], "create", user.get("email", ""),
                 f"Création de la fiche {doc.get('code','')} — {doc.get('nom','')}, {doc.get('prenom','')}")
    return AvocatOut(**doc)


@api_router.put("/avocats/{avocat_id}", response_model=AvocatOut)
async def update_avocat(avocat_id: str, payload: AvocatUpdate, user: dict = Depends(require_role("admin", "editeur"))):
    update_doc = {k: (v.model_dump() if hasattr(v, "model_dump") else v)
                  for k, v in payload.model_dump(exclude_unset=True).items()}
    if not update_doc:
        raise HTTPException(status_code=400, detail="Aucun champ à mettre à jour")
    update_doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    update_doc["usermodif"] = user.get("email", "")
    res = await db.avocats.update_one({"id": avocat_id}, {"$set": update_doc})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    doc = await db.avocats.find_one({"id": avocat_id}, {"_id": 0})
    # Résumé : champs modifiés (hors méta)
    changed = sorted(k for k in update_doc.keys() if k not in {"updated_at", "usermodif"})
    if changed:
        await _audit(avocat_id, "update", user.get("email", ""),
                     f"Modification : {', '.join(changed)}")
    return _avocat_to_out(doc)


@api_router.delete("/avocats/{avocat_id}")
async def delete_avocat(avocat_id: str, user: dict = Depends(require_role("admin"))):
    avo = await db.avocats.find_one({"id": avocat_id}, {"_id": 0, "code": 1, "nom": 1, "prenom": 1})
    await db.avocat_adresses.delete_many({"avocat_id": avocat_id})
    await db.avocat_mega.delete_one({"avocat_id": avocat_id})
    await db.avocat_inhab.delete_many({"avocat_id": avocat_id})
    res = await db.avocats.delete_one({"id": avocat_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    summary = f"Suppression de {avo.get('code','')} — {avo.get('nom','')}, {avo.get('prenom','')}" if avo else "Suppression"
    await _audit(avocat_id, "delete", user.get("email", ""), summary)
    return {"ok": True}


@api_router.get("/avocats/{avocat_id}/adresses")
async def list_adresses(avocat_id: str, user: dict = Depends(get_current_user)):
    docs = await db.avocat_adresses.find({"avocat_id": avocat_id}, {"_id": 0}).sort("created_at", -1).to_list(length=200)
    return docs


@api_router.post("/avocats/{avocat_id}/adresses", status_code=201)
async def create_adresse(avocat_id: str, payload: Adresse, courant: bool = False, user: dict = Depends(require_role("admin", "editeur"))):
    avo = await db.avocats.find_one({"id": avocat_id})
    if not avo:
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    now = datetime.now(timezone.utc).isoformat()
    doc = payload.model_dump()
    doc.update({"id": str(uuid.uuid4()), "avocat_id": avocat_id, "courant": courant, "created_at": now, "updated_at": now})
    if courant:
        await db.avocat_adresses.update_many({"avocat_id": avocat_id}, {"$set": {"courant": False}})
        await db.avocats.update_one({"id": avocat_id}, {"$set": {"adresse": payload.model_dump(), "updated_at": now}})
    await db.avocat_adresses.insert_one(doc.copy())
    doc.pop("_id", None)
    await _audit(avocat_id, "adresse_create", user.get("email", ""),
                 f"Adresse ajoutée : {payload.address or '?'}, {payload.ville or ''}".strip(", "))
    return doc


@api_router.put("/avocats/{avocat_id}/adresses/{adresse_id}")
async def update_adresse(avocat_id: str, adresse_id: str, payload: Adresse, courant: bool = False, user: dict = Depends(require_role("admin", "editeur"))):
    now = datetime.now(timezone.utc).isoformat()
    update = payload.model_dump()
    update.update({"courant": courant, "updated_at": now})
    if courant:
        await db.avocat_adresses.update_many({"avocat_id": avocat_id}, {"$set": {"courant": False}})
        await db.avocats.update_one({"id": avocat_id}, {"$set": {"adresse": payload.model_dump(), "updated_at": now}})
    res = await db.avocat_adresses.update_one({"id": adresse_id, "avocat_id": avocat_id}, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Adresse introuvable")
    await _audit(avocat_id, "adresse_update", user.get("email", ""),
                 f"Adresse modifiée : {payload.address or '?'}, {payload.ville or ''}".strip(", "))
    return {"ok": True}


@api_router.delete("/avocats/{avocat_id}/adresses/{adresse_id}")
async def delete_adresse(avocat_id: str, adresse_id: str, user: dict = Depends(require_role("admin", "editeur"))):
    adr = await db.avocat_adresses.find_one({"id": adresse_id, "avocat_id": avocat_id}, {"_id": 0})
    res = await db.avocat_adresses.delete_one({"id": adresse_id, "avocat_id": avocat_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Adresse introuvable")
    label = f"{(adr or {}).get('address','?')}, {(adr or {}).get('ville','')}" if adr else "—"
    await _audit(avocat_id, "adresse_delete", user.get("email", ""),
                 f"Adresse supprimée : {label}".strip(", "))
    return {"ok": True}


# ---------- Users CRUD (admin only) ----------
@api_router.get("/users")
async def list_users(user: dict = Depends(require_role("admin"))):
    docs = await db.users.find({}, {"_id": 0, "password_hash": 0}).to_list(length=500)
    return docs


@api_router.post("/users", status_code=201)
async def create_user(payload: UserCreate, user: dict = Depends(require_role("admin"))):
    email = payload.email.lower()
    if await db.users.find_one({"email": email}):
        raise HTTPException(status_code=409, detail="Courriel déjà utilisé")
    doc = {
        "id": str(uuid.uuid4()),
        "email": email,
        "name": payload.name,
        "role": payload.role,
        "password_hash": hash_password(payload.password),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.users.insert_one(doc.copy())
    return {"id": doc["id"], "email": email, "name": payload.name, "role": payload.role}


@api_router.put("/users/{user_id}")
async def update_user(user_id: str, payload: UserUpdate, user: dict = Depends(require_role("admin"))):
    update = {}
    if payload.name is not None:
        update["name"] = payload.name
    if payload.role is not None:
        update["role"] = payload.role
    if payload.password:
        update["password_hash"] = hash_password(payload.password)
    if not update:
        raise HTTPException(status_code=400, detail="Aucun champ à mettre à jour")
    res = await db.users.update_one({"id": user_id}, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return {"ok": True}


@api_router.delete("/users/{user_id}")
async def delete_user(user_id: str, user: dict = Depends(require_role("admin"))):
    if user_id == user["id"]:
        raise HTTPException(status_code=400, detail="Impossible de supprimer son propre compte")
    res = await db.users.delete_one({"id": user_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return {"ok": True}


class InfoMega(BaseModel):
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


class Inhabilite(BaseModel):
    model_config = ConfigDict(extra="ignore")
    datedeb: str
    datefin: Optional[str] = ""
    comm: Optional[str] = ""


class MandatBase(BaseModel):
    model_config = ConfigDict(extra="ignore")
    avocat_id: str
    requerant: str = ""
    article: str = "486.3"  # 486.3, 486.7, 672, 684
    date_ordonnance: Optional[str] = ""
    date_emission: Optional[str] = ""
    numero: str = ""
    groupe: str = "Pratique Privée"  # Pratique Privée | Permanent
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


@api_router.get("/avocats/{avocat_id}/mega")
async def get_mega(avocat_id: str, user: dict = Depends(get_current_user)):
    doc = await db.avocat_mega.find_one({"avocat_id": avocat_id}, {"_id": 0})
    return doc or {}


@api_router.put("/avocats/{avocat_id}/mega")
async def upsert_mega(avocat_id: str, payload: InfoMega, user: dict = Depends(require_role("admin", "editeur"))):
    avo = await db.avocats.find_one({"id": avocat_id})
    if not avo:
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    now = datetime.now(timezone.utc).isoformat()
    doc = payload.model_dump()
    doc.update({"avocat_id": avocat_id, "updated_at": now, "usermodif": user.get("email", "")})
    await db.avocat_mega.update_one(
        {"avocat_id": avocat_id},
        {"$set": doc, "$setOnInsert": {"id": str(uuid.uuid4()), "created_at": now}},
        upsert=True,
    )
    await db.avocats.update_one({"id": avocat_id}, {"$set": {"mega": True, "updated_at": now}})
    await _audit(avocat_id, "mega_update", user.get("email", ""),
                 f"Profil Méga mis à jour (sectbar={payload.sectbar or '—'}, exp={payload.experience or 0} an(s), districts={len(payload.districts or [])})")
    return {"ok": True}


@api_router.delete("/avocats/{avocat_id}/mega")
async def delete_mega(avocat_id: str, user: dict = Depends(require_role("admin", "editeur"))):
    await db.avocat_mega.delete_one({"avocat_id": avocat_id})
    await db.avocats.update_one({"id": avocat_id}, {"$set": {"mega": False}})
    await _audit(avocat_id, "mega_delete", user.get("email", ""), "Profil Méga supprimé")
    return {"ok": True}


@api_router.get("/avocats/{avocat_id}/inhabilites")
async def list_inhab(avocat_id: str, user: dict = Depends(get_current_user)):
    docs = await db.avocat_inhab.find({"avocat_id": avocat_id}, {"_id": 0}).sort("datedeb", -1).to_list(length=200)
    return docs


@api_router.post("/avocats/{avocat_id}/inhabilites", status_code=201)
async def create_inhab(avocat_id: str, payload: Inhabilite, user: dict = Depends(require_role("admin", "editeur"))):
    avo = await db.avocats.find_one({"id": avocat_id})
    if not avo:
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    now = datetime.now(timezone.utc).isoformat()
    doc = payload.model_dump()
    doc.update({"id": str(uuid.uuid4()), "avocat_id": avocat_id, "created_at": now, "updated_at": now})
    await db.avocat_inhab.insert_one(doc.copy())
    doc.pop("_id", None)
    await _audit(avocat_id, "inhab_create", user.get("email", ""),
                 f"Période d'inhabilité ajoutée : {payload.datedeb} → {payload.datefin or 'en cours'}")
    return doc


@api_router.put("/avocats/{avocat_id}/inhabilites/{inhab_id}")
async def update_inhab(avocat_id: str, inhab_id: str, payload: Inhabilite, user: dict = Depends(require_role("admin", "editeur"))):
    update = payload.model_dump()
    update["updated_at"] = datetime.now(timezone.utc).isoformat()
    res = await db.avocat_inhab.update_one({"id": inhab_id, "avocat_id": avocat_id}, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Période introuvable")
    await _audit(avocat_id, "inhab_update", user.get("email", ""),
                 f"Période d'inhabilité modifiée : {payload.datedeb} → {payload.datefin or 'en cours'}")
    return {"ok": True}


@api_router.delete("/avocats/{avocat_id}/inhabilites/{inhab_id}")
async def delete_inhab(avocat_id: str, inhab_id: str, user: dict = Depends(require_role("admin", "editeur"))):
    item = await db.avocat_inhab.find_one({"id": inhab_id, "avocat_id": avocat_id}, {"_id": 0})
    res = await db.avocat_inhab.delete_one({"id": inhab_id, "avocat_id": avocat_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Période introuvable")
    summary = (
        f"Période supprimée : {item.get('datedeb','?')} → {item.get('datefin','en cours')}"
        if item else "Période d'inhabilité supprimée"
    )
    await _audit(avocat_id, "inhab_delete", user.get("email", ""), summary)
    return {"ok": True}


@api_router.put("/avocats/{avocat_id}/web-password")
async def set_web_password(avocat_id: str, payload: dict, user: dict = Depends(require_role("admin", "editeur"))):
    pwd = (payload or {}).get("password", "")
    if len(pwd) < 6:
        raise HTTPException(status_code=400, detail="Mot de passe trop court (min 6)")
    avo = await db.avocats.find_one({"id": avocat_id})
    if not avo:
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    await db.avocats.update_one({"id": avocat_id}, {"$set": {"web_password_hash": hash_password(pwd), "updated_at": datetime.now(timezone.utc).isoformat()}})
    await _audit(avocat_id, "web_password_set", user.get("email", ""), "Mot de passe web défini")
    return {"ok": True}


@api_router.delete("/avocats/{avocat_id}/web-password")
async def clear_web_password(avocat_id: str, user: dict = Depends(require_role("admin", "editeur"))):
    await db.avocats.update_one({"id": avocat_id}, {"$unset": {"web_password_hash": ""}})
    await _audit(avocat_id, "web_password_clear", user.get("email", ""), "Mot de passe web réinitialisé")
    return {"ok": True}


# ---------- Audit log ----------
@api_router.get("/avocats/{avocat_id}/audit")
async def list_audit(
    avocat_id: str,
    user: dict = Depends(require_role("admin")),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """Retourne l'historique paginé des modifications pour un avocat (admin uniquement).
    Réponse : {items, total, page, page_size}.
    """
    skip = (page - 1) * page_size
    total = await db.audit_log.count_documents({"avocat_id": avocat_id})
    docs = await db.audit_log.find(
        {"avocat_id": avocat_id}, {"_id": 0}
    ).sort("timestamp", -1).skip(skip).limit(page_size).to_list(length=page_size)
    items = [_audit_to_out(d) for d in docs]
    return {"items": items, "total": total, "page": page, "page_size": page_size}


# ---------- Mandats CRUD ----------
@api_router.get("/mandats")
async def list_mandats(
    user: dict = Depends(get_current_user),
    avocat_id: Optional[str] = None,
    article: Optional[str] = None,
    date_debut: Optional[str] = None,
    date_fin: Optional[str] = None,
):
    q = {}
    if avocat_id: q["avocat_id"] = avocat_id
    if article: q["article"] = article
    if date_debut and date_fin:
        q["date_ordonnance"] = {"$gte": date_debut, "$lte": date_fin}
    docs = await db.mandats.find(q, {"_id": 0}).sort("date_ordonnance", -1).to_list(length=2000)
    return docs


@api_router.post("/mandats", status_code=201)
async def create_mandat(payload: MandatBase, user: dict = Depends(require_role("admin", "editeur"))):
    if not await db.avocats.find_one({"id": payload.avocat_id}):
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    now = datetime.now(timezone.utc).isoformat()
    doc = payload.model_dump()
    doc.update({"id": str(uuid.uuid4()), "created_at": now, "updated_at": now, "usermodif": user.get("email", "")})
    await db.mandats.insert_one(doc.copy())
    doc.pop("_id", None)
    return doc


@api_router.put("/mandats/{mandat_id}")
async def update_mandat(mandat_id: str, payload: MandatUpdate, user: dict = Depends(require_role("admin", "editeur"))):
    update = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    update["updated_at"] = datetime.now(timezone.utc).isoformat()
    res = await db.mandats.update_one({"id": mandat_id}, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Mandat introuvable")
    return {"ok": True}


@api_router.delete("/mandats/{mandat_id}")
async def delete_mandat(mandat_id: str, user: dict = Depends(require_role("admin"))):
    res = await db.mandats.delete_one({"id": mandat_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Mandat introuvable")
    return {"ok": True}


# ---------- Rapports PDF ----------
from pdf_reports import (
    build_registre97,
    build_registre98,
    build_liste_det_bar,
    build_liste_det_dist,
    build_liste_det_reg,
    build_liste_som,
)


@api_router.get("/rapports/registre97")
async def rapport_registre97(date_debut: str, date_fin: str, user: dict = Depends(get_current_user)):
    cursor = db.mandats.find({"date_ordonnance": {"$gte": date_debut, "$lte": date_fin}}, {"_id": 0})
    avo_cache: dict[str, dict] = {}
    rows_par_article: dict[str, list[dict]] = {}
    for m in await cursor.to_list(length=10000):
        if m["avocat_id"] not in avo_cache:
            a = await db.avocats.find_one({"id": m["avocat_id"]}, {"_id": 0, "nom": 1, "prenom": 1, "code": 1, "type_code": 1})
            avo_cache[m["avocat_id"]] = a or {}
        a = avo_cache[m["avocat_id"]]
        m["avocat_nom"] = f"{a.get('code','')}  {a.get('nom','')}, {a.get('prenom','')}".strip() if a else "—"
        m["avocat_type"] = a.get("type_code", "P") if a else "P"
        rows_par_article.setdefault(m.get("article", "486.3"), []).append(m)
    pdf = build_registre97(date_debut, date_fin, rows_par_article)
    return StreamingResponse(iter([pdf]), media_type="application/pdf",
                             headers={"Content-Disposition": f'attachment; filename="registre97_{date_debut}_{date_fin}.pdf"'})


@api_router.get("/rapports/registre98")
async def rapport_registre98(date_debut: str, date_fin: str, user: dict = Depends(get_current_user)):
    cursor = db.mandats.find({"date_ordonnance": {"$gte": date_debut, "$lte": date_fin}}, {"_id": 0})
    avo_cache: dict[str, dict] = {}
    rows_par_article: dict[str, list[dict]] = {}
    for m in await cursor.to_list(length=20000):
        if m["avocat_id"] not in avo_cache:
            a = await db.avocats.find_one({"id": m["avocat_id"]}, {"_id": 0, "nom": 1, "prenom": 1, "code": 1})
            avo_cache[m["avocat_id"]] = a or {}
        a = avo_cache[m["avocat_id"]]
        m["avocat_code"] = a.get("code", "") if a else ""
        m["avocat_nom"] = f"{a.get('nom','')}, {a.get('prenom','')}" if a else ""
        rows_par_article.setdefault(m.get("article", "486.3"), []).append(m)
    pdf = build_registre98(date_debut, date_fin, rows_par_article)
    return StreamingResponse(iter([pdf]), media_type="application/pdf",
                             headers={"Content-Disposition": f'attachment; filename="registre98_{date_debut}_{date_fin}.pdf"'})


async def _avocats_actifs_with_mega() -> list[dict]:
    """Charge les avocats actifs + leur fiche méga (jointure manuelle)."""
    avos = await db.avocats.find({"actif": True}, {"_id": 0}).sort([("nom", 1), ("prenom", 1)]).to_list(length=10000)
    if not avos:
        return []
    ids = [a["id"] for a in avos]
    megas = await db.avocat_mega.find({"avocat_id": {"$in": ids}}, {"_id": 0}).to_list(length=10000)
    by_id = {m["avocat_id"]: m for m in megas}
    for a in avos:
        a["_mega"] = by_id.get(a["id"]) or {}
    return avos


@api_router.get("/rapports/liste-det-bar")
async def rapport_liste_det_bar(user: dict = Depends(get_current_user)):
    avos = await _avocats_actifs_with_mega()
    groups: dict[str, list[dict]] = {}
    for a in avos:
        key = a.get("sectbar") or "(Sans section)"
        groups.setdefault(key, []).append(a)
    # Ordre alphabétique des sections
    groups = {k: groups[k] for k in sorted(groups.keys())}
    pdf = build_liste_det_bar(groups)
    return StreamingResponse(iter([pdf]), media_type="application/pdf",
                             headers={"Content-Disposition": 'attachment; filename="liste_det_bar.pdf"'})


@api_router.get("/rapports/liste-det-dist")
async def rapport_liste_det_dist(user: dict = Depends(get_current_user)):
    avos = await _avocats_actifs_with_mega()
    groups: dict[str, list[dict]] = {}
    for a in avos:
        ville = (a.get("adresse") or {}).get("ville") or "(Sans district)"
        groups.setdefault(ville, []).append(a)
    groups = {k: groups[k] for k in sorted(groups.keys())}
    pdf = build_liste_det_dist(groups)
    return StreamingResponse(iter([pdf]), media_type="application/pdf",
                             headers={"Content-Disposition": 'attachment; filename="liste_det_dist.pdf"'})


@api_router.get("/rapports/liste-det-reg")
async def rapport_liste_det_reg(user: dict = Depends(get_current_user)):
    # Regroupement par décennie d'inscription au barreau (équivalent VB legacy)
    avos = await db.avocats.find({}, {"_id": 0}).sort([("annee_barreau", 1), ("nom", 1)]).to_list(length=10000)
    ids = [a["id"] for a in avos]
    megas = await db.avocat_mega.find({"avocat_id": {"$in": ids}}, {"_id": 0}).to_list(length=10000)
    by_id = {m["avocat_id"]: m for m in megas}
    groups: dict[str, list[dict]] = {}
    for a in avos:
        a["_mega"] = by_id.get(a["id"]) or {}
        annee = a.get("annee_barreau") or ""
        if annee and str(annee).isdigit():
            decade = (int(annee) // 10) * 10
            key = f"Année barreau {decade}"
        else:
            key = "Année barreau (n.d.)"
        groups.setdefault(key, []).append(a)
    groups = {k: groups[k] for k in sorted(groups.keys())}
    pdf = build_liste_det_reg(groups)
    return StreamingResponse(iter([pdf]), media_type="application/pdf",
                             headers={"Content-Disposition": 'attachment; filename="liste_det_reg.pdf"'})


@api_router.get("/rapports/liste-som")
async def rapport_liste_som(date_debut: Optional[str] = None, date_fin: Optional[str] = None,
                            user: dict = Depends(get_current_user)):
    if not date_debut:
        date_debut = datetime.now().strftime("%Y-%m-01")
    if not date_fin:
        date_fin = datetime.now().strftime("%Y-%m-%d")
    avos = await _avocats_actifs_with_mega()
    pdf = build_liste_som(date_debut, date_fin, avos)
    return StreamingResponse(iter([pdf]), media_type="application/pdf",
                             headers={"Content-Disposition": 'attachment; filename="liste_som.pdf"'})


@api_router.get("/")
async def root():
    return {"app": "GestionCardex", "version": "1.0.0"}


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
async def on_startup():
    # Indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("id", unique=True)
    await db.avocats.create_index("code", unique=True)
    await db.avocats.create_index("id", unique=True)
    await db.avocats.create_index([("nom", 1), ("prenom", 1)])
    # Audit log : index composite pour requêtes par avocat triées par date
    await db.audit_log.create_index([("avocat_id", 1), ("timestamp", -1)])

    # Migration legacy — convertit les timestamps audit_log ISO string → datetime BSON natif
    legacy_count = await db.audit_log.count_documents({"timestamp": {"$type": "string"}})
    if legacy_count > 0:
        async for doc in db.audit_log.find({"timestamp": {"$type": "string"}}, {"id": 1, "timestamp": 1}):
            try:
                ts_str = doc["timestamp"].replace("Z", "+00:00")
                dt = datetime.fromisoformat(ts_str)
                await db.audit_log.update_one({"id": doc["id"]}, {"$set": {"timestamp": dt}})
            except Exception as e:
                logger.warning(f"audit_log migration skipped {doc.get('id')}: {e}")
        logger.info(f"audit_log: {legacy_count} timestamp(s) ISO string → datetime BSON natif")

    # Seed admin
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@gestioncardex.qc").lower()
    admin_password = os.environ.get("ADMIN_PASSWORD", "Admin2026!")
    existing = await db.users.find_one({"email": admin_email})
    if not existing:
        await db.users.insert_one({
            "id": str(uuid.uuid4()),
            "email": admin_email,
            "password_hash": hash_password(admin_password),
            "name": "Administrateur",
            "role": "admin",
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        logger.info(f"Admin créé: {admin_email}")
    elif not verify_password(admin_password, existing["password_hash"]):
        await db.users.update_one({"email": admin_email}, {"$set": {"password_hash": hash_password(admin_password)}})
        logger.info(f"Mot de passe admin mis à jour: {admin_email}")


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
