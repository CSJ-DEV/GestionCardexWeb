"""
Backend tests — Audit log feature (iteration 7, P3).

Covers:
  - GET /api/avocats/{id}/audit AuthZ matrix (401 / 403 / 200)
  - audit_log entries are created for every CRUD on avocat / adresse / mega /
    inhabilite / web-password
  - Each entry has required fields (id, avocat_id, action, user_email, summary, timestamp)
  - List is sorted desc by timestamp
"""
import os
import uuid
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL").rstrip("/")
API = f"{BASE_URL}/api"

ADMIN_EMAIL = "admin@gestioncardex.qc"
ADMIN_PASSWORD = "Admin2026!"

EDITOR_EMAIL = f"TEST_editor_{uuid.uuid4().hex[:6]}@gestioncardex.qc"
EDITOR_PASSWORD = "Editeur2026!"

EXPECTED_ACTIONS = {
    "create", "update", "delete",
    "adresse_create", "adresse_update", "adresse_delete",
    "mega_update", "mega_delete",
    "inhab_create", "inhab_update", "inhab_delete",
    "web_password_set", "web_password_clear",
}


# ---------- Fixtures ----------

@pytest.fixture(scope="module")
def admin_session():
    s = requests.Session()
    r = s.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert r.status_code == 200, f"admin login failed: {r.status_code} {r.text}"
    return s


@pytest.fixture(scope="module")
def editor_session(admin_session):
    """Create an editor user (or reuse) and return a session logged in as editor."""
    # Try to create
    r = admin_session.post(f"{API}/users", json={
        "email": EDITOR_EMAIL,
        "password": EDITOR_PASSWORD,
        "name": "Test Editor",
        "role": "editeur",
    })
    assert r.status_code in (200, 201, 400, 409), f"create editor unexpected: {r.status_code} {r.text}"
    s = requests.Session()
    r2 = s.post(f"{API}/auth/login", json={"email": EDITOR_EMAIL, "password": EDITOR_PASSWORD})
    if r2.status_code != 200:
        pytest.skip(f"editor login failed (status={r2.status_code}); cannot test 403 path")
    return s


@pytest.fixture(scope="module")
def avocat_id(admin_session):
    """Create a fresh test avocat. Returns its id; cleaned up after module."""
    code = f"TST{uuid.uuid4().hex[:5].upper()}"
    payload = {
        "code": code,
        "type_code": "A",
        "nom": "AuditTest",
        "prenom": "Avocat",
        "statut": "actif",
        "comm": "seed audit",
    }
    r = admin_session.post(f"{API}/avocats", json=payload)
    assert r.status_code in (200, 201), f"create avocat failed: {r.status_code} {r.text}"
    aid = r.json()["id"]
    yield aid
    # Teardown
    try:
        admin_session.delete(f"{API}/avocats/{aid}")
    except Exception:
        pass


# ---------- Helpers ----------

def fetch_audit(session, avocat_id):
    r = session.get(f"{API}/avocats/{avocat_id}/audit")
    assert r.status_code == 200, f"audit GET failed: {r.status_code} {r.text}"
    return r.json()


def assert_entry_shape(entry, expected_avocat_id):
    assert isinstance(entry, dict)
    for k in ("id", "avocat_id", "action", "user_email", "summary", "timestamp"):
        assert k in entry, f"missing key {k} in audit entry: {entry}"
    assert entry["avocat_id"] == expected_avocat_id
    # uuid format
    uuid.UUID(entry["id"])
    assert isinstance(entry["action"], str) and entry["action"]
    assert isinstance(entry["summary"], str)
    assert isinstance(entry["timestamp"], str) and "T" in entry["timestamp"]


# ---------- AuthZ matrix ----------

class TestAuditAuthZ:
    def test_audit_requires_auth(self, avocat_id):
        # No cookies → 401
        r = requests.get(f"{API}/avocats/{avocat_id}/audit")
        assert r.status_code == 401, f"expected 401, got {r.status_code}"

    def test_audit_forbidden_for_editor(self, editor_session, avocat_id):
        r = editor_session.get(f"{API}/avocats/{avocat_id}/audit")
        assert r.status_code == 403, f"expected 403 for editeur, got {r.status_code} body={r.text}"

    def test_audit_ok_for_admin(self, admin_session, avocat_id):
        r = admin_session.get(f"{API}/avocats/{avocat_id}/audit")
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body, list)


# ---------- Action coverage on each CRUD ----------

class TestAuditActionCoverage:
    """Drive every mutation, then check audit_log got an entry per action."""

    def test_drive_all_mutations_and_verify(self, admin_session, avocat_id):
        s = admin_session

        # 1. create -> already done by avocat_id fixture
        # 2. update avocat
        r = s.put(f"{API}/avocats/{avocat_id}", json={
            "code": "DUMMY",  # will be overridden by required fields below
            "type_code": "A",
            "nom": "AuditTest",
            "prenom": "Avocat",
            "statut": "actif",
            "comm": "audit drive update",
        })
        assert r.status_code in (200, 201), f"update avocat failed: {r.status_code} {r.text}"

        # 3. adresse create / update / delete
        r = s.post(f"{API}/avocats/{avocat_id}/adresses?courant=true", json={
            "address": "1 rue audit", "ville": "QC", "province": "QC",
            "codepostal": "G1A 1A1",
        })
        assert r.status_code in (200, 201), f"adresse_create failed: {r.status_code} {r.text}"
        adr_id = r.json().get("id")
        assert adr_id

        r = s.put(f"{API}/avocats/{avocat_id}/adresses/{adr_id}?courant=true", json={
            "address": "2 rue audit (modif)", "ville": "QC",
        })
        assert r.status_code == 200, f"adresse_update failed: {r.status_code} {r.text}"

        r = s.delete(f"{API}/avocats/{avocat_id}/adresses/{adr_id}")
        assert r.status_code in (200, 204)

        # 4. mega_update / mega_delete
        r = s.put(f"{API}/avocats/{avocat_id}/mega", json={
            "sectbar": "Civil", "francais": True, "anglais": False, "exp": 5, "districts": [1, 2],
        })
        assert r.status_code == 200, f"mega_update failed: {r.status_code} {r.text}"

        r = s.delete(f"{API}/avocats/{avocat_id}/mega")
        assert r.status_code in (200, 204)

        # 5. inhab create / update / delete
        r = s.post(f"{API}/avocats/{avocat_id}/inhabilites", json={
            "datedeb": "2025-01-01", "datefin": "2025-12-31", "motif": "audit test",
        })
        assert r.status_code in (200, 201), f"inhab_create failed: {r.status_code} {r.text}"
        inhab_id = r.json().get("id")
        assert inhab_id

        r = s.put(f"{API}/avocats/{avocat_id}/inhabilites/{inhab_id}", json={
            "datedeb": "2025-02-01", "datefin": "2025-11-30", "motif": "audit test (modif)",
        })
        assert r.status_code == 200

        r = s.delete(f"{API}/avocats/{avocat_id}/inhabilites/{inhab_id}")
        assert r.status_code in (200, 204)

        # 6. web_password set / clear
        r = s.put(f"{API}/avocats/{avocat_id}/web-password", json={"password": "WebPwd123!"})
        assert r.status_code == 200, f"web-password set failed: {r.status_code} {r.text}"

        r = s.delete(f"{API}/avocats/{avocat_id}/web-password")
        assert r.status_code in (200, 204)

        # ---- Now read audit log and verify ----
        entries = fetch_audit(s, avocat_id)
        assert len(entries) >= 12, f"expected >=12 audit entries, got {len(entries)}: {[e['action'] for e in entries]}"

        # Sorted desc by timestamp
        timestamps = [e["timestamp"] for e in entries]
        assert timestamps == sorted(timestamps, reverse=True), \
            "audit list not sorted desc by timestamp"

        # All entries well-formed and tied to admin
        for e in entries:
            assert_entry_shape(e, avocat_id)
            assert e["user_email"] == ADMIN_EMAIL, f"unexpected user_email: {e}"

        actions = {e["action"] for e in entries}

        # Required actions for this run (no global delete since we keep the avocat for teardown)
        required = {
            "create", "update",
            "adresse_create", "adresse_update", "adresse_delete",
            "mega_update", "mega_delete",
            "inhab_create", "inhab_update", "inhab_delete",
            "web_password_set", "web_password_clear",
        }
        missing = required - actions
        assert not missing, f"audit_log missing actions: {missing}; got={actions}"

        # All observed actions belong to the documented vocabulary
        unexpected = actions - EXPECTED_ACTIONS
        assert not unexpected, f"unexpected audit actions: {unexpected}"


# ---------- Regression — PDF reports endpoints still alive ----------

class TestPdfReportsRegression:
    REPORT_PATHS = [
        ("rapports/registre97", {"date_debut": "2024-01-01", "date_fin": "2025-12-31"}),
        ("rapports/registre98", {"date_debut": "2024-01-01", "date_fin": "2025-12-31"}),
        ("rapports/liste-det-bar", {}),
        ("rapports/liste-det-dist", {}),
        ("rapports/liste-det-reg", {}),
        ("rapports/liste-som", {}),
    ]

    @pytest.mark.parametrize("path,params", REPORT_PATHS)
    def test_pdf_endpoints_admin_returns_pdf(self, admin_session, path, params):
        r = admin_session.get(f"{API}/{path}", params=params)
        assert r.status_code == 200, f"{path}: status={r.status_code} body={r.text[:200]}"
        assert r.content[:4] == b"%PDF", f"{path}: not a PDF, first bytes={r.content[:8]!r}"
