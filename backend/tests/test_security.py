from backend.app import get_conn
from backend.app import health

def test_get_conn():
    assert get_conn() is not None

def test_health():
    assert health() == {"status": "ok", "db": "up"}