import base64
import uuid
from typing import List

from commons.clients.rabbit_mq import RabbitMQClient


def send_pii_list(img_id: str, pii_list: List[str]):
    # Initialize the RabbitMQ client
    pii_queue = "filter_pii_queue"
    rabbitmq_client = RabbitMQClient(connection_params, pii_queue)

    # Prepare the payload
    payload = {"img_id": img_id, "pii_terms": pii_list}

    # Publish the PII list message to the queue
    rabbitmq_client.publish_message(pii_queue, payload)

    print(f"Sent PII list for img_id {img_id} to {pii_queue}")


def submit_image(image_path: str, img_id: str):
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")

    # Initialize the RabbitMQ client
    ocr_queue = "ocr_queue"
    rabbitmq_client = RabbitMQClient(connection_params, ocr_queue)

    payload = {"img_id": img_id, "image_data": image_data}

    rabbitmq_client.publish_message(ocr_queue, payload)

    print(f"Submitted image for img_id {img_id}")


if __name__ == "__main__":
    connection_params = "localhost"

    img_id = str(uuid.uuid4())

    pii_list = [
        "Jose",
        "Antonio",
        "Camargo",
        "NEIL",
        "GABRIEL",
        "0000003100077280550602",
    ]

    path_to_img = "img.png"

    # Call the function to send the PII list and image
    send_pii_list(img_id, pii_list)
    submit_image(path_to_img, img_id)
