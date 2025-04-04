import os
import uuid
from glob import glob
from pathlib import Path
import requests
import chromadb
from dotenv import load_dotenv

load_dotenv()

# === CONFIG ===
OLLAMA_URL = "http://ollama:11434/api/embeddings"
CHROMA_HOST = os.environ.get("CHROMA_HOST")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT"))
COLLECTION_NAME = "rag-docs"
IMAGE_DIR = "/shared/processed_docs"
CHECKPOINT_FILE = Path(IMAGE_DIR) / "db_checkpoint.txt"

# === Setup ChromaDB ===
print("[0] Connecting to ChromaDB...")
chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

# === Load checkpoint ===
processed_images = set()
if CHECKPOINT_FILE.exists():
    with open(CHECKPOINT_FILE, "r", encoding="utf-8") as cp:
        processed_images = set(line.strip() for line in cp)

# === Process all PNG images ===
image_files = glob(os.path.join(IMAGE_DIR, "*.png"))
print(f"[0] Found {len(image_files)} image(s) in {IMAGE_DIR}")

for image_path in image_files:
    image_path = Path(image_path)
    if image_path.name in processed_images:
        print(f"⏭️ Skipping already pushed file: {image_path.name}")
        continue

    print(f"\n🔄 Processing: {image_path.name}")
    txt_path = image_path.with_suffix(".txt")

    if not txt_path.exists():
        print(f"❌ Missing OCR text for {image_path.name}, skipping.")
        continue

    # === Read OCR text ===
    with open(txt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        ocr_text = "".join(lines[3:]).strip()  # Skip metadata lines

    if not ocr_text:
        print(f"❌ Empty OCR result in {txt_path.name}, skipping.")
        continue

    # === Get embedding from Ollama ===
    print("[2] Sending text to Ollama for embedding...")
    embed_resp = requests.post(OLLAMA_URL, json={"model": "nomic-embed-text", "prompt": ocr_text})

    if embed_resp.status_code != 200:
        print(f"❌ Embedding failed: {embed_resp.status_code} - {embed_resp.text}")
        continue

    embedding = embed_resp.json().get("embedding")
    if not embedding:
        print("❌ No embedding returned from Ollama.")
        continue

    # === Upsert into Chroma ===
    print("[3] Upserting into ChromaDB...")
    doc_id = str(uuid.uuid4())
    source_url = f"https://fake.url/{image_path.name}"

    collection.add(
        ids=[doc_id],
        embeddings=[embedding],
        documents=[ocr_text],
        metadatas=[{"source": source_url}]
    )

    # === Update checkpoint ===
    with open(CHECKPOINT_FILE, "a", encoding="utf-8") as cp:
        cp.write(f"{image_path.name}\n")

    print(f"✔️ Inserted document ID {doc_id}")

print("\n✅ All done!")
