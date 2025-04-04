# ./ocr-helper/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import torch
import os

app = FastAPI()

# === GPU/CPU SETUP ===
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[INIT] Using device: {device}")

# === Load TrOCR model and processor ===
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten").to(device)

class OCRRequest(BaseModel):
    image_path: str
    source_url: str

@app.post("/extract_clean_text")
def extract_clean_text(data: OCRRequest):
    try:
        if not os.path.exists(data.image_path):
            return {"error": f"Image not found: {data.image_path}"}

        image = Image.open(data.image_path).convert("RGB")
        pixel_values = processor(images=image, return_tensors="pt").pixel_values.to(device)
        generated_ids = model.generate(pixel_values)
        text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

        # Heuristic clarity estimation
        extracted_len = len(text)
        est_total_len = os.path.getsize(data.image_path) / 2.5
        clarity = round((extracted_len / est_total_len) * 100, 1)

        return {
            "clean_text": text.strip(),
            "clarity_percent": clarity,
            "fallback_url": data.source_url
        }

    except Exception as e:
        return {"error": str(e)}
