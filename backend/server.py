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
    response.set_cookie("access_token", access_token, httponly=True, secure=False, samesite="lax",
                        max_age=60 * 60 * 8, path="/")
    response.set_cookie("refresh_token", refresh_token, httponly=True, secure=False, samesite="lax",
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
    nom: str = Field(..., min_length=1, max_length=80)
    prenom: str = Field(..., min_length=1, max_length=80)
    sectbar: Optional[str] = ""
    mega: bool = False
    actif: bool = True
    dateinscbarr: Optional[str] = ""
    payable: bool = True
    codebar: Optional[str] = ""
    comm: Optional[str] = ""
    nas: Optional[str] = ""
    depodirect: bool = False
    factweb: bool = False
    confweb: bool = False
    villerref: Optional[str] = ""
    surveil: bool = False
    neq: Optional[str] = ""
    adresse: Adresse = Field(default_factory=Adresse)


class AvocatCreate(AvocatBase):
    pass


class AvocatUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    nom: Optional[str] = None
    prenom: Optional[str] = None
    sectbar: Optional[str] = None
    mega: Optional[bool] = None
    actif: Optional[bool] = None
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
async def create_avocat(payload: AvocatCreate, user: dict = Depends(get_current_user)):
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
    return AvocatOut(**doc)


@api_router.put("/avocats/{avocat_id}", response_model=AvocatOut)
async def update_avocat(avocat_id: str, payload: AvocatUpdate, user: dict = Depends(get_current_user)):
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
    return _avocat_to_out(doc)


@api_router.delete("/avocats/{avocat_id}")
async def delete_avocat(avocat_id: str, user: dict = Depends(get_current_user)):
    res = await db.avocats.delete_one({"id": avocat_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Avocat introuvable")
    return {"ok": True}


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
