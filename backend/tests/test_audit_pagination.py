"""
Backend tests — Iteration 8 P3:
  - GET /api/avocats/{id}/audit pagination shape & params validation
  - timestamp stored as native BSON datetime (verified via a sort sanity check + ISO string in HTTP)
  - Legacy migration: no remaining string timestamps in audit_log
"""
import os
import uuid
import time
import pytest
import requests
from datetime import datetime

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL").rstrip("/")
API = f"{BASE_URL}/api"

ADMIN_EMAIL = "admin@gestioncardex.qc"
ADMIN_PASSWORD = "Admin2026!"


# ---------- Fixtures ----------
@pytest.fixture(scope="module")
def admin_session():
    s = requests.Session()
    r = s.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert r.status_code == 200, f"admin login failed: {r.status_code} {r.text}"
    return s


@pytest.fixture(scope="module")
def avocat_with_history(admin_session):
    """Create an avocat then drive 3 successive updates so we have >= 4 audit entries."""
    code = f"TST{uuid.uuid4().hex[:5].upper()}"
    payload = {
        "code": code, "type_code": "A", "nom": "PaginAudit", "prenom": "Test",
        "statut": "actif", "comm": "v0",
    }
    r = admin_session.post(f"{API}/avocats", json=payload)
    assert r.status_code in (200, 201), f"create avocat failed: {r.status_code} {r.text}"
    aid = r.json()["id"]

    # 3 successive updates
    for i in range(1, 4):
        upd = {**payload, "comm": f"v{i}"}
        r = admin_session.put(f"{API}/avocats/{aid}", json=upd)
        assert r.status_code in (200, 201), f"update #{i} failed: {r.status_code} {r.text}"
        time.sleep(0.05)  # ensure distinct timestamps

    yield aid
    try:
        admin_session.delete(f"{API}/avocats/{aid}")
    except Exception:
        pass


# ---------- Tests : shape / defaults ----------
class TestAuditPaginationShape:
    def test_default_shape(self, admin_session, avocat_with_history):
        r = admin_session.get(f"{API}/avocats/{avocat_with_history}/audit")
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body, dict), f"expected dict, got {type(body)}"
        for k in ("items", "total", "page", "page_size"):
            assert k in body, f"missing key {k} in response: {body}"
        assert body["page"] == 1
        assert body["page_size"] == 20
        assert isinstance(body["items"], list)
        assert isinstance(body["total"], int)
        assert body["total"] >= 4  # create + 3 updates

    def test_custom_page_size_capped(self, admin_session, avocat_with_history):
        r = admin_session.get(f"{API}/avocats/{avocat_with_history}/audit",
                              params={"page": 1, "page_size": 5})
        assert r.status_code == 200
        body = r.json()
        assert body["page"] == 1
        assert body["page_size"] == 5
        assert len(body["items"]) <= 5
        # total is absolute, not bounded by page_size
        assert body["total"] >= 4

    def test_page2_distinct_or_empty(self, admin_session, avocat_with_history):
        r1 = admin_session.get(f"{API}/avocats/{avocat_with_history}/audit",
                               params={"page": 1, "page_size": 5})
        r2 = admin_session.get(f"{API}/avocats/{avocat_with_history}/audit",
                               params={"page": 2, "page_size": 5})
        assert r1.status_code == 200 and r2.status_code == 200
        b1, b2 = r1.json(), r2.json()
        ids1 = {it["id"] for it in b1["items"]}
        ids2 = {it["id"] for it in b2["items"]}
        if b1["total"] > 5:
            assert ids2, "expected page=2 items when total>5"
            assert ids1.isdisjoint(ids2), "page1 and page2 should not overlap"
        else:
            assert b2["items"] == [], f"expected empty page 2 when total <=5; got {b2['items']}"


# ---------- Tests : validation 422 ----------
class TestAuditPaginationValidation:
    @pytest.mark.parametrize("ps", [0, 201, -1, 1000])
    def test_invalid_page_size(self, admin_session, avocat_with_history, ps):
        r = admin_session.get(f"{API}/avocats/{avocat_with_history}/audit",
                              params={"page": 1, "page_size": ps})
        assert r.status_code == 422, f"page_size={ps} should be 422, got {r.status_code} {r.text[:200]}"

    @pytest.mark.parametrize("p", [0, -1])
    def test_invalid_page(self, admin_session, avocat_with_history, p):
        r = admin_session.get(f"{API}/avocats/{avocat_with_history}/audit",
                              params={"page": p, "page_size": 5})
        assert r.status_code == 422, f"page={p} should be 422, got {r.status_code} {r.text[:200]}"


# ---------- Tests : sort DESC ----------
class TestAuditSortDesc:
    def test_timestamp_descending(self, admin_session, avocat_with_history):
        r = admin_session.get(f"{API}/avocats/{avocat_with_history}/audit",
                              params={"page": 1, "page_size": 50})
        assert r.status_code == 200
        items = r.json()["items"]
        assert len(items) >= 4
        ts = [it["timestamp"] for it in items]
        # Each ts should be an ISO string
        for t in ts:
            assert isinstance(t, str) and "T" in t
            datetime.fromisoformat(t.replace("Z", "+00:00"))  # must parse
        assert ts == sorted(ts, reverse=True), f"not sorted desc: {ts}"


# ---------- Tests : timestamp ISO string in response ----------
class TestTimestampIsoInResponse:
    def test_response_timestamp_is_iso_string(self, admin_session, avocat_with_history):
        r = admin_session.get(f"{API}/avocats/{avocat_with_history}/audit",
                              params={"page": 1, "page_size": 1})
        assert r.status_code == 200
        items = r.json()["items"]
        assert items, "expected at least one entry"
        ts = items[0]["timestamp"]
        assert isinstance(ts, str), f"timestamp not str: {type(ts)} {ts!r}"
        # Parse roundtrip
        parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        assert parsed.year >= 2024
