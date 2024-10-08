FROM python:3.11-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN python -m pip install pip --upgrade

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./app /code/app

COPY ../commons ./commons

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
