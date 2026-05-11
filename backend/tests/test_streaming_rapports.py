"""Tests régression streaming PDF (iteration 12).

Vérifie que le refactor StreamingResponse(chunk_bytes(...)) + yield_per(500) sur
les 6 endpoints /api/rapports/* n'a rien cassé :
  - Status 200 + signature %PDF-
  - Content-Length présent et égal à la taille du body téléchargé
  - Cache-Control: no-store
  - Auth requise (401 sans cookie)
  - Test de charge léger (100 avocats + 100 mandats) < 5s/rapport
  - Régression : aucune autre route /api/* impactée
"""
from __future__ import annotations

import os
import time
import uuid
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
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


# ---------- Fixtures auth ----------
@pytest.fixture(scope="module")
def auth_session():
    s = requests.Session()
    r = s.post(f"{BASE_URL}/api/auth/login",
               json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
               timeout=20)
    assert r.status_code == 200, f"Login failed: {r.status_code} {r.text}"
    assert "access_token" in s.cookies, "access_token cookie not set"
    return s


# ---------- Tests headers streaming ----------
@pytest.mark.parametrize("name,url", PDF_ENDPOINTS)
def test_pdf_unauthenticated_returns_401(name, url):
    """Sans cookie auth → 401 (régression : auth toujours requise)."""
    r = requests.get(f"{BASE_URL}{url}", timeout=20)
    assert r.status_code == 401, f"{name} expected 401 got {r.status_code}"


@pytest.mark.parametrize("name,url", PDF_ENDPOINTS)
def test_pdf_status_signature_and_streaming_headers(name, url, auth_session):
    """Status 200, %PDF-, Content-Length cohérent, Cache-Control no-store."""
    r = auth_session.get(f"{BASE_URL}{url}", timeout=60)
    assert r.status_code == 200, f"{name} status={r.status_code} body={r.text[:200]}"

    # Signature PDF
    assert r.content[:4] == b"%PDF", \
        f"{name} signature attendue b'%PDF' got {r.content[:20]!r}"

    # content-type
    ct = r.headers.get("content-type", "")
    assert ct.startswith("application/pdf"), f"{name} content-type={ct}"

    # Content-Length présent
    cl = r.headers.get("content-length")
    assert cl is not None, f"{name} : Content-Length manquant"
    assert int(cl) == len(r.content), \
        f"{name} : Content-Length={cl} != body size={len(r.content)}"

    # Cache-Control: no-store
    cc = r.headers.get("cache-control", "")
    assert "no-store" in cc.lower(), \
        f"{name} : Cache-Control sans no-store : '{cc}'"

    # Taille raisonnable
    assert len(r.content) > 1000, f"{name} PDF suspicieusement petit: {len(r.content)}"


# ---------- Test de charge léger ----------
@pytest.fixture(scope="module")
def bulk_data(auth_session):
    """Insère 100 avocats + 100 mandats (idempotent via prefix unique TEST_BULK_)."""
    s = auth_session
    run_id = uuid.uuid4().hex[:4].upper()
    created_avocats: list[str] = []
    created_mandats: list[str] = []

    for i in range(100):
        code = f"TB{run_id}{i:02d}"  # max 8 chars usually OK
        payload = {
            "code": code, "type_code": "P",
            "nom": f"TEST_BULK_{run_id}_{i:03d}",
            "prenom": "Charge",
            "sectbar": "Civil" if i % 2 == 0 else "Criminel",
            "annee_barreau": str(2000 + (i % 25)),
            "actif": True, "mega": False,
            "adresse": {"address": f"{i} rue Charge", "ville": "Montréal",
                        "province": "QC", "codepostal": "H1A1A1",
                        "telephone": "514-555-0000", "email": f"tb{i}@x.qc"},
        }
        r = s.post(f"{BASE_URL}/api/avocats", json=payload, timeout=20)
        if r.status_code == 201:
            avo = r.json()
            created_avocats.append(avo["id"])
            # Mandat associé pour registre97/98
            rm = s.post(f"{BASE_URL}/api/mandats", json={
                "avocat_id": avo["id"], "requerant": f"Requerant_{i}",
                "article": "486.3" if i % 2 == 0 else "486.5",
                "date_ordonnance": "2025-06-15",
                "date_emission": "2025-06-20",
                "numero": f"M-BULK-{run_id}-{i:03d}",
                "groupe": "Pratique Privée",
            }, timeout=20)
            if rm.status_code == 201:
                created_mandats.append(rm.json().get("id"))

    yield {"avocats": created_avocats, "mandats": created_mandats, "run_id": run_id}

    # ---- Cleanup ----
    for mid in created_mandats:
        if mid:
            try:
                s.delete(f"{BASE_URL}/api/mandats/{mid}", timeout=20)
            except Exception:
                pass
    for aid in created_avocats:
        try:
            s.delete(f"{BASE_URL}/api/avocats/{aid}", timeout=20)
        except Exception:
            pass


@pytest.mark.parametrize("name,url", PDF_ENDPOINTS)
def test_pdf_charge_legere_under_5s(name, url, auth_session, bulk_data):
    """Avec 100 avocats + 100 mandats, chaque rapport < 5s."""
    t0 = time.perf_counter()
    r = auth_session.get(f"{BASE_URL}{url}", timeout=30)
    elapsed = time.perf_counter() - t0
    assert r.status_code == 200, f"{name} status={r.status_code}"
    assert r.content[:4] == b"%PDF", f"{name} signature cassée sous charge"
    assert elapsed < 5.0, f"{name} trop lent : {elapsed:.2f}s"
    print(f"[BULK] {name} = {elapsed:.2f}s / {len(r.content)} bytes")


# ---------- Régression non-rapports ----------
def test_login_still_works():
    s = requests.Session()
    r = s.post(f"{BASE_URL}/api/auth/login",
               json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=20)
    assert r.status_code == 200
    assert "access_token" in s.cookies


def test_auth_me_works(auth_session):
    r = auth_session.get(f"{BASE_URL}/api/auth/me", timeout=20)
    assert r.status_code == 200
    assert r.json()["email"] == ADMIN_EMAIL


def test_avocats_list(auth_session):
    r = auth_session.get(f"{BASE_URL}/api/avocats?page=1&page_size=10", timeout=20)
    assert r.status_code == 200
    body = r.json()
    assert "items" in body
    assert isinstance(body["items"], list)


def test_avocats_stats(auth_session):
    r = auth_session.get(f"{BASE_URL}/api/avocats/stats", timeout=20)
    assert r.status_code == 200


def test_avocats_crud_roundtrip(auth_session):
    s = auth_session
    code = f"TR{uuid.uuid4().hex[:4].upper()}"
    payload = {"code": code, "type_code": "P",
               "nom": f"TEST_REG_{code}", "prenom": "Roundtrip",
               "sectbar": "Civil", "annee_barreau": "2020",
               "actif": True, "mega": False,
               "adresse": {"address": "1 rue Test", "ville": "Montréal",
                           "province": "QC", "codepostal": "H1A1A1",
                           "telephone": "514-555-0000", "email": "rt@x.qc"}}
    rc = s.post(f"{BASE_URL}/api/avocats", json=payload, timeout=20)
    assert rc.status_code == 201, rc.text
    aid = rc.json()["id"]

    rg = s.get(f"{BASE_URL}/api/avocats/{aid}", timeout=20)
    assert rg.status_code == 200
    assert rg.json()["nom"] == payload["nom"]

    rp = s.put(f"{BASE_URL}/api/avocats/{aid}",
               json={**payload, "prenom": "Updated"}, timeout=20)
    assert rp.status_code == 200
    assert rp.json()["prenom"] == "Updated"

    rd = s.delete(f"{BASE_URL}/api/avocats/{aid}", timeout=20)
    assert rd.status_code in (200, 204)

    r404 = s.get(f"{BASE_URL}/api/avocats/{aid}", timeout=20)
    assert r404.status_code == 404


def test_users_list(auth_session):
    r = auth_session.get(f"{BASE_URL}/api/users", timeout=20)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_connexions_list(auth_session):
    r = auth_session.get(f"{BASE_URL}/api/connexions?page=1&page_size=10", timeout=20)
    assert r.status_code == 200


def test_change_password_rejects_wrong_current(auth_session):
    r = auth_session.put(f"{BASE_URL}/api/auth/change-password",
                         json={"current_password": "WRONG_PWD!!", "new_password": "Whatever123!"},
                         timeout=20)
    assert r.status_code in (400, 401), f"got {r.status_code}"


def test_change_password_rejects_same(auth_session):
    r = auth_session.put(f"{BASE_URL}/api/auth/change-password",
                         json={"current_password": ADMIN_PASSWORD,
                               "new_password": ADMIN_PASSWORD},
                         timeout=20)
    assert r.status_code == 400
