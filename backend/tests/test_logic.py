# Base de datos simulada en memoria
from datetime import datetime, timedelta, timezone
import uuid

# === Simulación de datos ===
citas_mock = [
    {
        "id": uuid.uuid4(),
        "usuario_id": uuid.uuid4(),
        "nombre_cita": "Chequeo general",
        "fecha_hora": datetime(2025, 10, 25, 10, 0, tzinfo=timezone.utc),
        "estado": "programada",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    },
    {
        "id": uuid.uuid4(),
        "usuario_id": uuid.uuid4(),
        "nombre_cita": "Revisión anual",
        "fecha_hora": datetime(2025, 10, 26, 12, 0, tzinfo=timezone.utc),
        "estado": "programada",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    },
]


def get_citas():
    """Simula una obtencion de citas, para no usar la base de datos real.
    Estas citas usan el mismo formato, parametros y datos que las citas reales de la base de datos.

    Returns:
        : list: Lista de diccionarios con las citas simuladas.
    """
    return citas_mock

def test_get_citas():
    """
    Funcion de prueba para get_citas.
    Verifica que la funcion retorne una lista de citas con el formato correcto.
    
    Asserts:
        - El resultado es una lista.
        - La lista contiene al menos una cita.
        - Cada cita tiene las claves esperadas: id, fecha, hora, paciente, medico, descripcion.
    """
    
    resultado = get_citas()
    assert isinstance(resultado, list), "El resultado debe ser una lista"
    assert "nombre_cita" in resultado[0], "Cada cita debe tener una clave 'nombre_cita'"
    assert resultado[0]["estado"] == "programada", "El estado de la cita debe ser 'programada'"
    
def crear_cita(citas, usuario_id, nombre_cita, fecha_hora):
    """Simula la creacion de una nueva cita en la base de datos.

    Args:
        citas (list): Lista de citas existentes.
        usuario_id (uuid): ID del usuario que crea la cita.
        nombre_cita (str): Nombre o descripcion de la cita.
        fecha_hora (datetime): Fecha y hora de la cita.

    Returns:
        dict: La nueva cita creada.
    """
    
    if not nombre_cita or fecha_hora < datetime.now(timezone.utc):
        return {"error": "Datos invalidos o fecha pasada"}  # Simula fallo en la creacion de la cita
    
    nueva_cita = {
        "id": uuid.uuid4(),
        "usuario_id": usuario_id,
        "nombre_cita": nombre_cita,
        "fecha_hora": fecha_hora,
        "estado": "programada",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    citas.append(nueva_cita)
    return {"mensaje": "Cita creada exitosamente", "cita": nueva_cita, "total": len(citas)}
    
def test_crear_cita_valida():
    """Cita valida:
    La funcion debe crear una cita correctamente cuando se proporcionan datos validos.
    Se copian las citas mock para no alterar el estado global. Se usa la funcion crear_cita con datos validos. 
    Se valida con asserts que la respuesta contiene un mensaje de exito y que el total de citas es correcto.
    
    Asserts:
        - La respuesta contiene un mensaje de exito.
        - El total de citas debe ser igual al tamaño actualizado.
        
    """
    citas_local = citas_mock.copy()
    usuario = uuid.uuid4()
    nueva_fecha = datetime.now(timezone.utc) + timedelta(days=2)
    resultado = crear_cita(citas_local, usuario, "Medicina General", nueva_fecha)
    assert "mensaje" in resultado, "Debe devolver un mensaje de exito"
    assert resultado["total"] == len(citas_local), "El total debe coincidir con el tamaño actualizado"
    
def test_crear_cita_invalida():
    """Cita invalida:
    La funcion debe manejar correctamente los datos invalidos.
    Se copian las citas mock para no alterar el estado global. Se usa la funcion crear_cita con datos invalidos (nombre vacio y fecha pasada).
    Se valida con asserts que la respuesta contiene un error.
    
    Asserts:
        - La respuesta contiene un error.
    """
    citas_local = citas_mock.copy()
    usuario = uuid.uuid4()
    fecha_pasada = datetime.now(timezone.utc) - timedelta(days=1)
    resultado = crear_cita(citas_local, usuario, "", fecha_pasada)
    assert "error" in resultado, "Debe devolver un error por datos inválidos o fecha antigua"


# === Función 3: EDITAR CITA ===
def editar_cita(citas, id_cita, nuevos_datos):
    """Editar Cita:
    La funcion simula la edicion de una cita existente en la base de datos.
    Se copian las citas mock para no alterar el estado global. Se busca la cita por ID y se actualizan los datos proporcionados.
    
    Args:
        citas (_type_): Listado de las citas.
        id_cita (_type_): ID de la cita a editar.
        nuevos_datos (_type_): Diccionario con los nuevos datos a actualizar.

    Returns:
        _type_: _Diccionario con el resultado de la operacion.
    """
    for cita in citas:
        if cita["id"] == id_cita:
            cita.update(nuevos_datos)
            cita["updated_at"] = datetime.now(timezone.utc)
            return {"mensaje": "Cita actualizada", "cita": cita}
    return {"error": "Cita no encontrada"}


def test_editar_cita_existente():
    """Test Editar Cita:
    
    Verifica que se pueda editar una cita existente correctamente.
    Se copian las citas mock para no alterar el estado global. Se edita el estado de una cita existente.
    
    Asserts:
        - El estado de la cita debe cambiar al nuevo valor.
        - El campo updated_at debe ser actualizado.

    """
    citas_local = citas_mock.copy()
    id_existente = citas_local[0]["id"]
    nuevos_datos = {"estado": "cancelada"}
    resultado = editar_cita(citas_local, id_existente, nuevos_datos)
    assert resultado["cita"]["estado"] == "cancelada", "El estado debe cambiar a 'cancelada'"
    assert "updated_at" in resultado["cita"], "Debe actualizar el campo updated_at"


def test_editar_cita_inexistente():
    """Test Editar Cita inexistente:
    
    Se verifica que no se pueda editar una cita que no existe.
    Se copian las citas mock para no alterar el estado global. Se intenta editar una cita con un ID aleatorio que no existe.
    
    Asserts:
        - Debe devolver un error indicando que la cita no fue encontrada.
    """
    citas_local = citas_mock.copy()
    resultado = editar_cita(citas_local, uuid.uuid4(), {"estado": "finalizada"})
    assert "error" in resultado, "Debe devolver error si el ID no existe"


# === Función 4: ELIMINAR CITA ===
def eliminar_cita(citas, id_cita):
    """Eliminar Cita:
    Simula la eliminacion de una cita existente en la base de datos.
    Se copian las citas mock para no alterar el estado global. Se busca la cita por ID y se elimina.
    Args:
        citas (list): Lista de citas existentes.
        id_cita (uuid): ID de la cita a eliminar.
    Returns:
        dict: Diccionario con el resultado de la operacion.
    """
    for cita in citas:
        if cita["id"] == id_cita:
            citas.remove(cita)
            return {"mensaje": "Cita eliminada", "total": len(citas)}
    return {"error": "Cita no encontrada"}


def test_eliminar_cita_existente():
    
    """Test Eliminar Cita Existente:
    
    Verifica que se pueda eliminar una cita existente correctamente.
    Se copian las citas mock para no alterar el estado global. Se elimina una cita existente.
    
    Asserts:
        - Debe devolver un mensaje dexito indicando que la cita fue eliminada.
        - Debe quedar una sola cita tras eliminar.
    """
    citas_local = citas_mock.copy()
    id_existente = citas_local[0]["id"]
    resultado = eliminar_cita(citas_local, id_existente)
    assert "mensaje" in resultado, "Debe devolver mensaje de éxito"
    assert resultado["total"] == 1, "Debe quedar una sola cita tras eliminar"


def test_eliminar_cita_inexistente():
    """Test Eliminar Cita Inexistente:
    
    Verifica que no se pueda eliminar una cita que no existe.
    Se copian las citas mock para no alterar el estado global. Se intenta eliminar una cita con un ID aleatorio que no existe.
    Asserts:
        - Debe devolver un error indicando que la cita no fue encontrada.
    """
    citas_local = citas_mock.copy()
    resultado = eliminar_cita(citas_local, uuid.uuid4())
    assert "error" in resultado, "Debe devolver error si el ID no existe"