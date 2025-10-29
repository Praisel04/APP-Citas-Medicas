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


def get_citas_count(client):
    """Devuelve el número actual de citas consultando el endpoint."""
    res = client.get("/citas")
    return len(res.get_json())


def test_get_citas(client):
    res = client.get("/citas")
    data = res.get_json()
    assert res.status_code == 200
    assert len(data) == 2
    assert data[0]["nombre_cita"] == "Chequeo general"


def test_crear_cita(client):
    count_before = get_citas_count(client)

    nueva_cita = {
        "usuario_id": "11111111-1111-1111-1111-111111111111",
        "nombre_cita": "Consulta dermatología",
        "fecha_hora": "2025-11-20T11:00:00Z"
    }
    res = client.post("/citas", json=nueva_cita)
    data = res.get_json()

    count_after = get_citas_count(client)

    assert res.status_code == 201
    assert data["nombre_cita"] == "Consulta dermatología"
    assert count_after == count_before + 1


def test_editar_cita(client):
    # Obtener una cita existente
    res = client.get("/citas")
    cita_id = res.get_json()[0]["id"]

    # Editar
    res = client.put(f"/citas/{cita_id}", json={"estado": "completada"})
    data = res.get_json()

    assert res.status_code == 200
    assert data["cita"]["estado"] == "completada"


def test_eliminar_cita(client):
    res = client.get("/citas")
    cita_id = res.get_json()[0]["id"]

    count_before = len(res.get_json())

    res = client.delete(f"/citas/{cita_id}")
    count_after = get_citas_count(client)

    assert res.status_code == 200
    assert count_after == count_before - 1
