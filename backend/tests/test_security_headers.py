def test_request_id_header(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "x-request-id" in response.headers
