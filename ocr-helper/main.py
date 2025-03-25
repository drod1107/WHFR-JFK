# ./ocr-helper/main.py
from fastapi import FastAPI, Request
from pydantic import BaseModel
from PIL import Image
import pytesseract
import cv2
import os

app = FastAPI()

class OCRRequest(BaseModel):
    image_path: str
    source_url: str

@app.post("/extract_clean_text")
def extract_clean_text(data: OCRRequest):
    try:
        # Load and preprocess image
        img = cv2.imread(data.image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        scaled = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        thresh = cv2.adaptiveThreshold(
            scaled, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        processed_path = "/tmp/processed.png"
        cv2.imwrite(processed_path, thresh)

        # OCR
        text = pytesseract.image_to_string(Image.open(processed_path), config="--psm 11")
        extracted_len = len(text)
        est_total_len = os.path.getsize(data.image_path) / 2.5  # heuristic
        clarity = round((extracted_len / est_total_len) * 100, 1)

        return {
            "clean_text": text.strip(),
            "clarity_percent": clarity,
            "fallback_url": data.source_url
        }

    except Exception as e:
        return {"error": str(e)}
