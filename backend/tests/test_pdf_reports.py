"""Backend tests — 6 PDF reports rewritten to mimic Crystal Reports legacy formatting.
Validates: HTTP 200 with valid PDF (signature %PDF) when authenticated,
HTTP 401 when no authentication, and includes seed data so the PDFs are not empty.
"""
import os
import uuid
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://cardex-migrate.preview.emergentagent.com").rstrip("/")
ADMIN_EMAIL = "admin@gestioncardex.qc"
ADMIN_PASSWORD = "Admin2026!"

PDF_ENDPOINTS = [
    ("registre97", "/api/rapports/registre97?date_debut=2024-01-01&date_fin=2026-12-31"),
    ("registre98", "/api/rapports/registre98?date_debut=2024-01-01&date_fin=2026-12-31"),
    ("liste-det-bar", "/api/rapports/liste-det-bar"),
    ("liste-det-dist", "/api/rapports/liste-det-dist"),
    ("liste-det-reg", "/api/rapports/liste-det-reg"),
    ("liste-som", "/api/rapports/liste-som"),
]


@pytest.fixture(scope="module")
def auth_session():
    s = requests.Session()
    r = s.post(f"{BASE_URL}/api/auth/login",
               json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
               timeout=20)
    assert r.status_code == 200, f"Login failed: {r.status_code} {r.text}"
    assert "access_token" in s.cookies, "access_token cookie not set"
    return s


@pytest.fixture(scope="module")
def seed_data(auth_session):
    """Seed at least one avocat with mega + inhab + mandats so PDFs have content."""
    s = auth_session
    code = f"TST{str(uuid.uuid4())[:4].upper()}"
    payload = {
        "code": code, "type_code": "P", "nom": "TestPDF",
        "prenom": "Avocat", "sectbar": "Civil", "annee_barreau": "2015",
        "actif": True, "mega": False,
        "adresse": {"address": "100 rue Test", "ville": "Montréal",
                    "province": "QC", "codepostal": "H1A1A1",
                    "telephone": "514-555-1234", "email": "test@example.com"},
    }
    r = s.post(f"{BASE_URL}/api/avocats", json=payload, timeout=20)
    if r.status_code == 409:
        # already exists, look it up
        r = s.get(f"{BASE_URL}/api/avocats?q={code}", timeout=20).json()
        avo = r["items"][0]
    else:
        assert r.status_code == 201, r.text
        avo = r.json()
    avocat_id = avo["id"]

    # Mega
    s.put(f"{BASE_URL}/api/avocats/{avocat_id}/mega", json={
        "sectbar": "Civil", "francais": True, "anglais": True,
        "experience": 10, "districts": [1, 2], "tous_districts": False,
    }, timeout=20)

    # Inhabilité
    s.post(f"{BASE_URL}/api/avocats/{avocat_id}/inhabilites",
           json={"datedeb": "2025-01-01", "datefin": "2025-12-31", "comm": "test"},
           timeout=20)

    # Mandat (for registre97/98)
    s.post(f"{BASE_URL}/api/mandats", json={
        "avocat_id": avocat_id, "requerant": "Jean Dupont",
        "article": "486.3", "date_ordonnance": "2025-06-15",
        "date_emission": "2025-06-20", "numero": "M-001",
        "groupe": "Pratique Privée",
    }, timeout=20)
    return {"avocat_id": avocat_id, "code": code}


@pytest.mark.parametrize("name,url", PDF_ENDPOINTS)
def test_pdf_unauthenticated_returns_401(name, url):
    r = requests.get(f"{BASE_URL}{url}", timeout=20)
    assert r.status_code == 401, f"{name} expected 401, got {r.status_code}"


@pytest.mark.parametrize("name,url", PDF_ENDPOINTS)
def test_pdf_authenticated_returns_valid_pdf(name, url, auth_session, seed_data):
    r = auth_session.get(f"{BASE_URL}{url}", timeout=60)
    assert r.status_code == 200, f"{name} status={r.status_code} body={r.text[:200]}"
    assert r.headers.get("content-type", "").startswith("application/pdf"), \
        f"{name} content-type={r.headers.get('content-type')}"
    assert r.content[:4] == b"%PDF", f"{name} missing %PDF signature: {r.content[:20]!r}"
    # Reasonable size — header+footer alone exceed 1KB
    assert len(r.content) > 1000, f"{name} suspiciously small: {len(r.content)} bytes"


def test_auth_me_works(auth_session):
    r = auth_session.get(f"{BASE_URL}/api/auth/me", timeout=20)
    assert r.status_code == 200
    assert r.json()["email"] == ADMIN_EMAIL
