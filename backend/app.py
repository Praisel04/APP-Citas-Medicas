import os
import psycopg
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import uuid


# === Config desde variables de entorno ===
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "appdb")
DB_USER = os.getenv("DB_USER", "appuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "supersecret_dev")

def get_conn():
    # Conexión simple por petición (suficiente para MVP)
    """
    Devuelve una conexión a la base de datos.
    
    La conexión se establece con los valores de configuración
    establecidos en las variables de entorno DB_HOST, DB_PORT,
    DB_NAME, DB_USER y DB_PASSWORD.
    
    La conexión se establece con autocommit=True, lo que significa
    que los cambios se confirmarán automáticamente.
    
    :return: Una conexión a la base de datos.
    :rtype: psycopg2.extensions.connection
    """
    return psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        autocommit=True,
    )

app = Flask(__name__)
CORS(app)  # permite consumir desde tu frontend

@app.get("/api/health")
def health():
    """
    Indica el estado de la aplicación y la conexión a la base de datos.
    
    El estado de la aplicación se indica con el campo "status" y puede tener
    los valores "ok" o "degraded".
    
    La conexión a la base de datos se indica con el campo "db" y puede tener
    los valores "up" o "down". En caso de que el estado sea "degraded", se
    incluye adicionalmente el campo "error" con la descripción del error.
    
    :return: Un objeto JSON con el estado de la aplicación y la conexión a la base de datos.
    :rtype: flask.Response
    """
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1;")
            cur.fetchone()
        return jsonify({"status": "ok", "db": "up"}), 200
    except Exception as e:
        return jsonify({"status": "degraded", "db": "down", "error": str(e)}), 503


# === Obtener citas del usuario ===
@app.route('/citas', methods=['GET'])
def get_citas():
    user_id = request.args.get('user_id')
    rol = request.args.get('rol')

    if not user_id:
        return jsonify({"error": "Falta el parámetro user_id"}), 400

    try:
        conn = get_conn()
        cur = conn.cursor()

        if rol == 'medico':
            cur.execute("""
        SELECT 
            c.id, 
            c.nombre_cita, 
            c.fecha_hora, 
            c.estado, 
            c.created_at, 
            u.nombre AS nombre_paciente
        FROM cita c
        JOIN usuario u ON c.usuario_id = u.id
        ORDER BY c.fecha_hora ASC;
    """)
        elif rol == 'paciente':
            cur.execute("""
        SELECT 
            c.id, 
            c.nombre_cita, 
            c.fecha_hora, 
            c.estado, 
            c.created_at, 
            u.nombre AS nombre_paciente
        FROM cita c
        JOIN usuario u ON c.usuario_id = u.id
        WHERE c.usuario_id = %s
        ORDER BY c.fecha_hora ASC;
    """, (user_id,))

        citas = [
            {
                "id": str(row[0]),
                "nombre_cita": row[1],
                "fecha_hora": row[2],
                "estado": row[3],
                "created_at": row[4],
                "nombre_paciente": row[5]
            }
            for row in cur.fetchall()
        ]

        print("➡️ CITAS DEVUELTAS:", citas)  # 👈 imprime aquí
        
        cur.close()
        conn.close()

        return jsonify(citas), 200

    except Exception as e:
        print("Error en /citas (GET):", e)
        return jsonify({"error": "Error interno del servidor"}), 500


# === Crear una nueva cita ===
@app.route('/citas', methods=['POST'])
def crear_cita():
    data = request.get_json()
    user_id = data.get('user_id')
    nombre_cita = data.get('nombre_cita')
    fecha_hora = data.get('fecha_hora')
    estado = data.get('estado', 'programada')

    if not user_id or not fecha_hora:
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO cita (id, usuario_id, nombre_cita, fecha_hora, estado)
            VALUES (gen_random_uuid(), %s, %s, %s, %s)
            RETURNING id;
        """, (user_id, nombre_cita,fecha_hora, estado))

        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Cita creada correctamente", "cita_id": str(new_id)}), 201

    except Exception as e:
        print("Error en /citas (POST):", e)
        return jsonify({"error": "Error interno del servidor"}), 500


# === Eliminar una cita ===
@app.route('/citas/<cita_id>', methods=['DELETE'])
def eliminar_cita(cita_id):
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({"error": "Falta el parámetro user_id"}), 400

    try:
        conn = get_conn()
        cur = conn.cursor()

        # Solo elimina si pertenece al usuario
        cur.execute("""
            DELETE FROM cita
            WHERE id = %s
            RETURNING id;
        """, (cita_id,))

        deleted = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        if not deleted:
            return jsonify({"error": "Cita no encontrada o no pertenece al usuario"}), 404

        return jsonify({"message": "Cita eliminada correctamente"}), 200

    except Exception as e:
        print("Error en /citas (DELETE):", e)
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Validar que los campos estén presentes
    if not data or not all(k in data for k in ('nombre', 'email', 'password', 'rol')):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    nombre = data['nombre']
    email = data['email']
    password = data['password']
    rol = data['rol']

    try:
        conn = get_conn()
        cur = conn.cursor()

        # Verificar si el correo ya existe
        cur.execute("SELECT id FROM usuario WHERE email = %s;", (email,))
        existing_user = cur.fetchone()

        if existing_user:
            cur.close()
            conn.close()
            return jsonify({"error": "El correo ya está registrado"}), 400

        # Cifrar la contraseña
        password_hash = generate_password_hash(password)

        # Crear un nuevo usuario
        user_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO usuario (id, nombre, email, password_hash, rol)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """, (user_id, nombre, email, password_hash, rol))
        
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            "message": "Usuario registrado correctamente",
            "user_id": user_id,
            "nombre": nombre,
            "email": email,
            "rol": rol  # 👈 Mostramos el valor recibido del frontend
        }), 201



    except Exception as e:
        print("Error en /register:", e)
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not all(k in data for k in ('email', 'password')):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    email = data['email']
    password = data['password']

    try:
        conn = get_conn()
        cur = conn.cursor()

        # Buscar usuario por email
        cur.execute("SELECT id, nombre,password_hash, rol FROM usuario WHERE email = %s;", (email,))
        user = cur.fetchone()

        cur.close()
        conn.close()

        if not user:
            return jsonify({"error": "Correo no encontrado"}), 401

        user_id, nombre, stored_hash, rol = user

        # Verificar la contraseña
        if not check_password_hash(stored_hash, password):
            return jsonify({"error": "Contraseña incorrecta"}), 401

        return jsonify({
            "message": "Inicio de sesión correcto",
            "user_id": str(user_id),
            "nombre" : nombre,
            "rol": rol
        }), 200

    except Exception as e:
        print("Error en /login:", e)
        return jsonify({"error": "Error interno del servidor"}), 500
    
# === EDITAR CITA ===
@app.route('/citas/<cita_id>', methods=['PUT'])
def editar_cita(cita_id):
    data = request.get_json()
    user_id = data.get('user_id')
    nombre_cita = data.get('nombre_cita')
    fecha_hora = data.get('fecha_hora')
    estado = data.get('estado')

    if not user_id:
        return jsonify({"error": "Falta el user_id"}), 400

    try:
        conn = get_conn()
        cur = conn.cursor()

        # Verificar que la cita pertenece al usuario
        cur.execute("SELECT usuario_id FROM cita WHERE id = %s;", (cita_id,))
        result = cur.fetchone()
        if not result:
            return jsonify({"error": "Cita no encontrada"}), 404
        if str(result[0]) != str(user_id):
            return jsonify({"error": "No autorizado"}), 403

        update_fields = []
        values = []
        if nombre_cita:
            update_fields.append("nombre_cita = %s")
            values.append(nombre_cita)
        if fecha_hora:
            update_fields.append("fecha_hora = %s")
            values.append(fecha_hora)
        if estado:
            update_fields.append("estado = %s")
            values.append(estado)

        if not update_fields:
            return jsonify({"error": "No hay cambios para aplicar"}), 400

        values.append(cita_id)
        query = f"UPDATE cita SET {', '.join(update_fields)}, updated_at = now() WHERE id = %s"
        cur.execute(query, tuple(values))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Cita actualizada correctamente"}), 200
    except Exception as e:
        print("Error en /citas (PUT):", e)
        return jsonify({"error": "Error interno del servidor"}), 500

if __name__ == "__main__":
    # para ejecutar sin Gunicorn (desarrollo local opcional)
    app.run(host="0.0.0.0", port=8000)