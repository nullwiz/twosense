import pytest
import requests
import json
import redis
import time
import logging

logging.basicConfig(level=logging.INFO)
api_url = "http://localhost:5000"  # replace with your API url
redis_host = 'localhost'  # replace with your Redis host
redis_port = 6379  # replace with your Redis port


@pytest.fixture
def redis_client():
    client = redis.Redis(host=redis_host, port=redis_port, db=0)
    yield client
    client.flushdb()


def check_db_key(redis_client, user_id):
    keys = redis_client.keys(f"{user_id}*")
    return bool(keys)


def test_should_return_200_and_save_list_to_redis(redis_client):
    location = {
        "timestamp": "2017-01-01 13:05:12",
        "lat": 40.701,
        "long": -73.916,
        "accuracy": 11.3000021,
        "speed": 1.3999992,
        "user_id": "a1"
    }

    # Send the request to the /location endpoint
    response = requests.put(f'{api_url}/location', json=location)
    assert response.status_code == 200

    # Wait a bit to make sure the key has time to be saved in the database
    time.sleep(1)

    # Check that a new key has been saved to the database
    assert check_db_key(redis_client, location['user_id'])


def test_should_not_save_same_timestamp_to_redis_set(redis_client):
    location = {
        "timestamp": "2017-01-01 13:05:12",
        "lat": 40.701,
        "long": -73.916,
        "accuracy": 11.3000021,
        "speed": 1.3999992,
        "user_id": "a1"
    }

    # Send the request to the /location endpoint twice with the same timestamp
    response1 = requests.put(f'{api_url}/location', json=location)
    response2 = requests.put(f'{api_url}/location', json=location)
    response3 = requests.put(f'{api_url}/location', json=location)

    # Check that both requests were successful
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response3.status_code == 200

    # Wait a bit to make sure the key has time to be saved in the database
    time.sleep(1)

    # Check that only one key has been saved to the database
    keys = redis_client.keys(f"{location['user_id']}:*")

    logger = logging.getLogger(__name__)

    assert len(keys) == 1


def test_should_not_save_same_timestamp_to_redis_list(redis_client):
    location = {
        "timestamp": "2017-01-01 13:05:12",
        "lat": 40.701,
        "long": -73.916,
        "accuracy": 11.3000021,
        "speed": 1.3999992,
        "user_id": "a1"
    }

    # Send the request to the /location endpoint twice with the same timestamp
    response1 = requests.put(f'{api_url}/location', json=location)
    response2 = requests.put(f'{api_url}/location', json=location)
    response3 = requests.put(f'{api_url}/location', json=location)

    # Check that both requests were successful
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response3.status_code == 200

    # Wait a bit to make sure the key has time to be saved in the database
    time.sleep(1)

    # Check that only one key has been saved to the database
    list = redis_client.lrange(location['user_id'], 0, -1)
    assert len(list) == 1


def test_set_saved_with_key(redis_client):
    location = {
        "timestamp": "2017-01-01 13:05:12",
        "lat": 40.701,
        "long": -73.916,
        "accuracy": 11.3000021,
        "speed": 1.3999992,
        "user_id": "a1"
    }

    # Send the request to the /location endpoint
    response = requests.put(f'{api_url}/location', json=location)
    assert response.status_code == 200

    # Wait a bit to make sure the key has time to be saved in the database
    time.sleep(1)

    redis_set = redis_client.smembers(f"{location['user_id']}:timestamps")

    # its in UTC
    assert redis_set == {b'2017-01-01T18:05:12'}
