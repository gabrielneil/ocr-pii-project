from fastapi import FastAPI, File, HTTPException, UploadFile, status

from commons.exceptions import format_exception
from commons.message_queue import publish_message
from commons.ocr_utils import detect_text

app = FastAPI(
    docs_url="/docs",
    title="ocr-api",
    description="This project was designed to run OCR process",
    summary="OCR api to extract values from imgs.",
    contact={
        "name": "Gabriel Neil",
        "email": "gabrielneil7@gmail.com",
    },
)


@app.post("/perform_ocr", status_code=status.HTTP_201_CREATED)
async def perform_ocr(image: UploadFile = File(...)):
    try:
        image_data = await image.read()

        # Detect text in the image and get bounding boxes
        bounding_boxes = detect_text(image_data)

        # Serialize bounding boxes for message queue
        bounding_boxes_json = [box.__dict__ for box in bounding_boxes]
        # publish_message("filter_pii", bounding_boxes_json)

        return {"result": "OCR execution finished"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=format_exception(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5001)
