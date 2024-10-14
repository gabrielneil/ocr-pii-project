import json
from unittest import mock

import pytest

from FilterPII.src.app import FilterPIIService


# Define fixture to mock RabbitMQClient
@pytest.fixture
def mock_rabbitmq(mocker):
    # return mocker.patch("commons.clients.rabbit_mq.RabbitMQClient")
    return mocker.patch("FilterPII.src.app.RabbitMQClient")


# Define fixture to mock RedisStorage
@pytest.fixture
def mock_redis(mocker):
    return mocker.patch("FilterPII.src.app.RedisStorage")


# Test _filter_bounding_boxes method
def test_filter_bounding_boxes(mock_redis, mock_rabbitmq):
    service = FilterPIIService()

    bounding_boxes = [
        {"text": "Alice", "left": 10, "right": 100, "top": 20, "bottom": 30},
        {"text": "World", "left": 50, "right": 150, "top": 70, "bottom": 100},
    ]
    pii_terms = ["Alice"]

    # Call the method
    result = service._filter_bounding_boxes(bounding_boxes, pii_terms)

    # Check that the box with "Alice" is excluded
    expected_result = [
        {"text": "World", "left": 50, "right": 150, "top": 70, "bottom": 100}
    ]
    assert result == expected_result


# Test _process_message method when message contains bounding boxes
def test_process_message_bounding_boxes(mock_redis, mock_rabbitmq, mocker):
    # Initialize the service
    service = FilterPIIService()

    # Mock the Redis store and retrieve methods
    mock_redis.return_value.retrieve.return_value = (
        None  # No PII terms stored yet
    )

    # Mock the message body
    message_body = {
        "img_id": "image_123",
        "bounding_boxes": [
            {
                "text": "Hello",
                "left": 10,
                "right": 100,
                "top": 20,
                "bottom": 30,
            }
        ],
    }

    # Call _process_message
    service._process_message(
        mock.Mock(),
        mock.Mock(),
        mock.Mock(),
        json.dumps(message_body).encode(),
    )

    # Verify Redis store was called correctly
    mock_redis.return_value.store.assert_called_once_with(
        "image_123", "bounding_boxes", message_body["bounding_boxes"]
    )

    # Verify that it didn't proceed to publish since PII terms are missing
    mock_rabbitmq.return_value.publish_message.assert_not_called()


# Test _process_message method when message contains PII terms
def test_process_message_pii_terms(mock_redis, mock_rabbitmq, mocker):
    # Initialize the service
    service = FilterPIIService()

    # Mock Redis store and retrieve methods
    mock_redis.return_value.retrieve.return_value = [
        {"text": "Hello", "left": 10, "right": 100, "top": 20, "bottom": 30}
    ]  # Bounding boxes already stored

    # Mock the message body
    message_body = {"img_id": "image_123", "pii_terms": ["Hello"]}

    # Call _process_message
    service._process_message(
        mock.Mock(),
        mock.Mock(),
        mock.Mock(),
        json.dumps(message_body).encode(),
    )

    # Verify Redis store was called correctly
    mock_redis.return_value.store.assert_called_once_with(
        "image_123", "pii_terms", message_body["pii_terms"]
    )

    # Verify the filtered bounding boxes were published
    expected_payload = {"img_id": "image_123", "filtered_boxes": []}
    mock_rabbitmq.return_value.publish_message.assert_called_once_with(
        service.FILTERED_QUEUE, expected_payload
    )


# Test _process_message method with an unknown message type
def test_process_message_unknown_type(mock_redis, mock_rabbitmq, mocker):
    # Initialize the service
    service = FilterPIIService()

    # Mock the message body with unknown content
    message_body = {"img_id": "image_123", "unknown_key": "some_value"}

    # Call _process_message
    ch_mock = mock.Mock()
    method_mock = mock.Mock()
    service._process_message(
        ch_mock, method_mock, mock.Mock(), json.dumps(message_body).encode()
    )

    # Verify the message is acknowledged without processing
    ch_mock.basic_ack.assert_called_once_with(
        delivery_tag=method_mock.delivery_tag
    )
