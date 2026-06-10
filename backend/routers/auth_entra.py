"""Routes d'authentification Microsoft Entra ID (Azure AD) — OAuth 2.0 / OIDC.

Flow :
1. GET /api/auth/entra/login  → redirige vers Microsoft
2. Microsoft → utilisateur s'authentifie
3. GET /api/auth/entra/callback → échange code↔token, valide ID token,
   mappe les App Roles (claim `roles`) sur les rôles locaux, crée/MAJ AppUser,
   pose les cookies JWT existants (réutilise set_auth_cookies), redirige vers le frontend.

Les App Roles doivent être définis dans l'App Registration Azure (valeurs :
`admin`, `editeur`, `lecteur`, `ti`) et assignés aux utilisateurs/groupes via
l'Enterprise Application.
"""
from __future__ import annotations

import os
import uuid
import logging

import msal
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from itsdangerous import URLSafeSerializer, BadSignature
from sqlalchemy.orm import Session

from database import get_db
from models import AppUser
from security import (
    create_access_token, create_refresh_token, ENTRA_SSO_HASH,
    now_local, set_auth_cookies,
)

logger = logging.getLogger("gestioncardex.entra")

router = APIRouter(prefix="/auth/entra", tags=["auth-entra"])

# ----- Configuration (lue depuis l'env, JAMAIS hardcodée) -----
TENANT_ID = os.environ.get("ENTRA_TENANT_ID", "")
CLIENT_ID = os.environ.get("ENTRA_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("ENTRA_CLIENT_SECRET", "")
REDIRECT_URI = os.environ.get("ENTRA_REDIRECT_URI", "")
POST_LOGIN_REDIRECT = os.environ.get(
    "ENTRA_POST_LOGIN_REDIRECT",
    os.environ.get("FRONTEND_URL", "http://localhost:3000"),
)

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}" if TENANT_ID else ""
# Scopes OIDC : on ne demande pas de token Graph, juste l'identité.
OIDC_SCOPES: list[str] = []  # MSAL ajoute automatiquement openid/profile/offline_access

# Cookie signé qui transporte le `auth_code_flow` MSAL (state + nonce) entre /login et /callback.
FLOW_COOKIE_NAME = "entra_auth_flow"
FLOW_COOKIE_MAX_AGE = 300  # 5 minutes
_flow_serializer_secret = os.environ.get("JWT_SECRET", "")  # réutilise le secret app
_flow_serializer = URLSafeSerializer(_flow_serializer_secret, salt="entra-auth-flow") if _flow_serializer_secret else None


def _msal_app() -> msal.ConfidentialClientApplication:
    """Construit (lazy) le client MSAL. Lève 503 si la config Entra ID manque."""
    if not (TENANT_ID and CLIENT_ID and CLIENT_SECRET and REDIRECT_URI):
        raise HTTPException(
            status_code=503,
            detail="Authentification Microsoft non configurée sur ce serveur.",
        )
    return msal.ConfidentialClientApplication(
        client_id=CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET,
    )


# ----- Mapping des App Roles Entra → rôles locaux -----
# Les App Roles sont définis dans l'App Registration. Les valeurs (claim `roles`)
# correspondent exactement aux rôles locaux ci-dessous.
ALLOWED_LOCAL_ROLES = {"admin", "editeur", "lecteur", "ti"}
# Priorité d'élection si l'utilisateur a plusieurs rôles (du plus puissant au moins).
ROLE_PRIORITY = ["ti", "admin", "editeur", "lecteur"]


def _select_local_role(roles_claim: list[str] | str | None) -> str | None:
    """Sélectionne LE rôle local effectif à partir du claim `roles` Entra.

    Retourne None si aucun rôle valide n'est trouvé → l'accès doit être refusé.
    """
    if not roles_claim:
        return None
    if isinstance(roles_claim, str):
        roles_claim = [roles_claim]
    roles_set = {r.lower() for r in roles_claim if isinstance(r, str)}
    for role in ROLE_PRIORITY:
        if role in roles_set:
            return role
    return None


# ============================================================
#                            ROUTES
# ============================================================
@router.get("/login")
def entra_login():
    """Démarre le flow OAuth : redirige le navigateur vers Microsoft."""
    app = _msal_app()
    if _flow_serializer is None:
        raise HTTPException(status_code=503, detail="JWT_SECRET non configuré.")

    flow = app.initiate_auth_code_flow(
        scopes=OIDC_SCOPES,
        redirect_uri=REDIRECT_URI,
    )
    if "auth_uri" not in flow:
        logger.error("MSAL initiate_auth_code_flow a échoué : %s", flow)
        raise HTTPException(status_code=500, detail="Impossible d'initier l'authentification Microsoft.")

    # On stocke tout le dict `flow` (state, nonce, code_verifier MSAL-side) dans un cookie signé.
    cookie_value = _flow_serializer.dumps(flow)

    response = RedirectResponse(url=flow["auth_uri"], status_code=302)
    # samesite=lax car la requête revient via GET depuis Microsoft → le cookie sera renvoyé.
    secure = os.environ.get("COOKIE_SECURE", "false").lower() == "true"
    response.set_cookie(
        key=FLOW_COOKIE_NAME, value=cookie_value,
        httponly=True, secure=secure, samesite="lax",
        max_age=FLOW_COOKIE_MAX_AGE, path="/api/auth/entra",
    )
    return response


@router.get("/callback")
def entra_callback(request: Request, db: Session = Depends(get_db)):
    """Reçoit le code OAuth de Microsoft, échange contre des tokens, log l'utilisateur."""
    app = _msal_app()
    if _flow_serializer is None:
        raise HTTPException(status_code=503, detail="JWT_SECRET non configuré.")

    # 1. Récupérer le flow signé depuis le cookie
    cookie_value = request.cookies.get(FLOW_COOKIE_NAME)
    if not cookie_value:
        # Cookie expiré ou navigation directe sur l'URL → erreur claire
        return _error_redirect("session_expired", "Session d'authentification expirée. Veuillez réessayer.")
    try:
        flow = _flow_serializer.loads(cookie_value)
    except BadSignature:
        return _error_redirect("invalid_state", "État d'authentification invalide.")

    # 2. Échange code ↔ tokens (MSAL valide automatiquement state + nonce)
    auth_response = dict(request.query_params)
    result = app.acquire_token_by_auth_code_flow(flow, auth_response)

    if "error" in result:
        logger.warning("Entra ID erreur token exchange: %s — %s",
                       result.get("error"), result.get("error_description"))
        return _error_redirect(result.get("error", "token_error"),
                               result.get("error_description") or "Échec de l'authentification.")

    claims = result.get("id_token_claims") or {}
    email = (claims.get("preferred_username") or claims.get("email") or "").lower()
    name = claims.get("name") or ""
    oid = claims.get("oid") or claims.get("sub") or ""
    tid = claims.get("tid") or ""

    if not email or not oid:
        return _error_redirect("missing_claims",
                               "Le compte Microsoft n'a pas fourni les informations requises.")

    # Sanity-check tenant (single-tenant strict)
    if TENANT_ID and tid and tid != TENANT_ID:
        return _error_redirect("invalid_tenant", "Compte Microsoft provenant d'un tenant non autorisé.")

    # 3. Mapper les App Roles
    roles_claim = claims.get("roles", [])
    local_role = _select_local_role(roles_claim)
    if not local_role:
        logger.warning("Utilisateur Entra %s sans App Role assigné (claims.roles=%s)", email, roles_claim)
        return _error_redirect(
            "no_role",
            f"Aucun rôle applicatif n'est assigné à {email}. Contactez l'administrateur.",
        )

    # 4. Upsert AppUser (par email)
    user = db.query(AppUser).filter_by(email=email).first()
    if user is None:
        user = AppUser(
            id=str(uuid.uuid4()),
            email=email,
            # Sentinel SSO : pas un bcrypt valide → login email/mdp impossible.
            # Détectable via `is_sso_user()` dans security.py.
            password_hash=ENTRA_SSO_HASH,
            name=name or email.split("@")[0],
            role=local_role,
            created_at=now_local(),
        )
        db.add(user)
        logger.info("Entra ID — Création AppUser : %s (role=%s)", email, local_role)
    else:
        # MAJ nom + rôle à chaque login (la source de vérité = Entra App Roles)
        if name and user.name != name:
            user.name = name
        if user.role != local_role:
            logger.info("Entra ID — MAJ rôle %s : %s → %s", email, user.role, local_role)
            user.role = local_role
        # Si un compte local existait déjà sous le même email, on le bascule
        # en compte SSO : le mdp local devient inutilisable pour cet utilisateur.
        if user.password_hash != ENTRA_SSO_HASH:
            logger.info("Entra ID — Conversion compte local → SSO pour %s", email)
            user.password_hash = ENTRA_SSO_HASH
    db.commit()
    db.refresh(user)

    # 5. Émettre les cookies JWT applicatifs (réutilise le flow existant)
    redirect = RedirectResponse(url=POST_LOGIN_REDIRECT, status_code=302)
    set_auth_cookies(
        redirect,
        create_access_token(user.id, user.email),
        create_refresh_token(user.id),
    )
    # Nettoyage du cookie de flow (déjà consommé)
    redirect.delete_cookie(FLOW_COOKIE_NAME, path="/api/auth/entra")
    return redirect


@router.get("/status")
def entra_status(user=Depends(lambda: None)):
    """Endpoint public — indique l'état de l'authentification côté serveur.

    Champs retournés :
      - `enabled` : True si Entra ID est configuré (variables ENTRA_* présentes)
      - `tenant_id` : tenant Entra (debug)
      - `local_login_enabled` : True si le formulaire courriel/mot de passe local
        est autorisé. False en prod Azure (variable DISABLE_LOCAL_LOGIN=true) où
        seule l'auth Microsoft doit être utilisée.
    """
    enabled = bool(TENANT_ID and CLIENT_ID and CLIENT_SECRET and REDIRECT_URI)
    local_disabled = os.environ.get("DISABLE_LOCAL_LOGIN", "").strip().lower() in ("1", "true", "yes")
    return {
        "enabled": enabled,
        "tenant_id": TENANT_ID if enabled else None,
        "local_login_enabled": not local_disabled,
    }


# ----- Helpers -----
def _error_redirect(code: str, message: str) -> RedirectResponse:
    """Redirige vers le frontend /login?entra_error=... avec un message lisible."""
    from urllib.parse import urlencode, urljoin
    base = POST_LOGIN_REDIRECT.rstrip("/")
    # On vise la route /login du frontend
    target = base + "/login?" + urlencode({"entra_error": code, "msg": message})
    return RedirectResponse(url=target, status_code=302)
