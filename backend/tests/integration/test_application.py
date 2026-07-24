from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_openapi_document_is_available() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200

    payload = response.json()

    assert "info" in payload
    assert "paths" in payload
