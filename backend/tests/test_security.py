from backend.app import get_conn
import psycopg2

def test_health():
        try:
            with get_conn() as conn, conn.cursor() as cur:
                cur.execute("SELECT 1;")
                cur.fetchone()
            assert {"status": "ok", "db": "up"}, 200
        
        except Exception as e:
            assert {"status": "degraded", "db": "down", "error": str(e)}, 503