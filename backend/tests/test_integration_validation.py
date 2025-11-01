import pytest
from .mock.mock_db import app, reset_mock_db


@pytest.fixture(autouse=True)
def setup_db():
    reset_mock_db()


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ------------------------------
# PRUEBAS PARA /register
# ------------------------------

def test_register_usuario_nuevo(client):
    nuevo_usuario = {
        "nombre": "Laura Pérez",
        "email": "laura@example.com",
        "password": "12345",
        "rol": "paciente"
    }

    res = client.post("/register", json=nuevo_usuario)
    data = res.get_json()

    assert res.status_code == 201
    assert data["message"] == "Usuario registrado correctamente"
    assert data["email"] == "laura@example.com"
    assert data["rol"] == "paciente"


def test_register_email_duplicado(client):
    # Ya existe "ana@example.com" en el mock
    usuario_duplicado = {
        "nombre": "Ana Duplicada",
        "email": "ana@example.com",
        "password": "nueva123",
        "rol": "paciente"
    }

    res = client.post("/register", json=usuario_duplicado)
    data = res.get_json()

    assert res.status_code == 400
    assert "El correo ya está registrado" in data["error"]


def test_register_faltan_campos(client):
    usuario_incompleto = {
        "nombre": "Pedro"
        # falta email, password, rol
    }

    res = client.post("/register", json=usuario_incompleto)
    data = res.get_json()

    assert res.status_code == 400
    assert "Faltan campos obligatorios" in data["error"]


# ------------------------------
# PRUEBAS PARA /login
# ------------------------------

def test_login_exitoso(client):
    # Usuario existente en mock_db: ana@example.com / password 1234
    credenciales = {
        "email": "ana@example.com",
        "password": "1234"
    }

    res = client.post("/login", json=credenciales)
    data = res.get_json()

    assert res.status_code == 200
    assert data["message"] == "Inicio de sesión correcto"
    assert data["email"] == credenciales["email"] if "email" in data else True  # opcional
    assert data["rol"] == "paciente"


def test_login_email_inexistente(client):
    credenciales = {
        "email": "noexiste@example.com",
        "password": "1234"
    }

    res = client.post("/login", json=credenciales)
    data = res.get_json()

    assert res.status_code == 401
    assert "Correo no encontrado" in data["error"]


def test_login_password_incorrecta(client):
    credenciales = {
        "email": "ana@example.com",
        "password": "incorrecta"
    }

    res = client.post("/login", json=credenciales)
    data = res.get_json()

    assert res.status_code == 401
    assert "Contraseña incorrecta" in data["error"]


def test_login_faltan_campos(client):
    credenciales_incompletas = {
        "email": "ana@example.com"
        # falta password
    }

    res = client.post("/login", json=credenciales_incompletas)
    data = res.get_json()

    assert res.status_code == 400
    assert "Faltan campos obligatorios" in data["error"]