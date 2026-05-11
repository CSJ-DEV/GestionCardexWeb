"""GestionCardex API — orchestrateur FastAPI.

Le code métier est éclaté en routers/* + helpers (security.py, schemas.py, audit.py).
Stack : FastAPI + SQLAlchemy 2.0 / SQLite (CardAvo.db), portable vers SQL Server.
"""
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

import os
import uuid
import logging

from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware

from database import engine, get_db, Base
from models import AppUser, Connexion
from security import hash_password, now_iso, verify_password

# Routers
from routers.auth import router as auth_router
from routers.avocats import router as avocats_router
from routers.adresses import router as adresses_router
from routers.mega_inhab import router as mega_inhab_router, audit_router
from routers.mandats import router as mandats_router
from routers.rapports import router as rapports_router
from routers.users import router as users_router
from routers.connexions import router as connexions_router


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("gestioncardex")

app = FastAPI(title="GestionCardex API", version="2.1.0")
api_router = APIRouter(prefix="/api")


@api_router.get("/")
def root():
    return {"app": "GestionCardex", "version": "2.1.0", "backend": "SQLAlchemy/SQLite"}


# Inclusion de tous les routers métier
for r in (auth_router, avocats_router, adresses_router, mega_inhab_router, audit_router,
          mandats_router, rapports_router, users_router, connexions_router):
    api_router.include_router(r)

app.include_router(api_router)

# CORS
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
    """Initialise les tables (idempotent) + seed admin/TI/connexions."""
    Base.metadata.create_all(bind=engine)

    db = next(get_db())
    try:
        # Seed admin
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

        # Seed TI
        ti_email = os.environ.get("TI_EMAIL", "ti@gestioncardex.qc").lower()
        ti_password = os.environ.get("TI_PASSWORD", "Ti2026!")
        if not db.query(AppUser).filter_by(email=ti_email).first():
            db.add(AppUser(id=str(uuid.uuid4()), email=ti_email,
                           password_hash=hash_password(ti_password),
                           name="Technicien TI", role="ti", created_at=now_iso()))
            db.commit()
            logger.info(f"Compte TI créé: {ti_email}")

        # Seed comptes de test (éditeur + lecteur) — idempotent
        for email, name, role, pwd in [
            ("editeur@gestioncardex.qc", "Éditeur", "editeur", "Editeur2026!"),
            ("lecteur@gestioncardex.qc", "Lecteur", "lecteur", "Lecteur2026!"),
        ]:
            if not db.query(AppUser).filter_by(email=email).first():
                db.add(AppUser(id=str(uuid.uuid4()), email=email,
                               password_hash=hash_password(pwd),
                               name=name, role=role, created_at=now_iso()))
                db.commit()
                logger.info(f"Compte de test créé: {email} ({role})")

        # Seed connexions SQLite
        sqlite_seeds = [
            {"name": "CardAvo (SQLite local)", "file": "sqlite_dbs/CardAvo.db", "primary": True,
             "description": "Base principale de l'app — tables Avocats, Adresses, infomega, inhpra, Mandats, AppUsers, AuditLog, Connexions."},
            {"name": "StaticPc (SQLite local)", "file": "sqlite_dbs/StaticPc.db", "primary": False,
             "description": "Base de référence — 84 tables (codes, listes, paramètres)."},
            {"name": "Art52 (SQLite local)", "file": "sqlite_dbs/Art52.db", "primary": False,
             "description": "Base Article 52 — 126 tables (paiements et règlements)."},
        ]
        for s in sqlite_seeds:
            if not db.query(Connexion).filter_by(name=s["name"]).first():
                now = now_iso()
                db.add(Connexion(id=str(uuid.uuid4()), name=s["name"], type="sqlite",
                                 server="(fichier local)", port=None, user="",
                                 database=s["file"], description=s["description"],
                                 password_enc="", is_primary=s["primary"],
                                 created_at=now, updated_at=now))
                db.commit()
                logger.info(f"SQLite seed: {s['name']}")

        # Nettoyage anciennes entrées (legacy MongoDB / nommage `s*`)
        for name in ["MongoDB principal (en service)", "sCardAvo (SQLite local)",
                     "sStaticPc (SQLite local)", "sArt52 (SQLite local)"]:
            old = db.query(Connexion).filter_by(name=name).first()
            if old:
                db.delete(old)
        db.commit()
    finally:
        db.close()
