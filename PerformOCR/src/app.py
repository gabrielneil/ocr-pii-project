import base64
import json
import os

from commons.clients.rabbit_mq import RabbitMQClient
from PerformOCR.src.utils import detect_text


class PerformOCRService:
    """
    Perform OCR on images received via a message queue and publish the bounding boxes.

    The PerformOCR class listens to a RabbitMQ queue for incoming image messages,
    decodes the image, runs OCR on it, and sends the detected bounding boxes to another queue for further processing.

    """

    OCR_QUEUE = "ocr_queue"
    FILTER_PII_QUEUE = "filter_pii_queue"

    def __init__(
        self,
        connection_params="localhost",
    ):
        """
        Initializes the PerformOCR class with a RabbitMQ connection.

        Parameters
        ----------
        connection_params : str, optional
            The connection string to connect to RabbitMQ (default is "localhost").
        """
        self.rabbitmq_client = RabbitMQClient(
            connection_params, self.OCR_QUEUE
        )

    def process_image_message(self, ch, method, properties, body):
        """
        Processes an incoming RabbitMQ message, decodes the image, runs OCR, and publishes bounding boxes.

        This method decodes the base64-encoded image data received in the message, extracts text bounding boxes
        using the `detect_text` function, and then publishes the results to the `FILTER_PII_QUEUE`.

        Parameters
        ----------
        ch : object
            The channel object provided by RabbitMQ when consuming messages.
        method : object
            The delivery method used by RabbitMQ for the message.
        properties : object
            The properties of the RabbitMQ message.
        body : bytes
            The body of the RabbitMQ message, which contains the image data in base64-encoded format.

        """
        try:
            # Decode the message body
            message = json.loads(body)
            image_data = base64.b64decode(message["image_data"])

            # Detect text in the image and get bounding boxes
            bounding_boxes = detect_text(image_data)

            # Serialize bounding boxes for the message queue
            bounding_boxes_json = [box.__dict__ for box in bounding_boxes]
            payload = {
                "img_id": message.get("img_id"),
                "bounding_boxes": bounding_boxes_json,
            }

            # Publish the results to the filter_pii_queue
            self.rabbitmq_client.publish_message(
                self.FILTER_PII_QUEUE, payload
            )
            print(
                f"Processed image and sent bounding boxes to filter_pii_queue for img_id {message.get('img_id')}"
            )

        except Exception as e:
            print(f"Error processing message: {e}")


if __name__ == "__main__":
    connection_params = os.getenv("RABBITMQ_HOST", "rabbitmq")
    ocr_service = PerformOCRService(connection_params)
    ocr_service.rabbitmq_client.start(ocr_service.process_image_message)
