Here’s the updated `README.md`, fully aligned with the current working state of your WHFR stack and its roadmap:

---

# WHFR: Local RAG Stack with Custom Chroma, OCR, and RAG API

**WHFR** is a fully containerized Retrieval-Augmented Generation (RAG) system designed for high-throughput, local-first document indexing and natural language querying. Built for speed, privacy, and extensibility, WHFR includes a zero-effort ingest pipeline, ChromaDB vector store, local LLM runtime, admin viewer, and full REST API interface for embedding, querying, and debugging.

---

## 🧠 Key Components

- **whfr-base** – Secure, unified Docker base image used by all services (based on `python:3.13-slim-bookworm`)
- **ChromaDB** – Custom-built from source with pinned Protobuf and hnswlib rebuild, for total vector index control
- **OCR Helper** – FastAPI + TrOCR service with GPU acceleration for scanned historical docs (image-based PDFs)
- **Ingest Runner** – High-speed parallel ingestion pipeline (multiprocessing + checkpointed) for massive ingest runs
- **RAG API** – FastAPI-based REST API that performs query embedding, Chroma search, and context-aware LLM generation
- **Viewer API** – FastAPI service with searchable `.txt` previews side-by-side with the original image output
- **Ollama** – Local LLM inference runtime for embedding and answer generation (supports Deepseek, Gemma, etc.)
- **OpenWebUI** – Full-featured chat UI with embedded knowledgebase plugin connected to WHFR's RAG API
- **VectorAdmin** *(optional)* – UI for inspecting Chroma vector contents
- **Apache Tika** – Text extraction fallback for structured (non-image) PDFs
- **PostgreSQL** – Metadata store for VectorAdmin (optional)

---

## 🚀 Roadmap Highlights

- 🔍 **Viewer Frontend** – Live searchable GUI for browsing OCR’d text + original page image (in progress)
- 💾 **Chunking + Re-Ranking** – Dynamic segmenting + context re-ranking for improved RAG accuracy
- 🔐 **Access Control** – Optional login/auth layers for shared deployments
- 📦 **Offline Ollama Model Bundles** – Support for pre-pulled Ollama model blobs in build phase
- 📊 **Ingest Dashboard** – Progress view, failure recovery UI, and resumable batch stats
- 🔁 **Stream-to-Ingest** – Real-time folder or S3 watcher to trigger ingestion on new file drop

---

## 🔧 How to Deploy Locally with Docker

### 1. Clone the repo

```bash
git clone https://github.com/your-org/WHFR.git
cd WHFR
```

### 2. Build everything

```bash
docker compose build --no-cache
```

This will automatically build the shared `whfr-base` image, then every service that depends on it. Ollama, Chroma, OCR, and ingest will all compile from local source.

### 3. Start the full stack

```bash
docker compose up
```

This launches all services, including:

- RAG API → `http://localhost:5050`
- Viewer API → `http://localhost:5051`
- OpenWebUI → `http://localhost:3000`
- ChromaDB → `http://localhost:8000`
- VectorAdmin *(if included)* → `http://localhost:8080`

---

## 📡 Example Query via RAG API

```bash
curl -X POST http://localhost:5050/rag \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the plaintiff arguing in the 1942 court brief?"}'
```

This performs embedding, semantic search via Chroma, and answer generation via your local Ollama model.

---

## 📂 Folder Structure (Simplified)

```bash
WHFR/
├── docker-compose.yml
├── Dockerfile.base                  # Shared base image used by all services
├── base-requirements.txt           # Base Python deps (for whfr-base)
├── shared/                         # OCR input/output (shared volume)
│   ├── incoming_docs/              # Drop PDFs here to ingest
│   └── processed_docs/             # .txt + .png outputs
├── rag-api/
├── ingest-runner/
├── ocr-helper/
├── viewer-api/
├── chroma/                         # Custom-built ChromaDB
```

---

## 🔒 Licensing

### OSS Components

All open-source components (ChromaDB, Ollama, trOCR, FastAPI, etc.) retain their original licenses. See `/licenses/` if included.

### WHFR Custom Code

The following components are **copyright © 2025 Windrose & Company LLC** and not open-source:

- `rag-api/`
- `ocr-helper/`
- `ingest-runner/`
- `viewer-api/`
- `rag_tool.py` + `rag_tool.json` (for OpenWebUI)
- Custom prompts, ingest logic, and processing flows

Use is permitted for personal and internal projects. For redistribution, licensing, or commercial deployment, contact Windrose & Co.

---

Let me know if you want a live badge system, Docker Hub push workflow, or GH Actions deployment added next.