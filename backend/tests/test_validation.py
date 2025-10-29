"""
=== TESTS SIMULADOS PARA REGISTER Y LOGIN ===
Simulan las rutas /register y /login sin conexión a base de datos real.
"""

from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

# === BASE DE DATOS MOCK ===
usuarios_mock = [
    {
        "id": uuid.uuid4(),
        "nombre": "Juan Pérez",
        "email": "juan@example.com",
        "password_hash": generate_password_hash("12345"),
        "rol": "usuario",
        "created_at": datetime.now(timezone.utc),
    }
]

# === FUNCIONES SIMULADAS ===
def register_mock(data, usuarios):
    """
    Simula el comportamiento de la ruta /register.
    Valida los datos, comprueba duplicados y agrega un nuevo usuario.
    """
    # Validar campos obligatorios
    if not data or not all(k in data for k in ('nombre', 'email', 'password', 'rol')):
        return {"error": "Faltan campos obligatorios"}, 400
    
    # Comprobar si ya existe el correo
    for u in usuarios:
        if u["email"] == data["email"]:
            return {"error": "El correo ya está registrado"}, 400
    
    # Crear nuevo usuario
    user_id = uuid.uuid4()
    nuevo_usuario = {
        "id": user_id,
        "nombre": data["nombre"],
        "email": data["email"],
        "password_hash": generate_password_hash(data["password"]),
        "rol": data["rol"],
        "created_at": datetime.now(timezone.utc),
    }
    usuarios.append(nuevo_usuario)
    return {
        "message": "Usuario registrado correctamente",
        "user_id": str(user_id),
        "nombre": data["nombre"],
        "email": data["email"],
        "rol": data["rol"],
        "total": len(usuarios)
    }, 201


def login_mock(data, usuarios):
    """
    Simula el comportamiento de la ruta /login.
    Busca el usuario por email y verifica la contraseña.
    """
    if not data or not all(k in data for k in ('email', 'password')):
        return {"error": "Faltan campos obligatorios"}, 400
    
    # Buscar usuario
    user = next((u for u in usuarios if u["email"] == data["email"]), None)
    if not user:
        return {"error": "Correo no encontrado"}, 401

    # Verificar contraseña
    if not check_password_hash(user["password_hash"], data["password"]):
        return {"error": "Contraseña incorrecta"}, 401

    return {
        "message": "Inicio de sesión correcto",
        "user_id": str(user["id"]),
        "nombre": user["nombre"],
        "rol": user["rol"]
    }, 200


# === TESTS PARA REGISTER ===

def test_register_valido():
    """Registro válido:
    Debe crear un nuevo usuario cuando los datos son correctos.
    
    Asserts:
        - Debe devolver mensaje de éxito.
        - El total de usuarios debe incrementarse.
    """
    usuarios_local = usuarios_mock.copy()
    datos = {"nombre": "Ana López", "email": "ana@example.com", "password": "abc123", "rol": "admin"}
    resultado, status = register_mock(datos, usuarios_local)
    
    assert status == 201, "El código de estado debe ser 201"
    assert "message" in resultado, "Debe devolver un mensaje de éxito"
    assert resultado["total"] == len(usuarios_local), "El total debe coincidir con la cantidad actualizada"


def test_register_duplicado():
    """Registro duplicado:
    Debe rechazar el registro si el email ya existe.
    
    Asserts:
        - Debe devolver un error por correo duplicado.
    """
    usuarios_local = usuarios_mock.copy()
    datos = {"nombre": "Juan Pérez", "email": "juan@example.com", "password": "12345", "rol": "usuario"}
    resultado, status = register_mock(datos, usuarios_local)
    
    assert status == 400, "Debe devolver 400 por duplicado"
    assert "error" in resultado, "Debe devolver un mensaje de error"


def test_register_campos_faltantes():
    """Registro con datos incompletos:
    Debe rechazar el registro si faltan campos obligatorios.
    
    Asserts:
        - Debe devolver un error de campos faltantes.
    """
    usuarios_local = usuarios_mock.copy()
    datos = {"email": "nuevo@example.com"}  # Faltan campos
    resultado, status = register_mock(datos, usuarios_local)
    
    assert status == 400, "Debe devolver 400 por campos faltantes"
    assert "error" in resultado, "Debe devolver un mensaje de error"


# === TESTS PARA LOGIN ===

def test_login_valido():
    """Inicio de sesión válido:
    Debe permitir el acceso cuando las credenciales son correctas.
    
    Asserts:
        - Debe devolver mensaje de éxito.
        - Debe incluir el nombre y el rol.
    """
    usuarios_local = usuarios_mock.copy()
    datos = {"email": "juan@example.com", "password": "12345"}
    resultado, status = login_mock(datos, usuarios_local)
    
    assert status == 200, "Debe devolver 200 en login correcto"
    assert "message" in resultado, "Debe contener mensaje de éxito"
    assert "nombre" in resultado and "rol" in resultado, "Debe incluir los campos 'nombre' y 'rol'"


def test_login_contrasena_incorrecta():
    """Contraseña incorrecta:
    Debe devolver un error si la contraseña no coincide.
    
    Asserts:
        - Debe devolver un error de autenticación.
    """
    usuarios_local = usuarios_mock.copy()
    datos = {"email": "juan@example.com", "password": "malapass"}
    resultado, status = login_mock(datos, usuarios_local)
    
    assert status == 401, "Debe devolver 401 si la contraseña es incorrecta"
    assert "error" in resultado, "Debe devolver un mensaje de error"


def test_login_usuario_no_existente():
    """Usuario inexistente:
    Debe devolver un error si el email no está registrado.
    
    Asserts:
        - Debe devolver error 401 y mensaje correspondiente.
    """
    usuarios_local = usuarios_mock.copy()
    datos = {"email": "nadie@example.com", "password": "123"}
    resultado, status = login_mock(datos, usuarios_local)
    
    assert status == 401, "Debe devolver 401 si el usuario no existe"
    assert "error" in resultado, "Debe devolver un mensaje de error"


def test_login_campos_faltantes():
    """Login con campos faltantes:
    Debe rechazar el intento de inicio si no están todos los campos.
    
    Asserts:
        - Debe devolver error 400 por campos incompletos.
    """
    usuarios_local = usuarios_mock.copy()
    datos = {"email": "juan@example.com"}  # Falta password
    resultado, status = login_mock(datos, usuarios_local)
    
    assert status == 400, "Debe devolver 400 por campos faltantes"
    assert "error" in resultado, "Debe devolver mensaje de error"
