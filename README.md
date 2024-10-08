# historian-middle-end-api

This project was designed to store and retrieve data from [historian-api](https://github.com/teknoir/historian-db).

## Index

- [Run project end to end locally](#run-project-end-to-end-locally)
    - [Makefile](#makefile)
    - [Run api locally](#run-api-locally)
- [Request examples](#request-examples)
    - [Ping](#ping)
    - [Retrieve events](#retrieve-events-from-a-collection)
- [Development](#development)
    - [Branches](#branches)
    - [Pull requests](#pull-request)

pii-detection/
│
├── docker-compose.yml
├── PerformOCR/
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
│   └── test_perform_ocr.py
├── FilterPII/
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
│   └── test_filter_pii.py
└── common/
    ├── message_queue.py
    └── text_bounding_box.py


## Run project end to end locally

### Makefile

#### Install dependencies

`make install`

#### Run lint to detect and fix code, applying best practices

`make lint-fix`

#### Run project end to end

`make compose`

#### Destroy infrastructure

`make stop`


## Request examples

Once you have built and run your image, it's time to give some tries!

#### Ping:

`curl --request GET \
--url http://127.0.0.1:30001/ping/`
