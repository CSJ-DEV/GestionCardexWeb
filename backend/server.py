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

from database import engine, get_db, Base, DATABASE_URL
from models import AppUser, Avocat, Connexion, bool_to_yn
from security import hash_password, now_local, verify_password

# Routers
from routers.auth import router as auth_router
from routers.auth_entra import router as auth_entra_router
from routers.avocats import router as avocats_router
from routers.adresses import router as adresses_router
from routers.mega_inhab import router as mega_inhab_router, audit_router
from routers.mandats import router as mandats_router
from routers.rapports import router as rapports_router
from routers.users import router as users_router
from routers.connexions import router as connexions_router
from routers.system import router as system_router


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("gestioncardex")

app = FastAPI(title="GestionCardex API", version="2.1.0")
api_router = APIRouter(prefix="/api")


@api_router.get("/")
def root():
    return {"app": "GestionCardex", "version": "2.1.0", "backend": "SQLAlchemy/SQLite"}


# Inclusion de tous les routers métier
for r in (auth_router, auth_entra_router, avocats_router, adresses_router, mega_inhab_router, audit_router,
          mandats_router, rapports_router, users_router, connexions_router, system_router):
    api_router.include_router(r)

app.include_router(api_router)

# CORS
# - FRONTEND_URL : domaine principal (Azure Static Web Apps en prod)
# - localhost : développement local
# - allow_origin_regex : autorise les tunnels VS Code (*.devtunnels.ms)
#   et GitHub Codespaces (*.app.github.dev) pour les démos / tests distants
frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:3000"],
    allow_origin_regex=r"https://[a-z0-9-]+\.(devtunnels\.ms|app\.github\.dev|ngrok-free\.app|ngrok\.io|loca\.lt)",
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
        is_dev = DATABASE_URL.startswith("sqlite")

        # ----- Migration idempotente : colonne AppUsers.auth_provider -----
        # Ajoutée pour distinguer comptes locaux (email/mdp) vs Microsoft Entra ID.
        # Idempotent sur SQLite (PRAGMA) et SQL Server (sys.columns).
        from sqlalchemy import text
        try:
            if is_dev:
                cols = [r[1] for r in db.execute(text("PRAGMA table_info('AppUsers')")).fetchall()]
                if "auth_provider" not in cols:
                    db.execute(text("ALTER TABLE AppUsers ADD COLUMN auth_provider VARCHAR(20) NOT NULL DEFAULT 'local'"))
                    db.commit()
                    logger.info("Migration: ajout AppUsers.auth_provider (SQLite)")
            else:
                exists = db.execute(text(
                    "SELECT 1 FROM sys.columns WHERE object_id=OBJECT_ID('AppUsers') AND name='auth_provider'"
                )).scalar()
                if not exists:
                    db.execute(text(
                        "ALTER TABLE AppUsers ADD auth_provider NVARCHAR(20) NOT NULL CONSTRAINT DF_AppUsers_auth_provider DEFAULT 'local'"
                    ))
                    db.commit()
                    logger.info("Migration: ajout AppUsers.auth_provider (SQL Server)")
        except Exception as e:
            db.rollback()
            logger.warning("Migration AppUsers.auth_provider échouée (peut-être déjà appliquée) : %s", e)

        # ----- Seed des comptes utilisateurs -----
        # En production (SQL Server), les comptes sont insérés par le DBA via
        # /app/memory/INIT_CARDAVO_PROD.sql. Le backend NE seed PAS automatiquement
        # pour éviter d'écraser un compte créé par le DBA avec un mot de passe
        # potentiellement modifié manuellement.
        if is_dev:
            # Seed admin
            admin_email = os.environ.get("ADMIN_EMAIL", "admin@gestioncardex.qc").lower()
            admin_password = os.environ.get("ADMIN_PASSWORD", "Admin2026!")
            existing = db.query(AppUser).filter_by(email=admin_email).first()
            if not existing:
                db.add(AppUser(id=str(uuid.uuid4()), email=admin_email,
                               password_hash=hash_password(admin_password),
                               name="Administrateur", role="admin", created_at=now_local()))
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
                               name="Technicien TI", role="ti", created_at=now_local()))
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
                                   name=name, role=role, created_at=now_local()))
                    db.commit()
                    logger.info(f"Compte de test créé: {email} ({role})")
        else:
            logger.info("Mode production (SQL Server) — pas de seed automatique des comptes.")
            # Sanity check : alerter le DBA si la table AppUsers est vide.
            if db.query(AppUser).count() == 0:
                logger.warning(
                    "⚠️ Aucun compte dans AppUsers en production. "
                    "Exécutez /app/memory/INIT_CARDAVO_PROD.sql sur la base CardAvo."
                )

        # Seed connexions — UNIQUEMENT en dev (SQLite local).
        # En production (SQL Server), les 3 connexions sont insérées par le DBA
        # via le script T-SQL /app/memory/INIT_CARDAVO_PROD.sql. Le backend ne
        # crée donc rien automatiquement pour ne pas polluer le catalogue.
        if is_dev:
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
                    now = now_local()
                    db.add(Connexion(id=str(uuid.uuid4()), name=s["name"], type="sqlite",
                                     server="(fichier local)", port=None, user="",
                                     database=s["file"], description=s["description"],
                                     password_enc="", is_primary=s["primary"],
                                     created_at=now, updated_at=now))
                    db.commit()
                    logger.info(f"SQLite seed: {s['name']}")

            # Nettoyage anciennes entrées (legacy MongoDB / nommage `s*`) — dev uniquement.
            for name in ["MongoDB principal (en service)", "sCardAvo (SQLite local)",
                         "sStaticPc (SQLite local)", "sArt52 (SQLite local)"]:
                old = db.query(Connexion).filter_by(name=name).first()
                if old:
                    db.delete(old)
            db.commit()

            # Seed des avocats de démo (uniquement si la table est vide).
            # Permet d'avoir un environnement dev fonctionnel après reset DB.
            if db.query(Avocat).count() == 0:
                now = now_local()
                demo_avocats = [
                    ("A00001", "Tremblay", "Marie",   "A", "O", "A", "2015", "514-555-1001"),
                    ("A00002", "Gagnon",   "Jean",    "A", "N", "A", "2010", "514-555-1002"),
                    ("A00003", "Roy",      "Sophie",  "A", "O", "A", "2018", "514-555-1003"),
                    ("P10101", "Bouchard", "Luc",     "P", "N", "A", "2008", "418-555-2001"),
                    ("N20001", "Lavoie",   "Nathalie","N", "N", "A", "2012", "450-555-3001"),
                ]
                for code, nom, prenom, tc, mega, actpass, annee, _tel in demo_avocats:
                    db.add(Avocat(
                        code=code, type_code=tc, nom=nom, prenom=prenom,
                        sectbar="Droit civil",
                        mega=mega, actpass=actpass, dateinscbarr=annee,
                        payable="O", codebar="", comm="Avocat de démo (dev seed)",
                        nas="", depodirect="N", factweb="N", confweb="N",
                        villeref="Montréal", surveil="N", neq="",
                        codeusager="", motpasse1="", motpasse2="",
                        created_at=now, updated_at=now, datemodif=now,
                        usermodif="seed@gestioncardex.qc",
                    ))
                db.commit()
                logger.info(f"Avocats de démo créés : {len(demo_avocats)} fiches.")
        else:
            logger.info("Mode production (SQL Server) — pas de seed automatique des connexions.")
            # Sanity check : alerter le DBA si la table Connexions est vide.
            if db.query(Connexion).count() == 0:
                logger.warning(
                    "⚠️ Aucune connexion dans Connexions en production. "
                    "Exécutez /app/memory/INIT_CARDAVO_PROD.sql sur la base CardAvo."
                )
    finally:
        db.close()
