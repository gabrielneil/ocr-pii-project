import json
import os
from typing import List

from commons.clients.rabbit_mq import RabbitMQClient
from commons.clients.redis_storage import RedisStorage


class FilterPIIService:
    """
    A service to filter bounding boxes containing PII (Personally Identifiable Information) from OCR results.

    The FilterPIIService listens to a RabbitMQ queue for incoming messages containing bounding boxes or PII terms,
    processes them, and publishes filtered results to another queue after excluding any bounding boxes containing PII.

    Attributes
    ----------
    FILTER_PII_QUEUE : str
        The name of the queue from which the service consumes messages.
    FILTERED_QUEUE : str
        The name of the queue to which the filtered bounding boxes are published.
    rabbitmq_client : RabbitMQClient
        A RabbitMQ client used for consuming and publishing messages.
    redis_storage : RedisStorage
        A Redis client used for storing and retrieving bounding boxes and PII terms.
    """

    FILTER_PII_QUEUE = "filter_pii_queue"
    FILTERED_QUEUE = "filtered_queue"

    def __init__(
        self,
        connection_params="localhost",
        redis_host="localhost",
        redis_port=6379,
    ):
        """
        Initializes the FilterPIIService with a RabbitMQ client and Redis storage.

        Parameters
        ----------
        connection_params : str, optional
            The connection string to connect to RabbitMQ (default is "localhost").
        redis_host : str, optional
            The hostname or IP address of the Redis server (default is "localhost").
        redis_port : int, optional
            The port number on which the Redis server is listening (default is 6379).
        """
        self.rabbitmq_client = RabbitMQClient(
            connection_params, self.FILTER_PII_QUEUE
        )
        self.redis_storage = RedisStorage(host=redis_host, port=redis_port)

    def _filter_bounding_boxes(
        self, bounding_boxes, pii_terms: List[str]
    ) -> dict:
        """
        Filters bounding boxes to exclude those that contain PII terms.

        This method iterates over bounding boxes and excludes any that contain the specified PII terms in the text.

        Parameters
        ----------
        bounding_boxes : list of dict
            A list of bounding box dictionaries, each containing details like text and coordinates.
        pii_terms : list of str
            A list of PII terms to filter out from the bounding boxes.

        Returns
        -------
        list of dict
            A filtered list of bounding boxes excluding any that contain PII terms.
        """
        return [
            box
            for box in bounding_boxes
            if not any(pii in box["text"] for pii in pii_terms)
        ]

    def _process_message(self, ch, method, properties, body):
        """
        Processes incoming messages from the RabbitMQ queue.

        The method determines if the message contains bounding boxes or PII terms, stores them in Redis, and
        once both are available, filters the bounding boxes to exclude those containing PII terms. The filtered
        bounding boxes are then published to another RabbitMQ queue.

        Parameters
        ----------
        ch : object
            The channel object provided by RabbitMQ when consuming messages.
        method : object
            The delivery method used by RabbitMQ for the message.
        properties : object
            The properties of the RabbitMQ message.
        body : bytes
            The body of the RabbitMQ message, which contains either bounding boxes or PII terms in JSON format.
        """
        try:
            message = json.loads(body)
            img_id = message["img_id"]

            print(f"Processing message for img_id: {img_id}")

            # Infer the message type based on keys
            if "bounding_boxes" in message:
                print(f"Message for img_id {img_id} contains bounding_boxes")
                self.redis_storage.store(
                    img_id, "bounding_boxes", message["bounding_boxes"]
                )

                # Try to retrieve pii_terms from Redis
                pii_terms = self.redis_storage.retrieve(img_id, "pii_terms")
                bounding_boxes = message["bounding_boxes"]

            elif "pii_terms" in message:
                print(f"Message for img_id {img_id} contains pii_terms")
                self.redis_storage.store(
                    img_id, "pii_terms", message["pii_terms"]
                )

                # Try to retrieve bounding_boxes from Redis
                bounding_boxes = self.redis_storage.retrieve(
                    img_id, "bounding_boxes"
                )
                pii_terms = message["pii_terms"]

            else:
                print(
                    f"Unknown message type for img_id {img_id}, discarding message."
                )
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            # If both bounding_boxes and pii_terms are available, proceed with filtering
            if bounding_boxes and pii_terms:
                filtered_boxes = self._filter_bounding_boxes(
                    bounding_boxes, pii_terms
                )
                payload = {"img_id": img_id, "filtered_boxes": filtered_boxes}

                self.rabbitmq_client.publish_message(
                    self.FILTERED_QUEUE, payload
                )
                print(
                    f"Filtered bounding boxes for img_id {img_id} and sent to filtered_queue"
                )

                print(f"Payload final result: {payload}")

                # Clean up Redis as the job is completed
                self.redis_storage.delete(img_id)

            # Acknowledge the message as successfully processed
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print(f"Error processing message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def start(self):
        """
        Start the Filter PII Service to listen for OCR and PII messages.

        This method begins consuming messages from the `FILTER_PII_QUEUE` and processes them
        using the `_process_message` method.

        Notes
        -----
        This method runs indefinitely, consuming and processing messages from the queue.
        """
        self.rabbitmq_client.start(self._process_message)
        print(
            f"Service is running and listening for messages on {self.FILTER_PII_QUEUE}..."
        )


# Usage
if __name__ == "__main__":
    connection_params = os.getenv("RABBITMQ_HOST", "rabbitmq")
    redis_host = os.getenv("REDIS_HOST", "redis")
    filter_pii_service = FilterPIIService(connection_params, redis_host)
    filter_pii_service.start()
