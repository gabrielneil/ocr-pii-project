from io import BytesIO
from unittest import mock

import pytesseract
import pytest
from PIL import Image

from commons.entities.text_bounding_box import TextBoundingBox
from PerformOCR.src.utils import detect_text


@pytest.mark.parametrize(
    "ocr_data, expected_result",
    [
        # Case 1: Text detected ("Hello" and "World")
        (
            {
                "text": ["Hello", "", "World"],
                "left": [10, 20, 30],
                "top": [40, 50, 60],
                "width": [100, 200, 300],
                "height": [10, 20, 30],
            },
            [
                TextBoundingBox(
                    text="Hello", left=10, right=110, top=40, bottom=50
                ),
                TextBoundingBox(
                    text="World", left=30, right=330, top=60, bottom=90
                ),
            ],
        ),
        # Case 2: No text detected (empty text)
        (
            {
                "text": ["", "", ""],
                "left": [10, 20, 30],
                "top": [40, 50, 60],
                "width": [100, 200, 300],
                "height": [10, 20, 30],
            },
            [],  # Expected result is an empty list
        ),
    ],
)
def test_detect_text(mocker, ocr_data, expected_result):
    # Mock the image opening process
    mock_image_open = mocker.patch("PIL.Image.open")

    # Create a mock image object
    mock_image = mock.Mock(spec=Image.Image)
    mock_image_open.return_value = mock_image

    # Mock the pytesseract output
    mock_pytesseract = mocker.patch("pytesseract.image_to_data")
    mock_pytesseract.return_value = ocr_data

    # Mock image bytes input
    mock_image_bytes = b"fake_image_data"

    # Call the detect_text function
    result = detect_text(mock_image_bytes)

    # Verify the result matches the expected output for each case
    assert result == expected_result

    # Assert that the image was opened using PIL.Image.open and check the content of the BytesIO object
    args, _ = mock_image_open.call_args
    opened_bytes_io = args[0]
    assert isinstance(opened_bytes_io, BytesIO)
    assert opened_bytes_io.getvalue() == mock_image_bytes  # Compare contents

    # Assert that pytesseract.image_to_data was called with the mock image
    mock_pytesseract.assert_called_once_with(
        mock_image, output_type=pytesseract.Output.DICT
    )

    # Assert that the image was closed after processing
    mock_image.close.assert_called_once()
