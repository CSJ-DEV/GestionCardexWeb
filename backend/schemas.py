"""Schémas Pydantic partagés entre les routers."""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


def _coerce_db_values(values: Any) -> Any:
    """Convertit UUID/datetime/date renvoyés par pyodbc (SQL Server) en str."""
    if not isinstance(values, dict):
        # SQLAlchemy ORM instance → on transforme en dict via __dict__
        if hasattr(values, "__dict__"):
            values = {k: v for k, v in values.__dict__.items() if not k.startswith("_")}
        else:
            return values
    out = {}
    for k, v in values.items():
        if isinstance(v, UUID):
            out[k] = str(v)
        elif isinstance(v, datetime):
            out[k] = v.isoformat()
        elif isinstance(v, date):
            out[k] = v.isoformat()
        else:
            out[k] = v
    return out


# ---------- Users ----------
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: EmailStr
    name: str
    role: str = "admin"
    auth_provider: str = "local"

    @model_validator(mode="before")
    @classmethod
    def _coerce(cls, v):
        return _coerce_db_values(v)


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


class ChangePasswordIn(BaseModel):
    """Pour le changement de mot de passe par l'utilisateur lui-même."""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)


# ---------- Avocats ----------
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
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    id: str
    created_at: str
    updated_at: str
    usermodif: Optional[str] = ""
    # Indicateurs booléens (jamais les valeurs en clair) — utiles côté UI
    # pour afficher « défini » sans donner accès au mot de passe.
    motpasse1_set: bool = False
    motpasse2_set: bool = False

    @model_validator(mode="before")
    @classmethod
    def _coerce(cls, v):
        return _coerce_db_values(v)


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


# ---------- Méga + Inhab ----------
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


# ---------- Mandats ----------
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
