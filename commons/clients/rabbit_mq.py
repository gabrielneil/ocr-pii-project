import json
import time

import pika


class RabbitMQClient:
    """
    A client to interact with RabbitMQ for consuming and publishing messages.

    The RabbitMQClient establishes a connection to a RabbitMQ broker, declares a queue, and
    provides methods to consume and publish messages to/from that queue. It includes a retry
    mechanism to handle connection failures.
    """

    def __init__(self, connection_parameters: str, queue_id: str = None):
        """
        Initializes the RabbitMQClient and establishes a connection to RabbitMQ.

        Tries to establish a connection to the RabbitMQ broker and declares a queue.
        In case of a connection failure, the client will retry up to 3 times with a 5-second delay.

        Parameters
        ----------
        connection_parameters : str
            The connection string to connect to the RabbitMQ broker.
        queue_id : str, optional
            The ID of the queue to interact with (default is None).

        Raises
        ------
        pika.exceptions.AMQPConnectionError
            If the client fails to connect to RabbitMQ after 3 attempts.
        """
        for attempt in range(3):
            try:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(connection_parameters)
                )
                self.channel = self.connection.channel()

                self.channel.queue_declare(queue_id, durable=True)
                self._queue_id = queue_id

            except pika.exceptions.AMQPConnectionError as e:
                print(
                    f"Attempt {attempt + 1}: Could not connect to RabbitMQ. Retrying in 5 seconds..."
                )
                time.sleep(5)

    def start(self, process_message):
        """
        Starts consuming messages from the queue and processes each message using the provided callback.

        This method listens for incoming messages from the queue (`_queue_id`) and processes
        them using the `process_message` callback. It does not return, as it continuously listens
        for messages until stopped.

        Parameters
        ----------
        process_message : function
            A callback function to process each received message. The function should accept three arguments:
            `ch` (channel), `method`, and `body` (the message content).


        """
        self.channel.basic_consume(
            queue=self._queue_id,
            on_message_callback=process_message,
            auto_ack=False,
        )
        print("Service is running and listening for messages...")
        self.channel.start_consuming()

    def publish_message(self, queue_id: str, message: dict):
        """
        Publishes a message to the specified RabbitMQ queue.

        The message is serialized to JSON format and sent to the RabbitMQ queue (`queue_id`).

        Parameters
        ----------
        queue_id : str
            The ID of the RabbitMQ queue to which the message should be published.
        message : dict
            The message to be published, which will be serialized as a JSON string.
        """
        self.channel.basic_publish(
            exchange="", routing_key=queue_id, body=json.dumps(message)
        )
