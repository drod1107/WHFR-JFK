# connect_to_chroma.py
import chromadb

# ⚠️ Use the internal Docker network name here
client = chromadb.HttpClient(host="chromadb", port=8000)

# List collections
collections = client.list_collections()
print(f"Found {len(collections)} collection(s):")
for col in collections:
    print(f" - {col.name}")

# Optionally inspect a collection's contents
print("\n--- Contents of 'rag-docs' ---")
try:
    collection = client.get_collection("rag-docs")
    results = collection.get(include=["documents", "metadatas"])
    for i, doc in enumerate(results['documents']):
        print(f"\n--- Document {i+1} ---")
        print("Text:", doc[:200], "...")
        print("Metadata:", results['metadatas'][i])
except Exception as e:
    print("Couldn't fetch rag-docs:", e)
