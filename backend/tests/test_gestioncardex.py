"""GestionCardex backend tests: auth + avocats CRUD"""
import os
import uuid
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://cardex-migrate.preview.emergentagent.com").rstrip("/")
ADMIN_EMAIL = "admin@gestioncardex.qc"
ADMIN_PASSWORD = "Admin2026!"


@pytest.fixture(scope="module")
def auth_session():
    s = requests.Session()
    r = s.post(f"{BASE_URL}/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=15)
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    assert "access_token" in s.cookies, "access_token cookie not set"
    assert "refresh_token" in s.cookies, "refresh_token cookie not set"
    return s


@pytest.fixture(scope="module")
def created_codes():
    codes = []
    yield codes
    s = requests.Session()
    s.post(f"{BASE_URL}/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=15)
    for c in codes:
        r = s.get(f"{BASE_URL}/api/avocats", params={"q": c}, timeout=15)
        if r.status_code == 200:
            for it in r.json().get("items", []):
                if it["code"] == c:
                    s.delete(f"{BASE_URL}/api/avocats/{it['id']}", timeout=15)


# ---------- Auth ----------
class TestAuth:
    def test_login_success(self, auth_session):
        r = auth_session.get(f"{BASE_URL}/api/auth/me", timeout=15)
        assert r.status_code == 200
        d = r.json()
        assert d["email"] == ADMIN_EMAIL
        assert d["role"] == "admin"

    def test_login_invalid(self):
        r = requests.post(f"{BASE_URL}/api/auth/login", json={"email": ADMIN_EMAIL, "password": "wrong"}, timeout=15)
        assert r.status_code == 401

    def test_me_without_cookie(self):
        r = requests.get(f"{BASE_URL}/api/auth/me", timeout=15)
        assert r.status_code == 401

    def test_logout_clears_cookies(self):
        s = requests.Session()
        s.post(f"{BASE_URL}/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=15)
        r = s.post(f"{BASE_URL}/api/auth/logout", timeout=15)
        assert r.status_code == 200
        # after logout cookies should be cleared - subsequent /me without cookies should 401
        s2 = requests.Session()
        r2 = s2.get(f"{BASE_URL}/api/auth/me", timeout=15)
        assert r2.status_code == 401


# ---------- Avocats Auth Required ----------
class TestAvocatsAuthRequired:
    def test_list_unauth(self):
        assert requests.get(f"{BASE_URL}/api/avocats", timeout=15).status_code == 401

    def test_stats_unauth(self):
        assert requests.get(f"{BASE_URL}/api/avocats/stats", timeout=15).status_code == 401

    def test_create_unauth(self):
        assert requests.post(f"{BASE_URL}/api/avocats", json={"code": "X", "nom": "N", "prenom": "P"}, timeout=15).status_code == 401


# ---------- Avocats CRUD ----------
class TestAvocatsCRUD:
    def test_create_get_update_delete(self, auth_session, created_codes):
        code = f"T{uuid.uuid4().hex[:6].upper()}"
        created_codes.append(code)
        payload = {"code": code, "nom": "Tremblay", "prenom": "Jean", "mega": True, "actif": True}
        r = auth_session.post(f"{BASE_URL}/api/avocats", json=payload, timeout=15)
        assert r.status_code == 201, r.text
        created = r.json()
        assert created["code"] == code
        assert created["nom"] == "Tremblay"
        assert created["mega"] is True
        avo_id = created["id"]

        # GET single
        rg = auth_session.get(f"{BASE_URL}/api/avocats/{avo_id}", timeout=15)
        assert rg.status_code == 200
        assert rg.json()["code"] == code

        # Duplicate code -> 409
        rd = auth_session.post(f"{BASE_URL}/api/avocats", json=payload, timeout=15)
        assert rd.status_code == 409

        # Update
        ru = auth_session.put(f"{BASE_URL}/api/avocats/{avo_id}", json={"nom": "Gagnon", "actif": False}, timeout=15)
        assert ru.status_code == 200
        assert ru.json()["nom"] == "Gagnon"
        assert ru.json()["actif"] is False

        # Verify persistence
        rg2 = auth_session.get(f"{BASE_URL}/api/avocats/{avo_id}", timeout=15)
        assert rg2.json()["nom"] == "Gagnon"

        # Delete
        rdl = auth_session.delete(f"{BASE_URL}/api/avocats/{avo_id}", timeout=15)
        assert rdl.status_code == 200
        # Verify gone
        rg3 = auth_session.get(f"{BASE_URL}/api/avocats/{avo_id}", timeout=15)
        assert rg3.status_code == 404

    def test_list_search_filter_pagination(self, auth_session, created_codes):
        # seed 2
        c1 = f"S{uuid.uuid4().hex[:6].upper()}"
        c2 = f"S{uuid.uuid4().hex[:6].upper()}"
        created_codes.extend([c1, c2])
        auth_session.post(f"{BASE_URL}/api/avocats", json={"code": c1, "nom": "Lavoie", "prenom": "Marie", "actif": True}, timeout=15)
        auth_session.post(f"{BASE_URL}/api/avocats", json={"code": c2, "nom": "Roy", "prenom": "Paul", "actif": False}, timeout=15)

        r = auth_session.get(f"{BASE_URL}/api/avocats", params={"q": "Lavoie"}, timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert any(it["nom"] == "Lavoie" for it in data["items"])

        r2 = auth_session.get(f"{BASE_URL}/api/avocats", params={"statut": "inactif"}, timeout=15)
        assert r2.status_code == 200
        for it in r2.json()["items"]:
            assert it["actif"] is False

        r3 = auth_session.get(f"{BASE_URL}/api/avocats", params={"page": 1, "page_size": 1}, timeout=15)
        assert r3.status_code == 200
        d3 = r3.json()
        assert d3["page"] == 1 and d3["page_size"] == 1
        assert len(d3["items"]) <= 1

    def test_stats(self, auth_session):
        r = auth_session.get(f"{BASE_URL}/api/avocats/stats", timeout=15)
        assert r.status_code == 200
        d = r.json()
        for k in ["total", "actifs", "inactifs", "mega", "nouveaux_30j"]:
            assert k in d and isinstance(d[k], int)
