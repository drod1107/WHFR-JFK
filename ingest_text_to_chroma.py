import os
import uuid
import sys
import requests
import chromadb
from dotenv import load_dotenv

load_dotenv()

# === CONFIG ===
OCR_URL = "http://localhost:8000/extract_clean_text"
OLLAMA_URL = "http://localhost:11434/api/embeddings"
CHROMA_HOST = os.environ.get("CHROMA_HOST")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT"))
IMAGE_PATH = os.path.abspath("shared/processed_docs/test_image.png")
SOURCE_URL = "https://fake.url/test.pdf"
COLLECTION_NAME = "rag-docs"

# === OCR Step ===
print("[1] Requesting OCR...")
ocr_payload = {
    "image_path": IMAGE_PATH,
    "source_url": SOURCE_URL
}
ocr_resp = requests.post(OCR_URL, json=ocr_payload)

if ocr_resp.status_code != 200:
    print(f"❌ OCR failed: {ocr_resp.status_code} - {ocr_resp.text}")
    sys.exit(1)

ocr_json = ocr_resp.json()
ocr_text = ocr_json.get("clean_text", "").strip()
clarity = ocr_json.get("clarity_percent")
print(f"[1] OCR complete. Clarity: {clarity}%")

if not ocr_text:
    print("❌ No text returned from OCR.")
    sys.exit(1)

# === Embedding Step ===
print("[2] Sending text to Ollama for embedding...")
embed_resp = requests.post(OLLAMA_URL, json={"model": "nomic-embed-text", "prompt": ocr_text})
if embed_resp.status_code != 200:
    print(f"❌ Embedding failed: {embed_resp.status_code} - {embed_resp.text}")
    sys.exit(1)

embedding = embed_resp.json().get("embedding")
if not embedding:
    print("❌ No embedding returned from Ollama.")
    sys.exit(1)

# === ChromaDB Step ===
print("[3] Connecting to ChromaDB (remote via HttpClient)...")
chroma_client = chromadb.HttpClient(
    host=CHROMA_HOST,
    port=CHROMA_PORT
)

print("[3] Creating or getting collection...")
collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

# === Upsert ===
print("[4] Upserting document into ChromaDB...")
doc_id = str(uuid.uuid4())
collection.add(
    ids=[doc_id],
    embeddings=[embedding],
    documents=[ocr_text],
    metadatas=[{"source": SOURCE_URL}]
)

print(f"✔️ Document inserted into collection '{COLLECTION_NAME}' with ID {doc_id}")
