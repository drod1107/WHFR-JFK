# WHFR: Local RAG Stack with Custom Chroma, OCR, and RAG API

**WHFR** is a fully containerized, local-first Retrieval-Augmented Generation (RAG) system for OCR-processed, single-page PDFs. It enables document indexing, semantic search, and natural language Q&A using only local resources. Built for transparency, speed, and full control.

All services run in Docker and require no cloud APIs. The stack includes a GPU-accelerated OCR pipeline, a multiprocessing ingest system, vector storage with ChromaDB, and a local Ollama runtime for embeddings and language model responses.

---

## 🧠 Current Stack (April 2025)

| Component        | Technology / Tool                  | Status                      |
|------------------|-------------------------------------|-----------------------------|
| **OCR**          | TrOCR (`microsoft/trocr-base-handwritten`) via FastAPI | ✅ Single-page PDF OCR |
| **Embedding**    | `nomic-embed-text` via Ollama       | ✅ Vectorization for search |
| **LLM Runtime**  | Ollama 0.6.5                        | ✅ Serves Deepseek-R1:8b and Gemma 3 |
| **Vector Store** | ChromaDB (custom build)            | ✅ Embedded search engine |
| **Ingest**       | Multiprocessing FastAPI runner     | ✅ Parallel OCR + embedding |
| **RAG API**      | FastAPI endpoint (`/rag`)          | ⚠️ Functional, actively evolving |
| **Viewer API**   | FastAPI endpoint (`/search`)       | ✅ Returns `.txt` + `.png` matches |
| **Chat UI**      | OpenWebUI 0.6.5                    | ✅ Ollama-based chat, RAG-enabled |

---

## 💻 System Requirements

| Requirement       | Minimum                         | Recommended (Tested)       |
|-------------------|----------------------------------|----------------------------|
| **OS**            | Windows 11 + WSL2                | ✅ (Only tested setup)     |
| **GPU**           | NVIDIA RTX 3060 or better        | RTX 4070 Ti ✅             |
| **RAM**           | 16 GB                            | 32 GB                      |
| **Disk**          | 32 GB free                       | 64+ GB for large model use |
| **Software**      | Docker Desktop with WSL2 backend | ✅                         |

---

## ⏱ Performance Notes

- Ingesting ~27,000 single-page image PDFs takes ~3 hours on an RTX 4070 Ti.
- Output: one `.png` and one `.txt` per document in `/shared/processed_docs`.

---

## 📂 Input Format

WHFR is designed to process **single-page PDFs only**.

1. Drop your files into:

   ```bash
   shared/incoming_docs/
   ```

2. Output will appear in:

   ```bash
   shared/processed_docs/
   ```

To split multi-page PDFs, use any free online tool to export one PDF per page before ingest.

---

## 🚀 Setup and Run

### 1. Clone the repo

```bash
git clone https://github.com/your-org/WHFR.git
cd WHFR
```

### 2. Build all containers

```bash
docker compose build --no-cache
```

This builds a shared `whfr-base` image and all dependent services.

### 3. Launch the system

```bash
docker compose up
```

Available endpoints:

| Service        | URL                            |
|----------------|---------------------------------|
| Viewer API     | `http://localhost:5051/search?q=...` |
| RAG API        | `http://localhost:5050/rag`    |
| OpenWebUI      | `http://localhost:3000`        |
| ChromaDB       | `http://localhost:8000`        |

---

## 🔍 Example Queries

### Text Search

```bash
http://localhost:5051/search?q=plaintiff
```

Returns matched `.txt` excerpts and linked `.png` previews.

### Document-Aware Question (RAG)

```bash
curl -X POST http://localhost:5050/rag \
  -H "Content-Type: application/json" \
  -d '{"query": "What was the main outcome of the 1942 court decision?"}'
```

---

## 🧩 Enable RAG in OpenWebUI Chat

1. Visit `http://localhost:3000`  
   - Create an admin account and select a workspace

2. **Install RAG Plugin**
   - Go to the **Tools** tab
   - Click **➕ Add**
   - Paste the following into the editor and click **Save**:

   <details>
   <summary>Click to expand plugin code</summary>

   ```python
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
           self.rag_api_url = "http://rag-api:5050/rag"

       def rag_query(self, query: str) -> str:
           try:
               response = requests.post(self.rag_api_url, json={"query": query})
               if response.status_code == 200:
                   return response.json().get("response", "No response key returned.")
               return f"[RAG Error] API returned {response.status_code}: {response.text}"
           except Exception as e:
               return f"[RAG Exception] {str(e)}"
   ```

   </details>

3. **Add Ollama Models**
   - Go to **Settings → Models**
   - Create models like `deepseek-r1:8b` or `gemma:3b`
   - Enable **Tool Use**, and select **RAG Plugin**

4. **Enable in Chat**
   - Click the **➕** icon in the message box
   - Toggle **"Use RAG Plugin"**
   - All answers will now use your document index

To pull additional models:

```bash
docker exec -it ollama bash
ollama pull mistral
exit
```

---

## 📁 Folder Structure

```bash
WHFR/
├── docker-compose.yml
├── Dockerfile.base
├── base-requirements.txt
├── shared/
│   ├── incoming_docs/        # Place PDFs here
│   └── processed_docs/       # Output .txt and .png
├── ocr-helper/               # FastAPI OCR service
├── ingest-runner/            # Multiprocessing OCR + embedding
├── rag-api/                  # RAG pipeline API
├── viewer-api/               # Search UI API
├── chroma/                   # Custom Chroma source
├── rag_tool.py               # RAG plugin for OpenWebUI
```

---

## 🔐 License

This project combines open-source tools with custom logic.

### OSS (under original licenses)

- Ollama, ChromaDB, PyTorch, OpenWebUI, TrOCR

### Custom Code (© 2025 Windrose & Company LLC)

- `ocr-helper/`, `ingest-runner/`, `rag-api/`, `viewer-api/`
- `rag_tool.py`
- All pipeline logic and integration design

Use is permitted for personal or internal use.  
**Commercial use, redistribution, or repackaging requires permission.**

---

## ⭐ Stay Updated

WHFR is evolving fast.  
If you find it useful:

- ⭐ Star the repo  
- 🛠 Watch for updates as RAG and Viewer API improve  
- 🧠 Feedback welcome
