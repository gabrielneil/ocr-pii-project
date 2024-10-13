import base64
import json
from unittest import mock

import pytest

from commons.clients.rabbit_mq import RabbitMQClient
from PerformOCR.src.app import PerformOCRService
from PerformOCR.src.utils import detect_text


@pytest.fixture
def mock_rabbitmq_client(mocker):
    """Fixture to mock the RabbitMQClient."""
    return mocker.patch(
        "mymodule.RabbitMQClient"
    )  # Adjust based on actual module name


# Test the process_image_message method when OCR is successful
def test_process_image_message_success(mocker, mock_rabbitmq_client):
    # Mock detect_text to return bounding boxes
    mock_detect_text = mocker.patch("PerformOCR.src.utils.detect_text")
    mock_detect_text.return_value = [
        mock.Mock(text="Hello", left=10, right=100, top=20, bottom=30),
        mock.Mock(text="World", left=50, right=150, top=70, bottom=100),
    ]

    # Mock RabbitMQClient's publish_message
    mock_publish_message = mock_rabbitmq_client().publish_message

    # Create PerformOCR instance
    ocr_service = PerformOCRService()

    # Mock channel and method (used by pika)
    mock_channel = mock.Mock()
    mock_method = mock.Mock()
    mock_properties = mock.Mock()

    # Mock image data and base64 encoding
    mock_image_data = b"fake_image_data"
    mock_encoded_image = base64.b64encode(mock_image_data).decode("utf-8")
    message_body = json.dumps(
        {
            "img_id": "image_123",
            "image_data": mock_encoded_image,
        }
    )

    # Call process_image_message
    ocr_service.process_image_message(
        mock_channel, mock_method, mock_properties, message_body
    )

    # Assert detect_text was called with the correct image data
    mock_detect_text.assert_called_once_with(mock_image_data)

    # Verify the bounding boxes were serialized correctly
    expected_payload = {
        "img_id": "image_123",
        "bounding_boxes": [
            {
                "text": "Hello",
                "left": 10,
                "right": 100,
                "top": 20,
                "bottom": 30,
            },
            {
                "text": "World",
                "left": 50,
                "right": 150,
                "top": 70,
                "bottom": 100,
            },
        ],
    }

    # Assert that the message was published to the FILTER_PII_QUEUE
    mock_publish_message.assert_called_once_with(
        ocr_service.FILTER_PII_QUEUE, expected_payload
    )


# Test process_image_message handles errors gracefully
def test_process_image_message_error(mocker, mock_rabbitmq_client):
    # Mock detect_text to raise an exception
    mock_detect_text = mocker.patch("PerformOCR.src.utils.detect_text")
    mock_detect_text.side_effect = Exception("OCR failed")

    # Mock RabbitMQClient's publish_message
    mock_publish_message = mock_rabbitmq_client().publish_message

    # Create PerformOCR instance
    ocr_service = PerformOCRService()

    # Mock channel and method (used by pika)
    mock_channel = mock.Mock()
    mock_method = mock.Mock()
    mock_properties = mock.Mock()

    # Mock image data and base64 encoding
    mock_image_data = b"fake_image_data"
    mock_encoded_image = base64.b64encode(mock_image_data).decode("utf-8")
    message_body = json.dumps(
        {
            "img_id": "image_123",
            "image_data": mock_encoded_image,
        }
    )

    # Mock logging to capture the error log
    mock_logging = mocker.patch("builtins.print")

    # Call process_image_message and ensure no exception is raised
    ocr_service.process_image_message(
        mock_channel, mock_method, mock_properties, message_body
    )

    # Assert detect_text was called with the correct image data
    mock_detect_text.assert_called_once_with(mock_image_data)

    # Verify that the error was logged
    mock_logging.assert_called_once_with(
        "Error processing message: OCR failed"
    )

    # Assert publish_message was not called because of the exception
    mock_publish_message.assert_not_called()
