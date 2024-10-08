import io

import pytesseract
from PIL import Image

from commons.text_bounding_box import TextBoundingBox


def detect_text(image: bytes) -> list[TextBoundingBox]:
    """Detects text in an image and returns a list of TextBoundingBox objects."""
    try:
        # Convert bytes to an image
        img = Image.open(io.BytesIO(image))

        # Run OCR using Tesseract
        ocr_data = pytesseract.image_to_data(
            img, output_type=pytesseract.Output.DICT
        )

        # List to hold TextBoundingBox instances
        bounding_boxes = []

        # Iterate through the detected text data and extract bounding boxes
        for i in range(len(ocr_data["text"])):
            if ocr_data["text"][i].strip():
                bounding_box = TextBoundingBox(
                    text=ocr_data["text"][i],
                    left=ocr_data["left"][i],
                    top=ocr_data["top"][i],
                    right=ocr_data["left"][i] + ocr_data["width"][i],
                    bottom=ocr_data["top"][i] + ocr_data["height"][i],
                )
                bounding_boxes.append(bounding_box)

        return bounding_boxes

    finally:
        img.close()
