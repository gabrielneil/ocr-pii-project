# ocr-pii-project

This project was designed to extract text from images using OCR and filter pii elements

## Scaffolding
```
ocr-pii-project/
├── commons/ # Common utilities shared across services
│
├── FilterPII/ # PII filtering microservice
│
├── PerformOCR/ # OCR processing microservice
│
├── tests/ # Unit tests for the system
```

## Run project end to end locally

### Makefile

#### Install dependencies

`make install`

#### Run lint to detect and fix code, applying best practices

`make lint-fix`

#### Build and launch containers

`make compose`

#### Run test

`make run-process`

##### Notes:

When you run the command, messages will be sent to two different topics:

* OCR: The topic handling the OCR text extraction.
* PII List: The topic responsible for processing the PII terms. 
`Filtered list: [
        "Jose",
        "Antonio",
        "Camargo",
        "NEIL",
        "GABRIEL",
        "0000003100077280550602",
    ]
`
* `
##### Example Output:
Once the process finishes, the final filtered result will be printed to the console. An example of the output might look like this:

`
Payload final result: {
    "img_id": "6e9c23e0-00aa-4b89-8cc7-5c6fcad58891",
    "filtered_boxes": [
        {"text": "i", "left": 180, "right": 220, "top": 76, "bottom": 113},
        {"text": "02/10/2024", "left": 446, "right": 552, "top": 77, "bottom": 91},
        {"text": "BBY.", "left": 76, "right": 187, "top": 77, "bottom": 127},
        {"text": "08:52:00", "left": 475, "right": 551, "top": 99, "bottom": 113},
        {"text": "Transferiste", "left": 258, "right": 359, "top": 177, "bottom": 191},
        {"text": "a", "left": 364, "right": 372, "top": 181, "bottom": 191},
        {"text": "$", "left": 203, "right": 226, "top": 262, "bottom": 300},
        {"text": "27.000,00", "left": 237, "right": 429, "top": 265, "bottom": 300},
        {"text": "Numero", "left": 119, "right": 191, "top": 365, "bottom": 380},
        {"text": "de", "left": 197, "right": 217, "top": 365, "bottom": 380},
        {"text": "referencia", "left": 224, "right": 314, "top": 365, "bottom": 380},
        {"text": "70103193010241002", "left": 320, "right": 511, "top": 365, "bottom": 380},
        {"text": "Cuenta", "left": 75, "right": 134, "top": 430, "bottom": 444},
        {"text": "de", "left": 140, "right": 159, "top": 430, "bottom": 444},
        {"text": "origen", "left": 165, "right": 215, "top": 430, "bottom": 448},
        {"text": "CA$", "left": 303, "right": 338, "top": 428, "bottom": 446},
        {"text": "290-339466/6", "left": 343, "right": 470, "top": 429, "bottom": 444},
        {"text": "Titular", "left": 71, "right": 128, "top": 472, "bottom": 500},
        {"text": "Cuenta", "left": 75, "right": 134, "top": 523, "bottom": 537},
        {"text": "de", "left": 140, "right": 159, "top": 523, "bottom": 537},
        {"text": "destino", "left": 165, "right": 225, "top": 523, "bottom": 537},
        {"text": "Destinatario", "left": 76, "right": 176, "top": 565, "bottom": 591},
        {"text": "CBU/CVU", "left": 75, "right": 159, "top": 616, "bottom": 630},
        {"text": "del", "left": 165, "right": 189, "top": 616, "bottom": 630},
        {"text": "destinatario", "left": 195, "right": 293, "top": 616, "bottom": 630},
        {"text": "CUIT", "left": 75, "right": 116, "top": 663, "bottom": 677},
        {"text": "destinatario", "left": 122, "right": 220, "top": 663, "bottom": 677},
        {"text": "Motivo", "left": 76, "right": 131, "top": 709, "bottom": 723},
        {"text": "y", "left": 136, "right": 145, "top": 713, "bottom": 727},
        {"text": "concepto", "left": 150, "right": 227, "top": 710, "bottom": 727},
        {"text": "VARIOS", "left": 303, "right": 368, "top": 709, "bottom": 724},
        {"text": "Esta", "left": 148, "right": 182, "top": 836, "bottom": 850},
        {"text": "operacién", "left": 188, "right": 269, "top": 836, "bottom": 854},
        {"text": "se", "left": 275, "right": 293, "top": 840, "bottom": 850},
        {"text": "realizé", "left": 299, "right": 353, "top": 836, "bottom": 850},
        {"text": "en", "left": 358, "right": 377, "top": 840, "bottom": 850},
        {"text": "BBVA", "left": 384, "right": 431, "top": 836, "bottom": 850},
        {"text": "Movil", "left": 437, "right": 478, "top": 836, "bottom": 850}
    ]
}
`