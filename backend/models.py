"""Modèles SQLAlchemy mappés sur les tables legacy (CardAvo) + tables app web.

Convention :
- On préserve les noms de colonnes legacy (ex `dateinscbarr`, `actpass`, `adremail`)
  pour rester compatible avec le futur SQL Server.
- Les colonnes ajoutées par l'app web (`id`, `actif`, `attente`, `created_at`, etc.)
  sont documentées dans `/app/memory/TABLES_AJOUTEES_APP.md`.
- Les booléens sont stockés en INTEGER (0/1) pour SQLite ; on bascule à `BIT` côté
  SQL Server transparente via SQLAlchemy.
"""
from __future__ import annotations

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Numeric, Index,
)

from database import Base


# ============================================================
#                    TABLES LEGACY (CardAvo)
# ============================================================
class Avocat(Base):
    __tablename__ = "Avocats"
    # Legacy a `code` comme PK ; on conserve. `id` (UUID) est utilisé par l'app.
    code = Column(String(10), primary_key=True)
    id = Column(String(36), unique=True, index=True)  # UUID app
    type_code = Column(String(1), default="A", nullable=False)
    nom = Column(String(80), nullable=False)
    prenom = Column(String(80), nullable=False)
    sectbar = Column(String(100), default="")
    mega = Column(String(1), default="N")  # 'O'/'N' legacy
    actpass = Column(String(1), default="A")  # 'A'/'P' legacy (Actif/Passif)
    dateinscbarr = Column(String(10), default="")  # année d'inscription au barreau (ex: '2010')
    payable = Column(String(1), default="O")
    adrcour = Column(Integer)  # FK Adresses.noseq (adresse courante)
    adrnonpay = Column(Integer)
    codebar = Column(String(10), default="")
    comm = Column(String(500), default="")
    datemodif = Column(String(30))
    nas = Column(String(9), default="")
    depodirect = Column(String(1), default="N")
    codeusager = Column(String(20), default="")
    motpasse1 = Column(String(8))
    motpasse2 = Column(String(8))
    factweb = Column(String(1), default="N")
    confweb = Column(String(1), default="N")
    villeref = Column(String(40), default="")
    usermodif = Column(String(50), default="")
    surveil = Column(String(1), default="N")
    neq = Column(String(10), default="")

    # Colonnes app web (audit + extranet uniquement)
    web_password_hash = Column(String(100))
    created_at = Column(String(30))
    updated_at = Column(String(30))


class Adresse(Base):
    __tablename__ = "Adresses"
    # PK = RowId legacy (uniqueidentifier) — pas de doublon avec un nouveau `id`.
    RowId = Column(String(36), primary_key=True)
    code = Column(String(6), nullable=False)  # FK legacy → Avocats.code
    address = Column(String(100), default="")
    adresse2 = Column(String(30), default="")
    adresse3 = Column(String(30), default="")
    ville = Column(String(40), default="")
    province = Column(String(20), default="")
    codepostal = Column(String(7), default="")
    telephone = Column(String(15), default="")
    telephone2 = Column(String(15), default="")
    fax = Column(String(15), default="")
    adremail = Column(String(50), default="")  # courriel legacy (unique)
    noseq = Column(Integer)
    courant = Column(String(1), default="N")  # 'O'/'N'
    dateadr = Column(String(30))
    poste1 = Column(String(6))
    poste2 = Column(String(6))
    usermodif = Column(String(20))
    datemodif = Column(String(30))
    created_at = Column(String(30))
    updated_at = Column(String(30))


class InfoMega(Base):
    __tablename__ = "infomega"
    id = Column(String(36), primary_key=True)
    avocat_id = Column(String(36), index=True)
    code = Column(String(6))
    francais = Column(String(1), default="N")  # 'O'/'N' legacy
    anglais = Column(String(1), default="N")
    autres = Column(String(40), default="")
    experience = Column(Integer, default=0)
    details = Column(String(500), default="")
    mega = Column(String(1), default="O")
    tarification = Column(String(1), default="N")
    art486 = Column(String(1), default="N")
    art672 = Column(String(1), default="N")
    art684 = Column(String(1), default="N")
    districthab = Column(String(100), default="")
    commentaire = Column(String(5000), default="")
    dateinsc = Column(String(30))
    usermodif = Column(String(20), default="")
    datemodif = Column(String(30))
    sectbar = Column(String(100), default="")
    tous_districts = Column(Boolean, default=False)
    created_at = Column(String(30))
    updated_at = Column(String(30))


class InfoDistrict(Base):
    """Liens many-to-many : un avocat → plusieurs districts.
    Legacy : pas d'id, juste (code, nodist). On ajoute un PK composite.
    """
    __tablename__ = "infodistrict"
    code = Column(String(6), primary_key=True)
    nodist = Column(Integer, primary_key=True)


class Inhpra(Base):
    __tablename__ = "inhpra"
    # Legacy a `Id` INTEGER autoincrement, mais on utilise `uuid` côté app
    Id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), index=True)  # UUID app
    avocat_id = Column(String(36), index=True)
    code = Column(String(6))
    datedeb = Column(String(30))
    datefin = Column(String(30))
    comm = Column(Text)
    created_at = Column(String(30))
    updated_at = Column(String(30))


# ============================================================
#                  TABLES APP WEB (CardAvo)
# ============================================================
class AppUser(Base):
    __tablename__ = "AppUsers"
    id = Column(String(36), primary_key=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    password_hash = Column(String(100), nullable=False)
    name = Column(String(200))
    role = Column(String(20), nullable=False)
    created_at = Column(String(30), nullable=False)


class AuditLog(Base):
    __tablename__ = "AuditLog"
    id = Column(String(36), primary_key=True)
    avocat_id = Column(String(36), nullable=False, index=True)
    action = Column(String(40), nullable=False)
    user_email = Column(String(200), nullable=False)
    summary = Column(String(500))
    timestamp = Column(String(30), nullable=False, index=True)


class Connexion(Base):
    __tablename__ = "Connexions"
    id = Column(String(36), primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    type = Column(String(20), nullable=False)
    server = Column(String(200), nullable=False)
    port = Column(Integer)
    user = Column(String(100))
    database = Column(String(100))
    description = Column(Text)
    password_enc = Column(String(500))
    is_primary = Column(Boolean, default=False, nullable=False)
    created_at = Column(String(30), nullable=False)
    updated_at = Column(String(30), nullable=False)


class Mandat(Base):
    __tablename__ = "Mandats"
    id = Column(String(36), primary_key=True)
    avocat_id = Column(String(36), nullable=False, index=True)
    requerant = Column(String(200), default="")
    article = Column(String(20), default="486.3", nullable=False)
    date_ordonnance = Column(String(30), index=True)
    date_emission = Column(String(30))
    numero = Column(String(50), default="")
    groupe = Column(String(50), default="Pratique Privée", nullable=False)
    commentaire = Column(Text)
    usermodif = Column(String(50))
    created_at = Column(String(30), nullable=False)
    updated_at = Column(String(30), nullable=False)


# ============================================================
#                Helpers de conversion ↔ dict
# ============================================================
# Conversions legacy ↔ booléen pour les colonnes 'O'/'N'
def yn_to_bool(v) -> bool:
    if isinstance(v, bool):
        return v
    if v is None:
        return False
    return str(v).upper() in {"O", "Y", "1", "TRUE"}


def bool_to_yn(v) -> str:
    return "O" if v else "N"
