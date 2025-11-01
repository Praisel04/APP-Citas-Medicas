from flask import Flask, jsonify, request
from copy import deepcopy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

app = Flask(__name__)

mock_db = {}


def reset_mock_db():
    """Reinicia la base de datos simulada antes de cada test."""
    global mock_db
    mock_db = deepcopy({
        "usuario": [
            {
                "id": "11111111-1111-1111-1111-111111111111",
                "nombre": "Ana García",
                "email": "ana@example.com",
                "password_hash": generate_password_hash("1234"),
                "rol": "paciente",
                "created_at": "2025-10-28T10:00:00Z",
                "updated_at": "2025-10-28T10:00:00Z",
            },
            {
                "id": "22222222-2222-2222-2222-222222222222",
                "nombre": "Dr. López",
                "email": "drlopez@example.com",
                "password_hash": generate_password_hash("abcd"),
                "rol": "medico",
                "created_at": "2025-10-28T10:00:00Z",
                "updated_at": "2025-10-28T10:00:00Z",
            },
        ],
        "cita": [
            {
                "id": "33333333-3333-3333-3333-333333333333",
                "usuario_id": "11111111-1111-1111-1111-111111111111",
                "nombre_cita": "Chequeo general",
                "fecha_hora": "2025-11-01T09:00:00Z",
                "estado": "programada",
                "created_at": "2025-10-28T10:00:00Z",
                "updated_at": "2025-10-28T10:00:00Z",
            },
            {
                "id": "44444444-4444-4444-4444-444444444444",
                "usuario_id": "11111111-1111-1111-1111-111111111111",
                "nombre_cita": "Revisión resultados",
                "fecha_hora": "2025-11-15T10:30:00Z",
                "estado": "programada",
                "created_at": "2025-10-28T10:00:00Z",
                "updated_at": "2025-10-28T10:00:00Z",
            },
        ],
    })


# ------------------------------
# ENDPOINTS DE USUARIOS
# ------------------------------

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Validar campos
    if not data or not all(k in data for k in ('nombre', 'email', 'password', 'rol')):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    nombre = data['nombre']
    email = data['email']
    password = data['password']
    rol = data['rol']

    # Verificar si el correo ya existe
    if any(u['email'] == email for u in mock_db['usuario']):
        return jsonify({"error": "El correo ya está registrado"}), 400

    # Crear usuario
    new_user = {
        "id": str(uuid.uuid4()),
        "nombre": nombre,
        "email": email,
        "password_hash": generate_password_hash(password),
        "rol": rol,
        "created_at": "2025-10-28T10:00:00Z",
        "updated_at": "2025-10-28T10:00:00Z",
    }

    mock_db['usuario'].append(new_user)

    return jsonify({
        "message": "Usuario registrado correctamente",
        "user_id": new_user["id"],
        "nombre": nombre,
        "email": email,
        "rol": rol
    }), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not all(k in data for k in ('email', 'password')):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    email = data['email']
    password = data['password']

    # Buscar usuario
    user = next((u for u in mock_db['usuario'] if u['email'] == email), None)
    if not user:
        return jsonify({"error": "Correo no encontrado"}), 401

    # Verificar contraseña
    if not check_password_hash(user['password_hash'], password):
        return jsonify({"error": "Contraseña incorrecta"}), 401

    return jsonify({
        "message": "Inicio de sesión correcto",
        "user_id": user['id'],
        "nombre": user['nombre'],
        "rol": user['rol']
    }), 200


# ------------------------------
# ENDPOINTS DE CITAS (de tu mock original)
# ------------------------------

@app.route("/citas", methods=["GET"])
def get_citas():
    return jsonify(mock_db["cita"]), 200


@app.route("/citas", methods=["POST"])
def crear_cita():
    data = request.get_json()
    nueva_cita = {
        "id": str(uuid.uuid4()),
        "usuario_id": data["usuario_id"],
        "nombre_cita": data["nombre_cita"],
        "fecha_hora": data["fecha_hora"],
        "estado": "programada",
        "created_at": "2025-10-28T10:00:00Z",
        "updated_at": "2025-10-28T10:00:00Z",
    }
    mock_db["cita"].append(nueva_cita)
    return jsonify(nueva_cita), 201


@app.route("/citas/<id>", methods=["PUT"])
def editar_cita(id):
    data = request.get_json()
    for cita in mock_db["cita"]:
        if cita["id"] == id:
            cita.update(data)
            return jsonify({"message": "Cita actualizada", "cita": cita}), 200
    return jsonify({"error": "Cita no encontrada"}), 404


@app.route("/citas/<id>", methods=["DELETE"])
def eliminar_cita(id):
    for i, cita in enumerate(mock_db["cita"]):
        if cita["id"] == id:
            del mock_db["cita"][i]
            return jsonify({"message": "Cita eliminada"}), 200
    return jsonify({"error": "Cita no encontrada"}), 404


# ------------------------------
# EJECUCIÓN LOCAL
# ------------------------------
if __name__ == "__main__":
    reset_mock_db()
    app.run(debug=True)
