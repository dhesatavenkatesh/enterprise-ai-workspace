def test_docs_available(client):
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_available(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "paths" in response.json()
