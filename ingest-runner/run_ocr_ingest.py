
import os
import uuid
import time
import socket
import logging
import requests
import chromadb
import multiprocessing
from glob import glob
from pathlib import Path
from pdf2image import convert_from_path
from dotenv import load_dotenv

# === Logging Setup ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(process)d] %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger()

load_dotenv()

# === CONFIG ===
OCR_HELPER_URL = "http://ocr-helper:8000/extract_clean_text"
OLLAMA_URL = "http://ollama:11434/api/embeddings"
CHROMA_HOST = os.environ.get("CHROMA_HOST")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT"))
COLLECTION_NAME = "rag-docs"
INPUT_DIR = Path("/shared/incoming_docs")
OUTPUT_DIR = Path("/shared/processed_docs")
FALLBACK_BASE_URL = "file:///shared/incoming_docs"
CHECKPOINT_FILE = OUTPUT_DIR / "db_checkpoint.txt"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def wait_for_ocr_service(host="ocr-helper", port=8000, timeout=240):
    log.info(f"Waiting for OCR helper at {host}:{port} to be ready...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=2):
                log.info("OCR helper is available!")
                return
        except OSError:
            time.sleep(1)
    raise RuntimeError("Timed out waiting for OCR helper to start.")

def load_checkpoint():
    processed = set()
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as cp:
            for line in cp:
                processed.add(line.strip())
    return processed

def save_to_checkpoint(filename, lock):
    with lock:
        with open(CHECKPOINT_FILE, "a", encoding="utf-8") as cp:
            cp.write(f"{filename}\n")

def convert_pdf_to_images(pdf_path):
    try:
        return convert_from_path(str(pdf_path), dpi=300, fmt='png')
    except Exception as e:
        log.error(f"Failed to convert {pdf_path.name}: {e}")
        return []

def process_single_pdf(file_path):
    try:
        if file_path.name in processed_files:
            log.info(f"Skipping already processed file: {file_path.name}")
            return []

        log.info(f"Processing file: {file_path.name}")
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
                except requests.exceptions.ConnectionError:
                    time.sleep(1)
            else:
                raise RuntimeError(f"OCR helper did not respond for {image_filename}")

            result = response.json()
            clean_text = result.get("clean_text", "").strip()
            if not clean_text:
                continue

            txt_path = image_path.with_suffix(".txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(f"[OCR Clarity: {result.get('clarity_percent')}%]\n")
                f.write(f"[Original Document: {result.get('fallback_url')}]\n\n")
                f.write(clean_text)

            log.info(f"OCR complete: {txt_path.name}")

            embed_resp = requests.post(OLLAMA_URL, json={"model": "nomic-embed-text", "prompt": clean_text})
            if embed_resp.status_code != 200:
                log.error(f"Embedding failed: {embed_resp.status_code}")
                continue

            embedding = embed_resp.json().get("embedding")
            if not embedding:
                log.error("No embedding returned")
                continue

            doc_id = str(uuid.uuid4())
            collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[clean_text],
                metadatas=[{"source": f"https://fake.url/{image_path.name}"}]
            )
            save_to_checkpoint(image_path.name, lock)
            log.info(f"Inserted document ID {doc_id}")
            results.append(doc_id)

        save_to_checkpoint(file_path.name, lock)
        return results

    except Exception as e:
        log.error(f"Failed to process {file_path.name}: {e}")
        return []

if __name__ == "__main__":
    wait_for_ocr_service()

    log.info("Connecting to ChromaDB...")
    chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

    processed_files = load_checkpoint()

    pdfs_to_process = sorted([
        f for f in INPUT_DIR.glob("*.pdf")
        if f.name not in processed_files
    ])

    log.info(f"{len(pdfs_to_process)} PDFs pending OCR and ingestion.")
    lock = multiprocessing.Lock()

    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        pool.map(process_single_pdf, pdfs_to_process)

    log.info("All done.")