# pip install flask-cors pytest werkzeug
# backend/tests/test_validation.py
import sys, importlib, importlib.util, types
from pathlib import Path
import pytest
from werkzeug.security import generate_password_hash

# =========================================================
#  🔧 Mock de 'psycopg' (y 'psycopg2') antes de cargar la app Flask
# =========================================================
dummy_psycopg = types.ModuleType("psycopg")
setattr(dummy_psycopg, "__version__", "dummy")
setattr(dummy_psycopg, "connect", lambda *a, **k: None)
sys.modules.setdefault("psycopg", dummy_psycopg)
sys.modules.setdefault("psycopg2", dummy_psycopg)

# =========================================================
#  🔧 Import robusto de la app Flask (sin necesidad de __init__.py)
# =========================================================
TEST_FILE = Path(__file__).resolve()
BACKEND_DIR = TEST_FILE.parents[1]          # .../APP-Citas-Medicas/backend
PROJ_ROOT = BACKEND_DIR.parent              # .../APP-Citas-Medicas

# Asegura que la raíz del proyecto está en sys.path
if str(PROJ_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJ_ROOT))

try:
    app_module = importlib.import_module("backend.app")
except ModuleNotFoundError:
    app_path = BACKEND_DIR / "app.py"
    spec = importlib.util.spec_from_file_location("app_module", app_path)
    app_module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader, f"No se pudo localizar {app_path}"
    spec.loader.exec_module(app_module)

flask_app = getattr(app_module, "app")

# =========================================================
#  🧩 Clases dummy para simular base de datos
# =========================================================
class DummyCursor:
    def __init__(self, scripted=None):
        self.scripted = list(scripted) if scripted else []
        self.executed = []

    def execute(self, query, params=None):
        self.executed.append((query, params))

    def fetchone(self):
        if self.scripted:
            return self.scripted.pop(0)
        return None

    def close(self):
        pass


class DummyConn:
    def __init__(self, cursor):
        self._cursor = cursor
        self.committed = False
        self.closed = False

    def cursor(self):
        return self._cursor

    def commit(self):
        self.committed = True

    def close(self):
        self.closed = True


# =========================================================
#  ⚙️ Fixtures
# =========================================================
@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


@pytest.fixture
def set_get_conn(monkeypatch):
    def _set(conn_source):
        if isinstance(conn_source, Exception):
            def fake_get_conn():
                raise conn_source
            monkeypatch.setattr(app_module, "get_conn", fake_get_conn)
        else:
            def fake_get_conn():
                return DummyConn(conn_source)
            monkeypatch.setattr(app_module, "get_conn", fake_get_conn)
    return _set


# =========================================================
#  🧪 TESTS /register
# =========================================================
def test_register_faltan_campos(client):
    resp = client.post("/register", json={})
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "Faltan campos obligatorios"


def test_register_email_existente(client, set_get_conn):
    cursor = DummyCursor(scripted=[("existing-user-id",)])
    set_get_conn(cursor)
    payload = {"nombre": "Alice", "email": "alice@example.com", "password": "Secr3t!", "rol": "user"}
    resp = client.post("/register", json=payload)
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "El correo ya está registrado"


def test_register_ok(client, set_get_conn):
    cursor = DummyCursor(scripted=[None])
    set_get_conn(cursor)
    payload = {"nombre": "Bob", "email": "bob@example.com", "password": "P4ssw0rd!", "rol": "admin"}
    resp = client.post("/register", json=payload)
    body = resp.get_json()
    assert resp.status_code == 201
    assert body["message"] == "Usuario registrado correctamente"
    assert body["email"] == payload["email"]
    assert body["nombre"] == payload["nombre"]
    assert body["rol"] == payload["rol"]
    assert isinstance(body["user_id"], str) and len(body["user_id"]) > 0


def test_register_error_interno(client, set_get_conn):
    set_get_conn(Exception("DB down"))
    payload = {"nombre": "Carol", "email": "carol@example.com", "password": "s3cret!", "rol": "user"}
    resp = client.post("/register", json=payload)
    assert resp.status_code == 500
    assert resp.get_json()["error"] == "Error interno del servidor"


# =========================================================
#  🧪 TESTS /login
# =========================================================
def test_login_faltan_campos(client):
    resp = client.post("/login", json={})
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "Faltan campos obligatorios"


def test_login_correo_no_encontrado(client, set_get_conn):
    cursor = DummyCursor(scripted=[None])
    set_get_conn(cursor)
    payload = {"email": "nobody@example.com", "password": "whatever"}
    resp = client.post("/login", json=payload)
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "Correo no encontrado"


def test_login_contrasena_incorrecta(client, set_get_conn):
    stored_hash = generate_password_hash("correcta")
    cursor = DummyCursor(scripted=[("u-1", "Dani", stored_hash, "user")])
    set_get_conn(cursor)
    payload = {"email": "dani@example.com", "password": "mala"}
    resp = client.post("/login", json=payload)
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "Contraseña incorrecta"


def test_login_ok(client, set_get_conn):
    stored_hash = generate_password_hash("superclave")
    cursor = DummyCursor(scripted=[("u-42", "Erika", stored_hash, "admin")])
    set_get_conn(cursor)
    payload = {"email": "erika@example.com", "password": "superclave"}
    resp = client.post("/login", json=payload)
    body = resp.get_json()
    assert resp.status_code == 200
    assert body["message"] == "Inicio de sesión correcto"
    assert body["user_id"] == "u-42"
    assert body["nombre"] == "Erika"
    assert body["rol"] == "admin"


def test_login_error_interno(client, set_get_conn):
    set_get_conn(Exception("DB fatal"))
    payload = {"email": "x@example.com", "password": "x"}
    resp = client.post("/login", json=payload)
    assert resp.status_code == 500
    assert resp.get_json()["error"] == "Error interno del servidor"
