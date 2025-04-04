# WHFR: Local RAG Stack with Custom Chroma, OCR, and RAG API

**WHFR** is a fully containerized Retrieval-Augmented Generation (RAG) system designed for serious local-first document indexing and natural language querying. It features a custom-built Chroma vector database, OCR pipeline, ingest runner, local LLM via Ollama, and a RESTful RAG API—all optimized for privacy, transparency, and extensibility.

---

## 🧠 Key Components

- **ChromaDB** – Custom-built from source for complete dependency control (e.g., pinned Protobuf, optional hnswlib rebuild).
- **VectorAdmin** – Visual admin interface for managing embeddings (connected to Chroma).
- **OCR Helper** – DocTR-based FastAPI service with GPU acceleration, optimized for scanned historical docs.
- **Ingest Runner** – FastAPI + multiprocessing pipeline with checkpointing for high-throughput ingest.
- **RAG API** – A lean, prompt-driven REST API layer for querying indexed data.
- **Ollama + OpenWebUI** – Local LLM runtime + chat interface, enhanced with a custom RAG plugin.
- **Apache Tika** – For structured text extraction from non-image PDFs.
- **PostgreSQL** – Backing store for VectorAdmin metadata.

---

## 🔧 How to Deploy Locally with Docker

### 1. Clone the repo

```bash
git clone https://github.com/your-org/WHFR.git
cd WHFR
```

### 2. Build all containers

```bash
docker compose build --no-cache
```

This ensures Chroma is rebuilt from the local folder using your custom Dockerfile (Protobuf, hnswlib, etc. included).

### 3. Start the stack

```bash
docker compose up
```

All services will spin up together, including VectorAdmin at `http://localhost:8080` and OpenWebUI at `http://localhost:3000`.

---

## 📡 Query the Vector DB via RAG API

Once up and running, you can query your indexed documents like this:

```bash
curl -X POST http://localhost:5050/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the plaintiff arguing in the 1942 court brief?"}'
```

The RAG API uses pre-configured prompts and fetches context chunks from Chroma to pass into the LLM.

---

## 🧪 Local Development (Partial Stack)

You can work on individual services independently:

```bash
# Run only the RAG API for development
docker compose run --service-ports rag-api
```

Or develop directly against the custom Chroma build:

```bash
docker compose up chromadb
```

All containers mount a shared volume for OCR and ingestion, so you can isolate just what you need.

---

## 📁 Folder Structure (Simplified)

```bash
WHFR/
├── docker-compose.yml
├── rag-api/
├── ocr-helper/
├── ingest-runner/
├── shared/                 # Mounted volume for OCR and ingest
├── chroma/                 # Custom Chroma source
│   ├── bin/docker_entrypoint.sh
│   └── Dockerfile
```

---

## 🔐 License

This project is dual-licensed:

### OSS Components:

All open-source components (ChromaDB, DocTR, Apache Tika, Ollama, etc.) retain their original licenses as required. Attribution and license copies are included per standard OSS guidelines.

### Custom Code:

The following components are protected and copyright © 2025 Windrose & Company LLC:

- `rag-api/`
- `ocr-helper/`
- `ingest-runner/`
- `rag_tool.py` + `rag_tool.json` plugin for OpenWebUI
- Custom prompts and ingest pipeline logic

These components are **not open-source** and may not be redistributed, sublicensed, or used in commercial applications without explicit permission. Licensing for commercial use is available upon request.
