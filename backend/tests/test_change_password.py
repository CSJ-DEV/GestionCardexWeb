"""Tests for PUT /api/auth/change-password endpoint (iteration 11)."""
import os
import time
import pytest
import requests

BASE_URL = "https://cardex-migrate.preview.emergentagent.com"
API = f"{BASE_URL}/api"

ADMIN_EMAIL = "admin@gestioncardex.qc"
ADMIN_PWD = "Admin2026!"
NEW_PWD = "Nouveau2026!"
TI_EMAIL = "ti@gestioncardex.qc"
TI_PWD = "Ti2026!"


def login(session, email, password):
    return session.post(f"{API}/auth/login", json={"email": email, "password": password})


def test_change_password_requires_auth():
    """No cookie => 401."""
    r = requests.put(f"{API}/auth/change-password",
                     json={"current_password": "x", "new_password": "abcdefgh"})
    assert r.status_code == 401, r.text


def test_change_password_validation_min_length():
    """new_password < 8 => 422 Pydantic."""
    s = requests.Session()
    r = login(s, ADMIN_EMAIL, ADMIN_PWD)
    assert r.status_code == 200, r.text
    r = s.put(f"{API}/auth/change-password",
              json={"current_password": ADMIN_PWD, "new_password": "short"})
    assert r.status_code == 422, r.text


def test_change_password_wrong_current():
    """Bad current_password => 400."""
    s = requests.Session()
    assert login(s, ADMIN_EMAIL, ADMIN_PWD).status_code == 200
    r = s.put(f"{API}/auth/change-password",
              json={"current_password": "WrongPassword!", "new_password": "ValidPass1!"})
    assert r.status_code == 400, r.text
    assert "incorrect" in r.json()["detail"].lower()


def test_change_password_same_as_current():
    """new == current => 400."""
    s = requests.Session()
    assert login(s, ADMIN_EMAIL, ADMIN_PWD).status_code == 200
    r = s.put(f"{API}/auth/change-password",
              json={"current_password": ADMIN_PWD, "new_password": ADMIN_PWD})
    assert r.status_code == 400, r.text
    assert "différent" in r.json()["detail"].lower() or "different" in r.json()["detail"].lower()


def test_full_change_password_workflow_and_restore():
    """Admin: change → fail old → ok new → restore. Critical."""
    s = requests.Session()
    assert login(s, ADMIN_EMAIL, ADMIN_PWD).status_code == 200

    r = s.put(f"{API}/auth/change-password",
              json={"current_password": ADMIN_PWD, "new_password": NEW_PWD})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("ok") is True
    assert "message" in body

    # Old password should fail
    s2 = requests.Session()
    r = login(s2, ADMIN_EMAIL, ADMIN_PWD)
    assert r.status_code == 401, f"Old password still works! {r.text}"

    # New password should work
    s3 = requests.Session()
    r = login(s3, ADMIN_EMAIL, NEW_PWD)
    assert r.status_code == 200, r.text

    # Restore to original password
    r = s3.put(f"{API}/auth/change-password",
               json={"current_password": NEW_PWD, "new_password": ADMIN_PWD})
    assert r.status_code == 200, f"FAILED TO RESTORE ADMIN PASSWORD: {r.text}"

    # Verify restore worked
    s4 = requests.Session()
    assert login(s4, ADMIN_EMAIL, ADMIN_PWD).status_code == 200, "Admin password broken!"


def test_change_password_works_for_editeur_role():
    """Verify non-admin role (editeur) can also change own password."""
    admin = requests.Session()
    assert login(admin, ADMIN_EMAIL, ADMIN_PWD).status_code == 200

    # Create temp editeur
    test_email = f"TEST_editeur_{int(time.time())}@example.com"
    init_pwd = "EditeurInit1!"
    r = admin.post(f"{API}/users", json={
        "email": test_email, "name": "TEST Editeur", "password": init_pwd, "role": "editeur"
    })
    assert r.status_code in (200, 201), r.text
    user_id = r.json()["id"]

    try:
        # Login as editeur
        s = requests.Session()
        r = login(s, test_email, init_pwd)
        assert r.status_code == 200, r.text
        assert r.json()["role"] == "editeur"

        # Change own password
        new = "EditeurNew1!"
        r = s.put(f"{API}/auth/change-password",
                  json={"current_password": init_pwd, "new_password": new})
        assert r.status_code == 200, r.text

        # Verify new password works
        s2 = requests.Session()
        assert login(s2, test_email, new).status_code == 200
        # Old fails
        assert login(requests.Session(), test_email, init_pwd).status_code == 401
    finally:
        # Cleanup
        admin.delete(f"{API}/users/{user_id}")


def test_change_password_works_for_lecteur_role():
    """Verify lecteur (read-only) can change own password."""
    admin = requests.Session()
    assert login(admin, ADMIN_EMAIL, ADMIN_PWD).status_code == 200
    test_email = f"TEST_lecteur_{int(time.time())}@example.com"
    init_pwd = "LecteurInit1!"
    r = admin.post(f"{API}/users", json={
        "email": test_email, "name": "TEST Lecteur", "password": init_pwd, "role": "lecteur"
    })
    assert r.status_code in (200, 201), r.text
    user_id = r.json()["id"]
    try:
        s = requests.Session()
        assert login(s, test_email, init_pwd).status_code == 200
        new = "LecteurNew1!"
        r = s.put(f"{API}/auth/change-password",
                  json={"current_password": init_pwd, "new_password": new})
        assert r.status_code == 200, r.text
        assert login(requests.Session(), test_email, new).status_code == 200
    finally:
        admin.delete(f"{API}/users/{user_id}")


def test_ti_password_still_valid_after_all_tests():
    """Sanity: TI account untouched."""
    s = requests.Session()
    assert login(s, TI_EMAIL, TI_PWD).status_code == 200
