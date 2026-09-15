from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_is_not_cacheable() -> None:
    response = client.get("/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "aura-api", "version": "0.2.0"}
    assert response.headers["cache-control"] == "no-store"
