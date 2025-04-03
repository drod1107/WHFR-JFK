import os
import uuid
import sys
import requests
import chromadb
from glob import glob
from dotenv import load_dotenv

load_dotenv()

# === CONFIG ===
OCR_URL = "http://localhost:8000/extract_clean_text"
OLLAMA_URL = "http://localhost:11434/api/embeddings"
CHROMA_HOST = os.environ.get("CHROMA_HOST")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT"))
COLLECTION_NAME = "rag-docs"
IMAGE_DIR = "shared/processed_docs"  # 👈 Folder with your PNG files

# === ChromaDB Setup ===
print("[0] Connecting to ChromaDB...")
chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

# === Load all image files ===
image_files = glob(os.path.join(IMAGE_DIR, "*.png"))
print(f"[0] Found {len(image_files)} image(s) in {IMAGE_DIR}")

for image_path in image_files:
    print(f"\n🔄 Processing: {image_path}")
    source_url = f"https://fake.url/{os.path.basename(image_path)}"

    # === OCR Step ===
    print("[1] Requesting OCR...")
    ocr_payload = {
        "image_path": os.path.abspath(image_path),
        "source_url": source_url
    }
    ocr_resp = requests.post(OCR_URL, json=ocr_payload)

    if ocr_resp.status_code != 200:
        print(f"❌ OCR failed: {ocr_resp.status_code} - {ocr_resp.text}")
        continue

    ocr_json = ocr_resp.json()
    ocr_text = ocr_json.get("clean_text", "").strip()
    clarity = ocr_json.get("clarity_percent")
    print(f"[1] OCR complete. Clarity: {clarity}%")

    if not ocr_text:
        print("❌ No text returned from OCR.")
        continue

    # === Embedding Step ===
    print("[2] Sending text to Ollama for embedding...")
    embed_resp = requests.post(OLLAMA_URL, json={"model": "nomic-embed-text", "prompt": ocr_text})
    if embed_resp.status_code != 200:
        print(f"❌ Embedding failed: {embed_resp.status_code} - {embed_resp.text}")
        continue

    embedding = embed_resp.json().get("embedding")
    if not embedding:
        print("❌ No embedding returned from Ollama.")
        continue

    # === Upsert Step ===
    print("[3] Upserting into ChromaDB...")
    doc_id = str(uuid.uuid4())
    collection.add(
        ids=[doc_id],
        embeddings=[embedding],
        documents=[ocr_text],
        metadatas=[{"source": source_url}]
    )
    print(f"✔️ Inserted document ID {doc_id}")

print("\n✅ All done!")
