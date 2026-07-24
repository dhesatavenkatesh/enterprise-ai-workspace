def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert "message" in payload


def test_system_health(client):
    response = client.get("/system/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
