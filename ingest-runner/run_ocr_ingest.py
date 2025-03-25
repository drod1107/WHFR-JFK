# ./ingest-runner/run_ocr_ingest.py
import os
import requests
from pathlib import Path
from PyPDF2 import PdfReader
from pdf2image import convert_from_path

# === CONFIG ===
OCR_HELPER_URL = "http://ocr-helper:8000/extract_clean_text"
# uncomment next two lines for docker configuration
INPUT_DIR = Path("/shared_data/incoming_docs")
OUTPUT_DIR = Path("/shared_data/processed_docs")
# uncomment these instead for testing on Windows locally
# INPUT_DIR = Path("incoming_docs")
# OUTPUT_DIR = Path("processed_docs")

FALLBACK_BASE_URL = "file:///mnt/data/incoming_docs"

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Track results
results = []

# Helper function to convert PDF pages to images
def convert_pdf_to_images(pdf_path):
    try:
        return convert_from_path(str(pdf_path), dpi=300, fmt='png')
    except Exception as e:
        print(f"[!] Failed to convert {pdf_path.name}: {e}")
        return []

# Process each file in the input directory
for file_path in INPUT_DIR.glob("*"):
    print(f"Found file: {file_path}")
    if file_path.suffix.lower() == ".pdf":
        # Convert PDF pages to images
        images = convert_pdf_to_images(file_path)
        for i, image in enumerate(images):
            image_filename = f"{file_path.stem}_page_{i+1}.png"
            image_path = OUTPUT_DIR / image_filename
            image.save(image_path)

            # Send to OCR helper
            response = requests.post(OCR_HELPER_URL, json={
                "image_path": str(image_path),
                "source_url": f"{FALLBACK_BASE_URL}/{file_path.name}"
            })

            if response.status_code == 200:
                result = response.json()
                clarity = result.get("clarity_percent", 0)
                clean_text = result.get("clean_text", "").strip()
                fallback_url = result.get("fallback_url")

                # Save text with clarity info + fallback
                output_txt_path = OUTPUT_DIR / f"{file_path.stem}_page_{i+1}.txt"
                with open(output_txt_path, "w", encoding="utf-8") as f:
                    f.write(f"[OCR Clarity: {clarity}%]\n")
                    f.write(f"[Original Document: {fallback_url}]\n\n")
                    f.write(clean_text)

                results.append({
                    "file": str(file_path.name),
                    "page": i + 1,
                    "clarity_percent": clarity,
                    "output": str(output_txt_path)
                })
            else:
                print(f"[X] OCR helper failed for {image_path.name}: {response.text}")

# Output a summary manifest
manifest_path = OUTPUT_DIR / "manifest.txt"
with open(manifest_path, "w", encoding="utf-8") as mf:
    for entry in results:
        mf.write(f"{entry['file']} (Page {entry['page']}): {entry['clarity_percent']}% -> {entry['output']}\n")

manifest_path.name
