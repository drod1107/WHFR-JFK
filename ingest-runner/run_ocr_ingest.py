import requests
from pathlib import Path
from pdf2image import convert_from_path
import time
import socket
import multiprocessing

# Global lock to be set in __main__
lock = None

def wait_for_ocr_service(host="ocr-helper", port=8000, timeout=240):
    print(f"[0] Waiting for OCR helper at {host}:{port} to be ready...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=2):
                print("[0] OCR helper is available!")
                return
        except OSError:
            print("[!] OCR helper port not open yet...")
            time.sleep(1)
    raise RuntimeError("❌ Timed out waiting for OCR helper to start.")

wait_for_ocr_service()

# === CONFIG ===
OCR_HELPER_URL = "http://ocr-helper:8000/extract_clean_text"
INPUT_DIR = Path("/shared/incoming_docs")
OUTPUT_DIR = Path("/shared/processed_docs")
FALLBACK_BASE_URL = "file:///shared/incoming_docs"
CHECKPOINT_FILE = OUTPUT_DIR / "checkpoint.txt"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

processed_files = set()
if CHECKPOINT_FILE.exists():
    with open(CHECKPOINT_FILE, "r", encoding="utf-8") as cp:
        for line in cp:
            processed_files.add(line.strip())

def convert_pdf_to_images(pdf_path):
    try:
        return convert_from_path(str(pdf_path), dpi=300, fmt='png')
    except Exception as e:
        print(f"[!] Failed to convert {pdf_path.name}: {e}")
        return []

def process_single_pdf(file_path: Path):
    global lock
    try:
        if file_path.name in processed_files:
            print(f"Skipping already processed file: {file_path.name}")
            return []

        print(f"Processing file: {file_path.name}")
        images = convert_pdf_to_images(file_path)
        if not images:
            return []

        results = []
        for i, image in enumerate(images):
            image_filename = f"{file_path.stem}_page_{i+1}.png"
            image_path = OUTPUT_DIR / image_filename
            image.save(image_path)

            for attempt in range(20):
                try:
                    response = requests.post(OCR_HELPER_URL, json={
                        "image_path": str(image_path),
                        "source_url": f"{FALLBACK_BASE_URL}/{file_path.name}"
                    })
                    if response.status_code == 200:
                        break
                    else:
                        print(f"[!] OCR helper error (status {response.status_code}): {response.text}")
                except requests.exceptions.ConnectionError:
                    print(f"[!] OCR helper not ready (attempt {attempt + 1}/20)")
                    time.sleep(1)
            else:
                raise RuntimeError(f"OCR helper did not respond for file {image_filename} after multiple retries")

            result = response.json()
            clarity = result.get("clarity_percent", 0)
            clean_text = result.get("clean_text", "").strip()
            fallback_url = result.get("fallback_url")

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

        with lock:
            with open(CHECKPOINT_FILE, "a", encoding="utf-8") as cp:
                cp.write(f"{file_path.name}\n")

        return results

    except Exception as e:
        print(f"[!] Failed to process {file_path.name}: {e}")
        return []

if __name__ == "__main__":
    pdfs_to_process = sorted([
        f for f in INPUT_DIR.glob("*.pdf")
        if f.name not in processed_files
    ])

    print(f"[Ingest] {len(pdfs_to_process)} PDFs pending OCR.")

    lock = multiprocessing.Lock()

    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        all_results = pool.map(process_single_pdf, pdfs_to_process)

    results = [entry for group in all_results for entry in group]

    manifest_path = OUTPUT_DIR / "manifest.txt"
    with open(manifest_path, "w", encoding="utf-8") as mf:
        for entry in results:
            mf.write(f"{entry['file']} (Page {entry['page']}): {entry['clarity_percent']}% -> {entry['output']}\n")

    print(f"\n✅ Done. Manifest written to: {manifest_path}")
