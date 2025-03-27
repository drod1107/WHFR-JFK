# rag_api.py
from fastapi import FastAPI, Request
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import requests
import chromadb
from chromadb.config import Settings

load_dotenv()

CHROMA_HOST = os.environ["CHROMA_HOST"]
CHROMA_PORT = int(os.environ["CHROMA_PORT"])
OLLAMA_URL = "http://ollama:11434/api/generate"
EMBED_MODEL = "nomic-embed-text"
LLM_MODEL = "llama3"
COLLECTION_NAME = "rag-docs"

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

@app.post("/rag")
def rag_query(req: QueryRequest):
    # 1. Embed the query
    embed_resp = requests.post("http://localhost:11434/api/embeddings", json={
        "model": EMBED_MODEL,
        "prompt": req.query
    })
    embedding = embed_resp.json()["embedding"]

    # 2. Retrieve context from Chroma
    chroma_client = chromadb.HttpClient(
        host=CHROMA_HOST,
        port=CHROMA_PORT,
        settings=Settings()
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
