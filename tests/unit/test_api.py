import pytest
from fastapi.testclient import TestClient

from api.entrypoints import app as main


@pytest.fixture
def client():
    app = main.app
    return TestClient(app)


def test_healthcheck(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'message': 'Healthy'}


def test_ping(client):
    response = client.get('/ping')
    assert response.status_code == 200
    assert response.json() == 'pong'


def test_docs(client):
    response = client.get('/docs')
    assert response.status_code == 200


def test_should_return_200_when_data_is_valid(client):
    location = {
        "timestamp": "2017-01-01 13:05:12",
        "lat": 40.701,
        "long": -73.916,
        "accuracy": 11.3000021,
        "speed": 1.3999992,
        "user_id": "a1"
    }

    response = client.put('/location', json=location)

    assert response.status_code == 200


def test_should_return_422_when_missing_timestamp(client):
    # FastAPI automatically handles this as an
    # unprocessable entity, which is actually status code 422
    # (https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/422)
    location = {
        "lat": 40.701,
        "long": -73.916,
        "accuracy": 11.3000021,
        "speed": 1.3999992,
        "user_id": "a1"
    }

    response = client.put('/location', json=location)

    assert response.status_code == 422
