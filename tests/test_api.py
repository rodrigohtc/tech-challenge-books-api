import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health():
    r = client.get('/api/v1/health')
    assert r.status_code == 200
    assert r.json()['status'] == 'ok'

def test_routes_exist():
    # these should exist even if CSV is empty
    assert client.get('/api/v1/books').status_code == 200
    assert client.get('/api/v1/categories').status_code == 200
    assert client.get('/api/v1/stats/overview').status_code == 200
