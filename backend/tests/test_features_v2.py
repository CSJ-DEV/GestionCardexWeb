"""V2 backend tests: NAS Luhn, next-code, adresses, mega, inhab, web-password, mandats, rapports, users, permissions"""
import os, uuid, pytest, requests

BASE = os.environ["REACT_APP_BACKEND_URL"].rstrip("/")
ADMIN = ("admin@gestioncardex.qc", "Admin2026!")


def _login(email, pw):
    s = requests.Session()
    r = s.post(f"{BASE}/api/auth/login", json={"email": email, "password": pw}, timeout=15)
    assert r.status_code == 200, r.text
    return s


@pytest.fixture(scope="module")
def admin_s():
    return _login(*ADMIN)


@pytest.fixture(scope="module")
def avo_id(admin_s):
    code = f"T{uuid.uuid4().hex[:6].upper()}"
    r = admin_s.post(f"{BASE}/api/avocats",
                     json={"code": code, "nom": "Test", "prenom": "Avo", "actif": True}, timeout=15)
    assert r.status_code == 201, r.text
    aid = r.json()["id"]
    yield aid
    admin_s.delete(f"{BASE}/api/avocats/{aid}", timeout=15)


# ---------- Next code ----------
def test_next_code(admin_s):
    r = admin_s.get(f"{BASE}/api/avocats/next-code", params={"type": "A"}, timeout=15)
    assert r.status_code == 200
    code = r.json()["code"]
    assert code.startswith("A") and len(code) == 5 and code[1:].isdigit()


# ---------- NAS Luhn ----------
def test_nas_invalid_rejected(admin_s):
    r = admin_s.post(f"{BASE}/api/avocats",
                     json={"code": f"N{uuid.uuid4().hex[:5].upper()}",
                           "nom": "X", "prenom": "Y", "nas": "123456789"}, timeout=15)
    assert r.status_code == 422, r.text


def test_duplicate_code(admin_s):
    code = f"D{uuid.uuid4().hex[:6].upper()}"
    r1 = admin_s.post(f"{BASE}/api/avocats", json={"code": code, "nom": "A", "prenom": "B"}, timeout=15)
    assert r1.status_code == 201
    r2 = admin_s.post(f"{BASE}/api/avocats", json={"code": code, "nom": "A", "prenom": "B"}, timeout=15)
    assert r2.status_code == 409
    admin_s.delete(f"{BASE}/api/avocats/{r1.json()['id']}", timeout=15)


# ---------- Adresses ----------
def test_adresses_courant_sync(admin_s, avo_id):
    r = admin_s.post(f"{BASE}/api/avocats/{avo_id}/adresses",
                     params={"courant": True},
                     json={"address": "123 rue", "ville": "Montréal", "telephone": "5145551234"}, timeout=15)
    assert r.status_code == 201, r.text
    rg = admin_s.get(f"{BASE}/api/avocats/{avo_id}", timeout=15)
    assert rg.json()["adresse"]["ville"] == "Montréal"
    lst = admin_s.get(f"{BASE}/api/avocats/{avo_id}/adresses", timeout=15).json()
    assert any(a.get("courant") for a in lst)


# ---------- Mega ----------
def test_mega_upsert_sets_flag(admin_s, avo_id):
    r = admin_s.put(f"{BASE}/api/avocats/{avo_id}/mega",
                    json={"francais": True, "art486": True, "districts": [1, 2], "tous_districts": False}, timeout=15)
    assert r.status_code == 200, r.text
    rg = admin_s.get(f"{BASE}/api/avocats/{avo_id}", timeout=15)
    assert rg.json()["mega"] is True
    m = admin_s.get(f"{BASE}/api/avocats/{avo_id}/mega", timeout=15).json()
    assert m["art486"] is True and m["districts"] == [1, 2]


# ---------- Inhabilites ----------
def test_inhab_crud(admin_s, avo_id):
    r = admin_s.post(f"{BASE}/api/avocats/{avo_id}/inhabilites",
                     json={"datedeb": "2025-01-01", "datefin": "2025-02-01", "comm": "X"}, timeout=15)
    assert r.status_code == 201, r.text
    iid = r.json()["id"]
    lst = admin_s.get(f"{BASE}/api/avocats/{avo_id}/inhabilites", timeout=15).json()
    assert any(x["id"] == iid for x in lst)
    rd = admin_s.delete(f"{BASE}/api/avocats/{avo_id}/inhabilites/{iid}", timeout=15)
    assert rd.status_code == 200


# ---------- Web password ----------
def test_web_password_flow(admin_s, avo_id):
    r1 = admin_s.put(f"{BASE}/api/avocats/{avo_id}/web-password", json={"password": "12345"}, timeout=15)
    assert r1.status_code == 400  # too short
    r2 = admin_s.put(f"{BASE}/api/avocats/{avo_id}/web-password", json={"password": "abcdef"}, timeout=15)
    assert r2.status_code == 200
    r3 = admin_s.delete(f"{BASE}/api/avocats/{avo_id}/web-password", timeout=15)
    assert r3.status_code == 200


# ---------- Mandats ----------
def test_mandats_crud(admin_s, avo_id):
    r = admin_s.post(f"{BASE}/api/mandats",
                     json={"avocat_id": avo_id, "requerant": "ABC", "article": "486.3",
                           "date_ordonnance": "2025-06-15", "numero": "M-1", "groupe": "Pratique Privée"}, timeout=15)
    assert r.status_code == 201, r.text
    mid = r.json()["id"]
    lst = admin_s.get(f"{BASE}/api/mandats", params={"avocat_id": avo_id}, timeout=15).json()
    assert any(m["id"] == mid for m in lst)
    rd = admin_s.delete(f"{BASE}/api/mandats/{mid}", timeout=15)
    assert rd.status_code == 200


# ---------- Rapports PDF ----------
@pytest.mark.parametrize("path,params", [
    ("/api/rapports/registre97", {"date_debut": "2025-01-01", "date_fin": "2025-12-31"}),
    ("/api/rapports/registre98", {"date_debut": "2025-01-01", "date_fin": "2025-12-31"}),
    ("/api/rapports/liste-det-bar", {}),
    ("/api/rapports/liste-det-dist", {}),
    ("/api/rapports/liste-det-reg", {}),
    ("/api/rapports/liste-som", {}),
])
def test_rapports_pdf(admin_s, path, params):
    r = admin_s.get(f"{BASE}{path}", params=params, timeout=30)
    assert r.status_code == 200, r.text
    assert r.content[:4] == b"%PDF", f"not a PDF: {r.content[:20]}"


# ---------- Users + Permissions ----------
@pytest.fixture(scope="module")
def users_setup(admin_s):
    users = {}
    for role in ("editeur", "lecteur"):
        email = f"test_{role}_{uuid.uuid4().hex[:6]}@x.qc"
        r = admin_s.post(f"{BASE}/api/users",
                         json={"email": email, "name": role, "password": "Pass1234!", "role": role}, timeout=15)
        assert r.status_code == 201, r.text
        users[role] = {"id": r.json()["id"], "email": email, "session": _login(email, "Pass1234!")}
    yield users
    for u in users.values():
        admin_s.delete(f"{BASE}/api/users/{u['id']}", timeout=15)


def test_users_admin_only(users_setup):
    # editeur cannot list users
    r = users_setup["editeur"]["session"].get(f"{BASE}/api/users", timeout=15)
    assert r.status_code == 403
    r2 = users_setup["lecteur"]["session"].get(f"{BASE}/api/users", timeout=15)
    assert r2.status_code == 403


def test_lecteur_readonly(users_setup):
    s = users_setup["lecteur"]["session"]
    r = s.get(f"{BASE}/api/avocats", timeout=15)
    assert r.status_code == 200
    rp = s.post(f"{BASE}/api/avocats",
                json={"code": f"L{uuid.uuid4().hex[:5].upper()}", "nom": "X", "prenom": "Y"}, timeout=15)
    assert rp.status_code == 403


def test_editeur_can_crud_but_not_delete_avocat(users_setup, admin_s):
    s = users_setup["editeur"]["session"]
    code = f"E{uuid.uuid4().hex[:5].upper()}"
    r = s.post(f"{BASE}/api/avocats", json={"code": code, "nom": "Ed", "prenom": "It"}, timeout=15)
    assert r.status_code == 201, r.text
    aid = r.json()["id"]
    ru = s.put(f"{BASE}/api/avocats/{aid}", json={"nom": "Ed2"}, timeout=15)
    assert ru.status_code == 200
    rd = s.delete(f"{BASE}/api/avocats/{aid}", timeout=15)
    assert rd.status_code == 403  # editeur cannot delete avocat
    admin_s.delete(f"{BASE}/api/avocats/{aid}", timeout=15)
