install:
	@( \
		python -m venv .venv; \
		source .venv/bin/activate; \
		python -m pip install --no-cache-dir -r requirements.txt; \
		python -m pip install --no-cache-dir -r requirements-dev.txt; \
	)

isort:
	@python -m isort -l 79 --profile black --check .

black:
	@python -m black -l 79 --check .

pylama:
	@python -m pylama .

lint: isort black pylama

lint-fix:
	@python -m isort -l 79 --profile black .
	@python -m black -l 79 .

compose:
	@docker-compose up --build

api-call-ocr:
	@curl --request POST \
  --url http://localhost:5001/perform_ocr \
  --header 'content-type: multipart/form-data' \
  --form image=@/Users/gabrielneil/Repos/ocr-pii-project/img.png

api-call-pii:
	@curl -X POST http://localhost:5001/start_filtering
