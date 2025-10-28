"""
=== TESTS DE INTEGRACIÓN VÍA HTTP ===
Prueban las rutas /register y /login contra el servidor Flask en ejecución.
No acceden directamente a la base de datos, solo usan peticiones HTTP reales.
"""

import requests
import pytest
import uuid

# URL base del backend Flask (no el frontend)
BASE_URL = "http://localhost:8000"


def test_backend_disponible():
    """Verifica que el backend esté disponible antes de correr las pruebas."""
    try:
        resp = requests.get(f"{BASE_URL}/")
        assert resp.status_code in (200, 404), (
            f"El backend no está accesible en {BASE_URL}. "
            "Asegúrate de ejecutar 'flask run --port=8000' o 'python app.py'."
        )
    except requests.exceptions.ConnectionError:
        pytest.fail(f"No se pudo conectar con el backend en {BASE_URL}")


@pytest.fixture(scope="session")
def email_unico():
    """Genera un email único por sesión de test para evitar duplicados."""
    return f"test_{uuid.uuid4().hex[:6]}@example.com"


# === 1. REGISTRO EXITOSO ===
def test_registro_exitoso(email_unico):
    """Debe crear correctamente un nuevo usuario."""
    datos = {
        "nombre": "Usuario Integración",
        "email": email_unico,
        "password": "Clave123!",
        "rol": "usuario"
    }
    resp = requests.post(f"{BASE_URL}/register", json=datos)
    assert resp.status_code == 201, f"Esperado 201, recibido {resp.status_code}"
    body = resp.json()
    assert "message" in body and body["message"] == "Usuario registrado correctamente"
    assert body["email"] == email_unico


# === 2. REGISTRO FALLIDO (EMAIL REPETIDO) ===
def test_registro_fallido_email_repetido(email_unico):
    """Debe rechazar el registro si el email ya existe."""
    datos = {
        "nombre": "Duplicado",
        "email": email_unico,
        "password": "Clave456!",
        "rol": "usuario"
    }
    resp = requests.post(f"{BASE_URL}/register", json=datos)
    assert resp.status_code == 400, f"Esperado 400, recibido {resp.status_code}"
    body = resp.json()
    assert "error" in body and body["error"] == "El correo ya está registrado"


# === 3. LOGIN EXITOSO ===
def test_login_exitoso(email_unico):
    """Debe permitir el acceso si las credenciales son correctas."""
    datos = {"email": email_unico, "password": "Clave123!"}
    resp = requests.post(f"{BASE_URL}/login", json=datos)
    assert resp.status_code == 200, f"Esperado 200, recibido {resp.status_code}"
    body = resp.json()
    assert "message" in body and body["message"] == "Inicio de sesión correcto"
    assert "user_id" in body and "rol" in body


# === 4. LOGIN FALLIDO (USUARIO INEXISTENTE) ===
def test_login_fallido_usuario_inexistente():
    """Debe devolver error si el usuario no existe."""
    datos = {"email": "no_existe_user@example.com", "password": "12345"}
    resp = requests.post(f"{BASE_URL}/login", json=datos)
    assert resp.status_code == 401, f"Esperado 401, recibido {resp.status_code}"
    body = resp.json()
    assert "error" in body and body["error"] == "Correo no encontrado"


# === 5. LOGIN FALLIDO (CAMPOS INCOMPLETOS) ===
def test_login_fallido_campos_incompletos():
    """Debe devolver error si faltan campos obligatorios."""
    datos = {"email": "falso@example.com"}  # Falta password
    resp = requests.post(f"{BASE_URL}/login", json=datos)
    assert resp.status_code == 400, f"Esperado 400, recibido {resp.status_code}"
    body = resp.json()
    assert "error" in body and body["error"] == "Faltan campos obligatorios"
