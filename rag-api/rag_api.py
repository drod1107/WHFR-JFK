# rag_api.py
from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
import chromadb
from chromadb.config import Settings
import os

# Use service names for internal Docker networking
CHROMA_HOST = os.environ.get("CHROMA_HOST", "chromadb")
CHROMA_PORT = os.environ.get("CHROMA_PORT", "8000")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama:11434") + "/api/generate"
EMBED_MODEL = "nomic-embed-text"
LLM_MODEL = "deepseek-r1:8b"
COLLECTION_NAME = "rag-docs"

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

@app.post("/rag")
def rag_query(req: QueryRequest):
    # 1. Embed the query
    embed_resp = requests.post(f"{OLLAMA_URL.replace('/generate', '/embeddings')}", json={
        "model": EMBED_MODEL,
        "prompt": req.query
    })
    embedding = embed_resp.json()["embedding"]

    # 2. Retrieve context from Chroma
    chroma_client = chromadb.HttpClient(
        host=CHROMA_HOST,
        port=CHROMA_PORT
    )
    collection = chroma_client.get_collection(COLLECTION_NAME)
    results = collection.query(query_embeddings=[embedding], n_results=3)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    context = "\n\n".join(
        f"[Source: {meta.get('source', 'unknown')}]\n{doc}"
        for doc, meta in zip(documents, metadatas)
    )

    # 3. Generate final answer
    prompt = f"""Answer the following question using only the context below. Cite the source if possible.

Context:
{context}

Question: {req.query}
Answer:"""

    final_resp = requests.post(OLLAMA_URL, json={
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": False
    })

    return {
        "response": final_resp.json()["response"],
        "sources": metadatas
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}