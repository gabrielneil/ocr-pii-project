import json

import pika


def get_connection():
    """Establishes a connection to RabbitMQ."""
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq")
    )
    return connection


def publish_message(queue_name, message):
    """Publishes a message to the specified RabbitMQ queue."""
    connection = get_connection()
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(
        exchange="", routing_key=queue_name, body=json.dumps(message)
    )
    connection.close()


def consume_message(queue_name, callback):
    """Consumes messages from the specified RabbitMQ queue and passes them to the callback function."""
    connection = get_connection()
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_consume(
        queue=queue_name,
        on_message_callback=lambda ch, method, properties, body: callback(
            ch, method, properties, body
        ),
        auto_ack=True,
    )
    print(f"Waiting for messages in {queue_name}. To exit press CTRL+C")
    channel.start_consuming()
