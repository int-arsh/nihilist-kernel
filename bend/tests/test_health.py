import os

os.environ.setdefault("GOOGLE_API_KEY", "test-key")

from app import app  # noqa: E402


def test_health_endpoint():
    client = app.test_client()
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"