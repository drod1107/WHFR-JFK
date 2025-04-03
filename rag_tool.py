"""
title: RAG Plugin
author: You
description: Custom RAG tool for document Q&A
version: 0.1.0
license: MIT
required_open_webui_version: 0.4.0
requirements: requests
"""

import requests


class Tools:
    def __init__(self):
        # Use container names for Docker networking
        self.rag_api_url = "http://rag-api:5050/rag"

    def rag_query(self, query: str) -> str:
        """
        Perform a RAG query using the embedded backend API.
        
        :param query: The user question to answer using the document knowledge base.
        :return: A generated answer from the LLM grounded in the documents.
        """

        try:
            response = requests.post(self.rag_api_url, json={"query": query})

            if response.status_code == 200:
                data = response.json()
                return data.get("response", "No response key returned.")
            else:
                return f"[RAG Error] API returned {response.status_code}: {response.text}"

        except Exception as e:
            return f"[RAG Exception] {str(e)}"
