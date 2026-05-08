"""
Tests for SQLAlchemy/SQLite migration of GestionCardex backend.

Coverage:
- Auth: login, /me, refresh, cookies httpOnly
- Avocats: CRUD + sequential code generation (A/N/P) + Luhn NAS
- Avocats: filters (q, statut, mega), pagination, stats
- Adresses: create/update with courant=true, snapshot in adresse_courante
- Mega: upsert + GET booleans + districts replace
- Inhabilité: POST/PUT/DELETE using uuid (TEXT) not Id (INTEGER)
- Web password: PUT/DELETE
- Audit: paginated, chronological
- Mandats: full CRUD + filters
- Rapports PDF: 6 endpoints return %PDF
- Connexions: CRUD, primary read-only, test/download, role-based access
- Users CRUD: admin only
- Roles: editor cannot delete avocats, lecteur cannot modify
- Persistence: data survives backend restart
"""
import os
import time
import uuid
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://cardex-migrate.preview.emergentagent.com").rstrip("/")
ADMIN_EMAIL = "admin@gestioncardex.qc"
ADMIN_PASSWORD = "Admin2026!"
TI_EMAIL = "ti@gestioncardex.qc"
TI_PASSWORD = "Ti2026!"


# ---------- Fixtures ----------
def _login(email: str, password: str) -> requests.Session:
    s = requests.Session()
    r = s.post(f"{BASE_URL}/api/auth/login",
               json={"email": email, "password": password}, timeout=15)
    assert r.status_code == 200, f"login {email} failed: {r.status_code} {r.text}"
    return s


@pytest.fixture(scope="module")
def admin():
    return _login(ADMIN_EMAIL, ADMIN_PASSWORD)


@pytest.fixture(scope="module")
def ti():
    return _login(TI_EMAIL, TI_PASSWORD)


@pytest.fixture(scope="module")
def created_avocats():
    """Track avocat ids to clean up at end."""
    ids = []
    yield ids
    s = _login(ADMIN_EMAIL, ADMIN_PASSWORD)
    for aid in ids:
        try:
            s.delete(f"{BASE_URL}/api/avocats/{aid}", timeout=15)
        except Exception:
            pass


@pytest.fixture(scope="module")
def created_users():
    ids = []
    yield ids
    s = _login(ADMIN_EMAIL, ADMIN_PASSWORD)
    for uid in ids:
        try:
            s.delete(f"{BASE_URL}/api/users/{uid}", timeout=15)
        except Exception:
            pass


def _create_avocat(s, type_code="A", nom=None, prenom=None, mega=False, actif=True, nas=""):
    nom = nom or f"TST_{uuid.uuid4().hex[:6]}"
    prenom = prenom or "Test"
    payload = {"nom": nom, "prenom": prenom, "type_code": type_code,
               "mega": mega, "actif": actif, "nas": nas}
    r = s.post(f"{BASE_URL}/api/avocats", json=payload, timeout=15)
    return r


# ---------- Auth ----------
class TestAuth:
    def test_login_admin(self, admin):
        assert "access_token" in admin.cookies
        assert "refresh_token" in admin.cookies

    def test_login_ti(self, ti):
        assert "access_token" in ti.cookies
        r = ti.get(f"{BASE_URL}/api/auth/me", timeout=15)
        assert r.status_code == 200
        assert r.json()["role"] == "ti"

    def test_me_admin(self, admin):
        r = admin.get(f"{BASE_URL}/api/auth/me", timeout=15)
        assert r.status_code == 200
        d = r.json()
        assert d["email"] == ADMIN_EMAIL
        assert d["role"] == "admin"

    def test_login_invalid(self):
        r = requests.post(f"{BASE_URL}/api/auth/login",
                          json={"email": ADMIN_EMAIL, "password": "wrong"}, timeout=15)
        assert r.status_code == 401

    def test_refresh_endpoint(self):
        s = _login(ADMIN_EMAIL, ADMIN_PASSWORD)
        # Force only refresh_token to be present by deleting access_token
        s.cookies.pop("access_token", None)
        r = s.post(f"{BASE_URL}/api/auth/refresh", timeout=15)
        assert r.status_code == 200, r.text
        assert "access_token" in s.cookies
        assert r.json()["email"] == ADMIN_EMAIL

    def test_cookie_httponly(self):
        # Verify Set-Cookie header has HttpOnly
        r = requests.post(f"{BASE_URL}/api/auth/login",
                          json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=15)
        assert r.status_code == 200
        cookies_hdr = r.headers.get("set-cookie", "")
        assert "HttpOnly" in cookies_hdr or "httponly" in cookies_hdr.lower()


# ---------- Avocats CRUD + code generation + Luhn ----------
class TestAvocatsCodeAndLuhn:
    def test_sequential_code_A(self, admin, created_avocats):
        r = _create_avocat(admin, type_code="A")
        assert r.status_code == 201, r.text
        d = r.json()
        assert d["code"].startswith("A") and len(d["code"]) == 6
        assert d["code"][1:].isdigit()
        created_avocats.append(d["id"])

    def test_sequential_code_P(self, admin, created_avocats):
        r = _create_avocat(admin, type_code="P")
        assert r.status_code == 201, r.text
        d = r.json()
        assert d["code"].startswith("P") and d["code"][1:].isdigit()
        created_avocats.append(d["id"])

    def test_sequential_code_N(self, admin, created_avocats):
        r = _create_avocat(admin, type_code="N")
        assert r.status_code == 201, r.text
        d = r.json()
        assert d["code"].startswith("N") and d["code"][1:].isdigit()
        created_avocats.append(d["id"])

    def test_invalid_nas_luhn(self, admin):
        # 123456789 fails Luhn
        r = _create_avocat(admin, nas="123456789")
        assert r.status_code == 422, r.text
        assert "NAS" in r.text or "Luhn" in r.text

    def test_valid_nas_luhn(self, admin, created_avocats):
        # 046454286 is a valid Luhn NAS
        r = _create_avocat(admin, nas="046454286")
        assert r.status_code == 201, r.text
        created_avocats.append(r.json()["id"])


# ---------- Avocats list/filter/stats ----------
class TestAvocatsList:
    def test_list_pagination(self, admin):
        r = admin.get(f"{BASE_URL}/api/avocats?page=1&page_size=5", timeout=15)
        assert r.status_code == 200
        d = r.json()
        assert d["page"] == 1 and d["page_size"] == 5
        assert isinstance(d["items"], list)
        assert isinstance(d["total"], int)

    def test_filter_actif(self, admin):
        r = admin.get(f"{BASE_URL}/api/avocats?statut=actif&page_size=10", timeout=15)
        assert r.status_code == 200
        for it in r.json()["items"]:
            assert it["actif"] is True

    def test_filter_inactif(self, admin, created_avocats):
        # Seed an inactive avocat
        r = _create_avocat(admin, actif=False)
        assert r.status_code == 201
        created_avocats.append(r.json()["id"])
        r2 = admin.get(f"{BASE_URL}/api/avocats?statut=inactif&page_size=10", timeout=15)
        assert r2.status_code == 200
        items = r2.json()["items"]
        assert all(it["actif"] is False for it in items)

    def test_filter_mega(self, admin, created_avocats):
        r = _create_avocat(admin, mega=True)
        assert r.status_code == 201
        created_avocats.append(r.json()["id"])
        r2 = admin.get(f"{BASE_URL}/api/avocats?mega=true&page_size=20", timeout=15)
        assert r2.status_code == 200
        for it in r2.json()["items"]:
            assert it["mega"] is True

    def test_search_q(self, admin, created_avocats):
        unique = f"Zzx{uuid.uuid4().hex[:5]}"
        r = _create_avocat(admin, nom=unique)
        assert r.status_code == 201
        created_avocats.append(r.json()["id"])
        r2 = admin.get(f"{BASE_URL}/api/avocats?q={unique}", timeout=15)
        assert r2.status_code == 200
        assert any(it["nom"] == unique for it in r2.json()["items"])

    def test_stats(self, admin):
        r = admin.get(f"{BASE_URL}/api/avocats/stats", timeout=15)
        assert r.status_code == 200
        d = r.json()
        for k in ("total", "actifs", "inactifs", "mega", "nouveaux_30j"):
            assert k in d and isinstance(d[k], int)


# ---------- Adresses ----------
class TestAdresses:
    def test_create_courant_updates_snapshot(self, admin, created_avocats):
        r = _create_avocat(admin)
        avo = r.json()
        avo_id = avo["id"]
        created_avocats.append(avo_id)

        adr = {"address": "123 rue Test", "ville": "Montréal",
               "province": "QC", "codepostal": "H1H 1H1", "email": "a@b.c"}
        r1 = admin.post(f"{BASE_URL}/api/avocats/{avo_id}/adresses?courant=true",
                        json=adr, timeout=15)
        assert r1.status_code == 201, r1.text
        adr1_id = r1.json()["id"]

        # Add second courant=true → first should become non-courant
        adr2 = {**adr, "address": "456 av. Autre"}
        r2 = admin.post(f"{BASE_URL}/api/avocats/{avo_id}/adresses?courant=true",
                        json=adr2, timeout=15)
        assert r2.status_code == 201

        # List should show only one current
        rl = admin.get(f"{BASE_URL}/api/avocats/{avo_id}/adresses", timeout=15)
        assert rl.status_code == 200
        currents = [a for a in rl.json() if a["courant"]]
        assert len(currents) == 1, f"Expected 1 current, got {len(currents)}"
        assert currents[0]["address"] == "456 av. Autre"

        # Avocat snapshot must be updated
        ra = admin.get(f"{BASE_URL}/api/avocats/{avo_id}", timeout=15)
        assert ra.status_code == 200
        snap = ra.json().get("adresse") or {}
        assert snap.get("address") == "456 av. Autre"

        # PUT first one back as courant
        ru = admin.put(f"{BASE_URL}/api/avocats/{avo_id}/adresses/{adr1_id}?courant=true",
                       json=adr, timeout=15)
        assert ru.status_code == 200, ru.text

        rl2 = admin.get(f"{BASE_URL}/api/avocats/{avo_id}/adresses", timeout=15)
        currents2 = [a for a in rl2.json() if a["courant"]]
        assert len(currents2) == 1
        assert currents2[0]["address"] == "123 rue Test"

        # DELETE adresse
        rd = admin.delete(f"{BASE_URL}/api/avocats/{avo_id}/adresses/{adr1_id}", timeout=15)
        assert rd.status_code == 200


# ---------- Méga ----------
class TestMega:
    def test_mega_upsert_and_districts_replace(self, admin, created_avocats):
        r = _create_avocat(admin)
        avo_id = r.json()["id"]
        created_avocats.append(avo_id)

        payload = {
            "sectbar": "MTL", "francais": True, "anglais": True,
            "art486": True, "art672": False, "art684": True,
            "experience": 10, "details": "test",
            "districts": [1, 5, 10], "tous_districts": False,
        }
        r1 = admin.put(f"{BASE_URL}/api/avocats/{avo_id}/mega", json=payload, timeout=15)
        assert r1.status_code == 200, r1.text

        # GET — booleans converted from O/N
        rg = admin.get(f"{BASE_URL}/api/avocats/{avo_id}/mega", timeout=15)
        assert rg.status_code == 200
        d = rg.json()
        assert d["francais"] is True
        assert d["anglais"] is True
        assert d["art486"] is True
        assert d["art672"] is False
        assert d["art684"] is True
        assert sorted(d["districts"]) == [1, 5, 10]
        assert all(isinstance(x, int) for x in d["districts"])

        # Re-PUT with different districts → must REPLACE not append
        payload2 = {**payload, "districts": [2, 7]}
        r2 = admin.put(f"{BASE_URL}/api/avocats/{avo_id}/mega", json=payload2, timeout=15)
        assert r2.status_code == 200
        rg2 = admin.get(f"{BASE_URL}/api/avocats/{avo_id}/mega", timeout=15)
        assert sorted(rg2.json()["districts"]) == [2, 7]


# ---------- Inhabilité (uuid not Id) ----------
class TestInhabilite:
    def test_inhab_crud_uses_uuid(self, admin, created_avocats):
        r = _create_avocat(admin)
        avo_id = r.json()["id"]
        created_avocats.append(avo_id)

        rc = admin.post(f"{BASE_URL}/api/avocats/{avo_id}/inhabilites",
                        json={"datedeb": "2025-01-01", "datefin": "2025-06-30",
                              "comm": "test"}, timeout=15)
        assert rc.status_code == 201, rc.text
        inhab = rc.json()
        inhab_id = inhab["id"]
        # uuid should be a TEXT uuid, not an integer string of small size
        assert len(inhab_id) >= 32 or "-" in inhab_id, f"id should be UUID-like: {inhab_id}"

        ru = admin.put(f"{BASE_URL}/api/avocats/{avo_id}/inhabilites/{inhab_id}",
                       json={"datedeb": "2025-01-01", "datefin": "2025-12-31",
                             "comm": "modifié"}, timeout=15)
        assert ru.status_code == 200, ru.text

        rd = admin.delete(f"{BASE_URL}/api/avocats/{avo_id}/inhabilites/{inhab_id}", timeout=15)
        assert rd.status_code == 200


# ---------- Web password ----------
class TestWebPassword:
    def test_set_clear_web_password(self, admin, created_avocats):
        r = _create_avocat(admin)
        avo_id = r.json()["id"]
        created_avocats.append(avo_id)

        rs = admin.put(f"{BASE_URL}/api/avocats/{avo_id}/web-password",
                       json={"password": "secret123"}, timeout=15)
        assert rs.status_code == 200
        rs2 = admin.put(f"{BASE_URL}/api/avocats/{avo_id}/web-password",
                        json={"password": "abc"}, timeout=15)
        assert rs2.status_code == 400  # too short
        rd = admin.delete(f"{BASE_URL}/api/avocats/{avo_id}/web-password", timeout=15)
        assert rd.status_code == 200


# ---------- Audit log ----------
class TestAudit:
    def test_audit_paginated(self, admin, created_avocats):
        r = _create_avocat(admin)
        avo_id = r.json()["id"]
        created_avocats.append(avo_id)

        # generate several audit entries
        for i in range(3):
            admin.put(f"{BASE_URL}/api/avocats/{avo_id}",
                      json={"comm": f"upd{i}"}, timeout=15)

        ra = admin.get(f"{BASE_URL}/api/avocats/{avo_id}/audit?page=1&page_size=10", timeout=15)
        assert ra.status_code == 200, ra.text
        d = ra.json()
        assert "items" in d and "total" in d and "page" in d
        assert d["total"] >= 4  # 1 create + 3 updates
        # chronological DESC
        ts = [it["timestamp"] for it in d["items"]]
        assert ts == sorted(ts, reverse=True)


# ---------- Mandats CRUD ----------
class TestMandats:
    def test_full_crud_and_filters(self, admin, created_avocats):
        r = _create_avocat(admin)
        avo_id = r.json()["id"]
        created_avocats.append(avo_id)

        payload = {"avocat_id": avo_id, "requerant": "Étienne",
                   "article": "486.3", "date_ordonnance": "2025-06-15",
                   "numero": "MAN-001", "groupe": "Pratique Privée"}
        rc = admin.post(f"{BASE_URL}/api/mandats", json=payload, timeout=15)
        assert rc.status_code == 201, rc.text
        mid = rc.json()["id"]

        # GET with filter avocat_id
        rl = admin.get(f"{BASE_URL}/api/mandats?avocat_id={avo_id}", timeout=15)
        assert rl.status_code == 200
        assert any(m["id"] == mid for m in rl.json())

        # Filter article
        rf = admin.get(f"{BASE_URL}/api/mandats?article=486.3", timeout=15)
        assert rf.status_code == 200
        assert all(m["article"] == "486.3" for m in rf.json())

        # Filter date range
        rd = admin.get(f"{BASE_URL}/api/mandats?date_debut=2025-06-01&date_fin=2025-06-30", timeout=15)
        assert rd.status_code == 200
        ids = [m["id"] for m in rd.json()]
        assert mid in ids

        # PUT update
        ru = admin.put(f"{BASE_URL}/api/mandats/{mid}",
                       json={"numero": "MAN-002", "commentaire": "ok"}, timeout=15)
        assert ru.status_code == 200

        # DELETE
        rdel = admin.delete(f"{BASE_URL}/api/mandats/{mid}", timeout=15)
        assert rdel.status_code == 200


# ---------- Rapports PDF ----------
class TestRapportsPDF:
    @pytest.mark.parametrize("path,params", [
        ("/api/rapports/registre97", {"date_debut": "2024-01-01", "date_fin": "2026-12-31"}),
        ("/api/rapports/registre98", {"date_debut": "2024-01-01", "date_fin": "2026-12-31"}),
        ("/api/rapports/liste-det-bar", {}),
        ("/api/rapports/liste-det-dist", {}),
        ("/api/rapports/liste-det-reg", {}),
        ("/api/rapports/liste-som", {}),
    ])
    def test_pdf_endpoint(self, admin, path, params):
        r = admin.get(f"{BASE_URL}{path}", params=params, timeout=30)
        assert r.status_code == 200, f"{path}: {r.status_code} {r.text[:200]}"
        # PDF signature
        assert r.content[:4] == b"%PDF", f"{path}: not a PDF, got {r.content[:20]!r}"


# ---------- Connexions ----------
class TestConnexions:
    def test_list_admin(self, admin):
        r = admin.get(f"{BASE_URL}/api/connexions", timeout=15)
        assert r.status_code == 200
        items = r.json()
        assert any(c.get("is_primary") for c in items), "expected at least one is_primary connexion"

    def test_list_ti_can_access(self, ti):
        r = ti.get(f"{BASE_URL}/api/connexions", timeout=15)
        assert r.status_code == 200

    def test_primary_readonly_except_description(self, admin):
        r = admin.get(f"{BASE_URL}/api/connexions", timeout=15)
        primary = next((c for c in r.json() if c.get("is_primary")), None)
        assert primary is not None
        # try changing server (not description) → 403
        rb = admin.put(f"{BASE_URL}/api/connexions/{primary['id']}",
                       json={"server": "newhost.example.com"}, timeout=15)
        assert rb.status_code == 403, rb.text
        # description ok
        ro = admin.put(f"{BASE_URL}/api/connexions/{primary['id']}",
                       json={"description": "Updated description"}, timeout=15)
        assert ro.status_code == 200, ro.text

    def test_primary_test_ok(self, admin):
        r = admin.get(f"{BASE_URL}/api/connexions", timeout=15)
        primary = next((c for c in r.json() if c.get("is_primary")), None)
        assert primary is not None
        rt = admin.post(f"{BASE_URL}/api/connexions/{primary['id']}/test", timeout=30)
        assert rt.status_code == 200
        d = rt.json()
        assert d.get("ok") is True, f"connection test failed: {d}"

    def test_primary_download_sqlite(self, admin):
        r = admin.get(f"{BASE_URL}/api/connexions", timeout=15)
        primary = next((c for c in r.json() if c.get("is_primary")
                       and c.get("type") == "sqlite"), None)
        assert primary is not None, "expected primary sqlite connexion"
        rd = admin.get(f"{BASE_URL}/api/connexions/{primary['id']}/download", timeout=30)
        assert rd.status_code == 200
        assert rd.headers.get("content-type", "").startswith("application/x-sqlite3")
        # SQLite file magic
        assert rd.content[:16].startswith(b"SQLite format 3")

    def test_primary_cannot_delete(self, admin):
        r = admin.get(f"{BASE_URL}/api/connexions", timeout=15)
        primary = next((c for c in r.json() if c.get("is_primary")), None)
        rd = admin.delete(f"{BASE_URL}/api/connexions/{primary['id']}", timeout=15)
        assert rd.status_code == 403


# ---------- Users CRUD + roles ----------
class TestUsersAndRoles:
    def test_user_crud_admin(self, admin, created_users):
        email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        rc = admin.post(f"{BASE_URL}/api/users",
                        json={"email": email, "name": "Editeur Test",
                              "role": "editeur", "password": "Pass1234!"}, timeout=15)
        assert rc.status_code == 201, rc.text
        uid = rc.json()["id"]
        created_users.append(uid)

        ru = admin.put(f"{BASE_URL}/api/users/{uid}",
                       json={"name": "Renommé"}, timeout=15)
        assert ru.status_code == 200

    def test_lecteur_cannot_modify(self, admin, created_users, created_avocats):
        # Create a lecteur user
        email = f"lec_{uuid.uuid4().hex[:8]}@example.com"
        pwd = "Lect1234!"
        rc = admin.post(f"{BASE_URL}/api/users",
                        json={"email": email, "name": "Lecteur",
                              "role": "lecteur", "password": pwd}, timeout=15)
        assert rc.status_code == 201
        created_users.append(rc.json()["id"])

        sl = _login(email, pwd)
        # Lecteur GET ok
        assert sl.get(f"{BASE_URL}/api/avocats", timeout=15).status_code == 200
        # Lecteur POST forbidden
        r = sl.post(f"{BASE_URL}/api/avocats",
                    json={"nom": "X", "prenom": "Y", "type_code": "A"}, timeout=15)
        assert r.status_code == 403, r.text
        # Lecteur cannot access connexions
        assert sl.get(f"{BASE_URL}/api/connexions", timeout=15).status_code == 403

    def test_editeur_cannot_delete_avocat(self, admin, created_users, created_avocats):
        email = f"ed_{uuid.uuid4().hex[:8]}@example.com"
        pwd = "Edit1234!"
        rc = admin.post(f"{BASE_URL}/api/users",
                        json={"email": email, "name": "Editeur",
                              "role": "editeur", "password": pwd}, timeout=15)
        assert rc.status_code == 201
        created_users.append(rc.json()["id"])

        # editeur creates and updates
        se = _login(email, pwd)
        rcr = _create_avocat(se)
        assert rcr.status_code == 201, rcr.text
        avo_id = rcr.json()["id"]
        created_avocats.append(avo_id)

        ru = se.put(f"{BASE_URL}/api/avocats/{avo_id}",
                    json={"nom": "Modifié"}, timeout=15)
        assert ru.status_code == 200

        # editeur cannot delete
        rd = se.delete(f"{BASE_URL}/api/avocats/{avo_id}", timeout=15)
        assert rd.status_code == 403

        # editeur cannot list users
        ru2 = se.get(f"{BASE_URL}/api/users", timeout=15)
        assert ru2.status_code == 403


# ---------- Persistence (after backend restart) ----------
class TestPersistence:
    def test_avocat_persists_after_restart(self, admin, created_avocats):
        unique_nom = f"Persist_{uuid.uuid4().hex[:6]}"
        r = _create_avocat(admin, nom=unique_nom)
        assert r.status_code == 201
        avo_id = r.json()["id"]
        created_avocats.append(avo_id)

        # Restart backend
        os.system("sudo supervisorctl restart backend > /dev/null 2>&1")
        time.sleep(5)

        # Wait for ready
        for _ in range(15):
            try:
                if requests.get(f"{BASE_URL}/api/", timeout=3).status_code in (200, 404, 401):
                    break
            except Exception:
                time.sleep(1)

        # Re-login because cookies still valid; try reusing first
        s2 = _login(ADMIN_EMAIL, ADMIN_PASSWORD)
        r2 = s2.get(f"{BASE_URL}/api/avocats/{avo_id}", timeout=15)
        assert r2.status_code == 200, f"avocat lost after restart: {r2.status_code}"
        assert r2.json()["nom"] == unique_nom
