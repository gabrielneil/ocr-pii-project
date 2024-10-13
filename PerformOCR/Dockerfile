FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && apt-get clean


COPY ./PerformOCR/requirements.txt /app/requirements.txt

RUN python -m pip install pip --upgrade

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt


COPY ./PerformOCR/src /app/PerformOCR/src
COPY ./commons /app/commons

ENV PYTHONPATH "${PYTHONPATH}:/app"

CMD ["python", "-u", "/app/PerformOCR/src/app.py"]