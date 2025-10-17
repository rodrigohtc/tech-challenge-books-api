import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


@pytest.fixture(scope="module")
def access_token():
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "secret"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]

def test_health():
    r = client.get('/api/v1/health')
    assert r.status_code == 200
    assert r.json()['status'] == 'ok'

def test_routes_exist(access_token):
    # these should exist even if CSV is empty
    headers = {"Authorization": f"Bearer {access_token}"}
    assert client.get('/api/v1/books', headers=headers).status_code == 200
    assert client.get('/api/v1/categories', headers=headers).status_code == 200
    assert client.get('/api/v1/stats/overview', headers=headers).status_code == 200
