"""
title: RAG Plugin
author: You
description: Custom RAG tool for document Q&A
version: 0.1.0
license: MIT
required_open_webui_version: 0.4.0
requirements: requests, chromadb
"""

import requests
import chromadb
from chromadb.config import Settings
from pydantic import BaseModel, Field

class Tools:
    def __init__(self):
        self.chroma_host = "localhost"
        self.chroma_port = 8001
        self.ollama_url = "http://ollama:11434/api/generate"
        self.embed_model = "nomic-embed-text"
        self.llm_model = "deepseek-r1:8b"
        self.collection = "rag-docs"

    class Valves(BaseModel):
        rag_mode: bool = Field(True, description="Enable document-grounded answering")

    def query_rag(self, query: str) -> str:
        """
        Query the ChromaDB vector database using an embedded query and return an LLM-generated answer.
        
        :param query: The question to answer using retrieved documents.
        :return: A generated answer based on the relevant documents.
        """

        # Embed query
        embed_resp = requests.post("http://ollama:11434/api/embeddings", json={
            "model": self.embed_model,
            "prompt": query
        })
        embedding = embed_resp.json()["embedding"]

        # Query Chroma
        chroma_client = chromadb.HttpClient(
            host=self.chroma_host,
            port=self.chroma_port,
            settings=Settings()
        )
        collection = chroma_client.get_collection(self.collection)
        results = collection.query(query_embeddings=[embedding], n_results=3)

        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        context = "\n\n".join(
            f"[{meta.get('source', 'unknown')}]:\n{doc}"
            for doc, meta in zip(docs, metas)
        )

        # Generate LLM response
        prompt = f"""Answer using only the context below. Cite your sources.

Context:
{context}

Question: {query}
Answer:"""

        llm_resp = requests.post(self.ollama_url, json={
            "model": self.llm_model,
            "prompt": prompt,
            "stream": False
        })

        return llm_resp.json()["response"]
