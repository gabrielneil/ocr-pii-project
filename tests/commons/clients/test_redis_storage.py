import json
from unittest import mock

import pytest

from commons.clients.redis_storage import RedisStorage


# Test the `store` method
def test_store_method(mocker):
    # Mock the Redis client
    mock_redis = mocker.patch("redis.Redis")

    # Create RedisStorage instance with mocked Redis client
    storage = RedisStorage(host="localhost", port=6379, db=0)

    # Call the `store` method
    storage.store(
        key="img_id", data_type="bounding_boxes", data={"box": "data"}
    )

    # Assert that Redis `set` was called with the correct arguments
    mock_redis().set.assert_called_once_with(
        "img_id:bounding_boxes", json.dumps({"box": "data"})
    )


# Test the `retrieve` method when data is found
def test_retrieve_method_with_data(mocker):
    # Mock the Redis client and its `get` method
    mock_redis = mocker.patch("redis.Redis")
    mock_redis().get.return_value = json.dumps({"box": "data"})

    # Create RedisStorage instance with mocked Redis client
    storage = RedisStorage(host="localhost", port=6379, db=0)

    # Call the `retrieve` method
    result = storage.retrieve(key="img_id", data_type="bounding_boxes")

    # Assert that Redis `get` was called with the correct arguments
    mock_redis().get.assert_called_once_with("img_id:bounding_boxes")

    # Assert the result is correctly deserialized
    assert result == {"box": "data"}


# Test the `retrieve` method when data is not found
def test_retrieve_method_no_data(mocker):
    # Mock the Redis client and its `get` method to return None
    mock_redis = mocker.patch("redis.Redis")
    mock_redis().get.return_value = None

    # Create RedisStorage instance with mocked Redis client
    storage = RedisStorage(host="localhost", port=6379, db=0)

    # Call the `retrieve` method
    result = storage.retrieve(key="img_id", data_type="bounding_boxes")

    # Assert that Redis `get` was called with the correct arguments
    mock_redis().get.assert_called_once_with("img_id:bounding_boxes")

    # Assert that the result is None
    assert result is None


# Test the `delete` method
def test_delete_method(mocker):
    # Mock the Redis client
    mock_redis = mocker.patch("redis.Redis")

    # Create RedisStorage instance with mocked Redis client
    storage = RedisStorage(host="localhost", port=6379, db=0)

    # Call the `delete` method
    storage.delete(key="img_id")

    # Assert that Redis `delete` was called twice with the correct arguments
    mock_redis().delete.assert_any_call("img_id:bounding_boxes")
    mock_redis().delete.assert_any_call("img_id:pii_terms")
    assert mock_redis().delete.call_count == 2
