import os

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


@pytest.fixture(scope="module")
def access_token():
    username = os.getenv("AUTH_USERNAME", "admin")
    password = os.getenv("AUTH_PASSWORD", "secret")
    response = client.post(
        "/api/v1/auth/token",
        data={"username": username, "password": password},
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
    assert client.get('/api/v1/ml/features', headers=headers).status_code == 200
    assert client.get('/api/v1/ml/training-data', headers=headers).status_code == 200


def test_ml_predictions(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "predictions": [
            {"book_id": 1, "model": "baseline-v1", "score": 4.3, "label": "buy"},
            {"book_id": 2, "model": "baseline-v1", "score": 2.1, "label": "hold"},
        ]
    }
    response = client.post('/api/v1/ml/predictions', json=payload, headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "accepted"
    assert body["summary"]["received"] == 2
