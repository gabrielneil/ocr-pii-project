FROM python:3.11-slim

WORKDIR /app

COPY ./FilterPII/requirements.txt /app/requirements.txt

RUN python -m pip install pip --upgrade

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./FilterPII/src /app/FilterPII/src

COPY ./commons /app/commons

ENV PYTHONPATH "${PYTHONPATH}:/app"

CMD ["python", "-u", "/app/FilterPII/src/app.py"]