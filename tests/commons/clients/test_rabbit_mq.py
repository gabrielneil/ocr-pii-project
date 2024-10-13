import json
from unittest import mock

import pika
import pytest

from commons.clients.rabbit_mq import RabbitMQClient


# Test that RabbitMQClient retries connections and initializes successfully
def test_rabbitmq_client_initializes_successfully(mocker):
    # Mock the pika.BlockingConnection
    mock_pika = mocker.patch("pika.BlockingConnection")
    mock_channel = mocker.Mock()
    mock_pika.return_value.channel.return_value = mock_channel

    # Test initializing the client
    client = RabbitMQClient(
        connection_parameters="localhost", queue_id="test_queue"
    )

    # Assert that queue_declare was called correctly
    mock_channel.queue_declare.assert_called_with("test_queue", durable=True)


# Test that RabbitMQClient retries on connection failure
def test_rabbitmq_client_retries_on_failure(mocker):
    # Mock pika to raise AMQPConnectionError on the first two attempts, and then succeed
    mock_pika = mocker.patch("pika.BlockingConnection")
    mock_pika.side_effect = [
        pika.exceptions.AMQPConnectionError,
        pika.exceptions.AMQPConnectionError,
        mock.Mock(),
    ]

    mock_channel = mock.Mock()
    mock_pika.return_value.channel.return_value = mock_channel

    # Test that RabbitMQClient retries and eventually succeeds
    client = RabbitMQClient(
        connection_parameters="localhost", queue_id="test_queue"
    )

    # Assert that pika.BlockingConnection was called 3 times (2 failures + 1 success)
    assert mock_pika.call_count == 3


# Test that the publish_message method works as expected
def test_publish_message(mocker):
    # Mock the pika connection and channel
    mock_pika = mocker.patch("pika.BlockingConnection")
    mock_channel = mock.Mock()
    mock_pika.return_value.channel.return_value = mock_channel

    # Create RabbitMQClient instance
    client = RabbitMQClient(
        connection_parameters="localhost", queue_id="test_queue"
    )

    # Test publishing a message
    client.publish_message(
        queue_id="test_queue", message={"msg": "test_message"}
    )

    # Assert that basic_publish was called with the correct arguments
    mock_channel.basic_publish.assert_called_once_with(
        exchange="",
        routing_key="test_queue",
        body=json.dumps({"msg": "test_message"}),
    )


# Test that start method sets up the consumer and starts consuming messages
def test_start_consuming(mocker):
    # Mock pika connection and channel
    mock_pika = mocker.patch("pika.BlockingConnection")
    mock_channel = mock.Mock()
    mock_pika.return_value.channel.return_value = mock_channel

    # Create RabbitMQClient instance
    client = RabbitMQClient(
        connection_parameters="localhost", queue_id="test_queue"
    )

    # Mock a message processing callback
    mock_process_message = mock.Mock()

    # Start consuming messages
    client.start(process_message=mock_process_message)

    # Assert that basic_consume was called correctly
    mock_channel.basic_consume.assert_called_once_with(
        queue="test_queue",
        on_message_callback=mock_process_message,
        auto_ack=False,
    )

    # Assert that start_consuming was called
    mock_channel.start_consuming.assert_called_once()
