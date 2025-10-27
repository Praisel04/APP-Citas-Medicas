"""
=== TESTS DE INTEGRACIÓN PARA /register Y /login ===
"""

import os
import sys
import pytest
import uuid
from werkzeug.security import generate_password_hash

# 🔧 Asegurar que la raíz del proyecto esté en el path (compatible con Windows y Anaconda)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.app import app  # ✅ Import correcto del Flask app


@pytest.fixture
def client():
    """Fixture que provee un cliente de prueba Flask."""
    app.config["TESTING"] = True
    app.config["DEBUG"] = False
    with app.test_client() as client:
        yield client


# ===============================
# === TESTS PARA /register ===
# ===============================

def test_register_valido(client, monkeypatch):
    """Registro exitoso:
    Verifica que un usuario nuevo pueda registrarse correctamente."""

    # Simulamos que el correo NO existe en la base de datos
    def mock_get_conn():
        class MockCursor:
            def execute(self, query, params=None):
                self.last_query = query
                self.last_params = params
                if "SELECT id FROM usuario" in query:
                    self.result = None  # no hay usuario duplicado
                elif "INSERT INTO usuario" in query:
                    self.result = [(str(uuid.uuid4()),)]
            def fetchone(self): return self.result
            def close(self): pass
        class MockConn:
            def cursor(self): return MockCursor()
            def commit(self): pass
            def close(self): pass
        return MockConn()

    monkeypatch.setattr("backend.app.get_conn", mock_get_conn)

    payload = {
        "nombre": "Carlos",
        "email": "carlos@example.com",
        "password": "abc123",
        "rol": "usuario"
    }

    response = client.post("/register", json=payload)
    data = response.get_json()

    assert response.status_code == 201
    assert "message" in data
    assert data["rol"] == "usuario"


def test_register_duplicado(client, monkeypatch):
    """Registro duplicado:
    Verifica que el endpoint devuelva error si el correo ya existe."""

    def mock_get_conn():
        class MockCursor:
            def execute(self, query, params=None):
                if "SELECT id FROM usuario" in query:
                    self.result = ("existing-id",)
            def fetchone(self): return self.result
            def close(self): pass
        class MockConn:
            def cursor(self): return MockCursor()
            def close(self): pass
        return MockConn()

    monkeypatch.setattr("backend.app.get_conn", mock_get_conn)

    payload = {
        "nombre": "Juan",
        "email": "juan@example.com",
        "password": "abc123",
        "rol": "usuario"
    }

    response = client.post("/register", json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert "error" in data


def test_register_campos_faltantes(client):
    """Campos faltantes:
    Debe devolver error 400 si faltan campos en el body."""
    payload = {"email": "incompleto@example.com"}  # faltan campos
    response = client.post("/register", json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert "error" in data


# ===============================
# === TESTS PARA /login ===
# ===============================

def test_login_exitoso(client, monkeypatch):
    """Login exitoso:
    Verifica que un usuario existente pueda autenticarse."""

    password_hash = generate_password_hash("abc123")

    def mock_get_conn():
        class MockCursor:
            def execute(self, query, params=None):
                if "SELECT id, nombre,password_hash, rol" in query:
                    self.result = (uuid.uuid4(), "Carlos", password_hash, "usuario")
            def fetchone(self): return self.result
            def close(self): pass
        class MockConn:
            def cursor(self): return MockCursor()
            def close(self): pass
        return MockConn()

    monkeypatch.setattr("backend.app.get_conn", mock_get_conn)

    payload = {"email": "carlos@example.com", "password": "abc123"}
    response = client.post("/login", json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert "message" in data
    assert data["nombre"] == "Carlos"


def test_login_contrasena_incorrecta(client, monkeypatch):
    """Contraseña incorrecta:
    Debe devolver 401 si la contraseña no coincide."""

    wrong_hash = generate_password_hash("otra_pass")

    def mock_get_conn():
        class MockCursor:
            def execute(self, query, params=None):
                if "SELECT id, nombre,password_hash, rol" in query:
                    self.result = (uuid.uuid4(), "Carlos", wrong_hash, "usuario")
            def fetchone(self): return self.result
            def close(self): pass
        class MockConn:
            def cursor(self): return MockCursor()
            def close(self): pass
        return MockConn()

    monkeypatch.setattr("backend.app.get_conn", mock_get_conn)

    payload = {"email": "carlos@example.com", "password": "abc123"}
    response = client.post("/login", json=payload)
    data = response.get_json()

    assert response.status_code == 401
    assert "error" in data


def test_login_usuario_no_encontrado(client, monkeypatch):
    """Usuario no encontrado:
    Verifica que devuelva 401 cuando el correo no existe."""

    def mock_get_conn():
        class MockCursor:
            def execute(self, query, params=None):
                if "SELECT id, nombre,password_hash, rol" in query:
                    self.result = None  # no hay usuario
            def fetchone(self): return self.result
            def close(self): pass
        class MockConn:
            def cursor(self): return MockCursor()
            def close(self): pass
        return MockConn()

    monkeypatch.setattr("backend.app.get_conn", mock_get_conn)

    payload = {"email": "nadie@example.com", "password": "abc123"}
    response = client.post("/login", json=payload)
    data = response.get_json()

    assert response.status_code == 401
    assert "error" in data


def test_login_campos_faltantes(client):
    """Campos faltantes:
    Debe devolver error 400 si falta email o password."""
    payload = {"email": "user@example.com"}  # falta password
    response = client.post("/login", json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert "error" in data
