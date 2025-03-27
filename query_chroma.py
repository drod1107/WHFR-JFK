# query_chroma.py
import os
import sys
import requests
import chromadb
from dotenv import load_dotenv

load_dotenv()

CHROMA_URL = "http://localhost:8001"
OLLAMA_URL = "http://localhost:11434/api/generate"
COLLECTION_NAME = "rag-docs"
EMBED_MODEL = "nomic-embed-text"
LLM_MODEL = "deepseek-r1:8b"
CHROMA_HOST = os.environ.get("CHROMA_HOST")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT"))


def embed_query(text):
    print("[1] Embedding query with Ollama...")
    resp = requests.post("http://localhost:11434/api/embeddings", json={
        "model": EMBED_MODEL,
        "prompt": text
    })
    if resp.status_code != 200:
        raise Exception(f"Embedding failed: {resp.status_code} - {resp.text}")
    return resp.json()["embedding"]

def generate_answer(context, query):
    print("[4] Generating answer from LLM...")
    prompt = f"""Answer the following question using only the context below. Cite the source if possible.

Context:
{context}

Question: {query}
Answer:"""

    resp = requests.post(OLLAMA_URL, json={
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": False
    })
    if resp.status_code != 200:
        raise Exception(f"LLM generation failed: {resp.status_code} - {resp.text}")
    return resp.json()["response"]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python query_chroma.py \"your question here\"")
        sys.exit(1)

    query = sys.argv[1]
    print("[0] Query received:", query)

    print("[2] Connecting to ChromaDB...")
    chroma_client = chromadb.HttpClient(
        host=CHROMA_HOST,
        port=CHROMA_PORT
    )

    print("[3] Querying ChromaDB for context...")
    collection = chroma_client.get_collection(COLLECTION_NAME)
    query_embedding = embed_query(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not documents:
        print("⚠️ No matching documents found.")
        sys.exit(0)

    context = "\n\n".join(
        f"[Source: {meta.get('source', 'unknown')}]\n{doc}"
        for doc, meta in zip(documents, metadatas)
    )

    answer = generate_answer(context, query)
    print("\n🤖 LLM Answer:\n" + answer.strip())
