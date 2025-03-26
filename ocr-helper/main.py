# ./ocr-helper/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import os

app = FastAPI()

# Load the DocTR OCR model once at startup
model = ocr_predictor(pretrained=True)

class OCRRequest(BaseModel):
    image_path: str
    source_url: str

@app.post("/extract_clean_text")
def extract_clean_text(data: OCRRequest):
    try:
        # Ensure file exists
        if not os.path.exists(data.image_path):
            return {"error": f"Image not found: {data.image_path}"}

        # Load image and run OCR
        doc = DocumentFile.from_images(data.image_path)
        result = model(doc)

        # Extract text from prediction
        json_output = result.export()
        extracted_text = "\n".join(
            word["value"]
            for page in json_output["pages"]
            for block in page["blocks"]
            for line in block["lines"]
            for word in line["words"]
        )

        # Heuristic for clarity estimation
        extracted_len = len(extracted_text)
        est_total_len = os.path.getsize(data.image_path) / 2.5  # crude guess
        clarity = round((extracted_len / est_total_len) * 100, 1)

        return {
            "clean_text": extracted_text.strip(),
            "clarity_percent": clarity,
            "fallback_url": data.source_url
        }

    except Exception as e:
        return {"error": str(e)}
