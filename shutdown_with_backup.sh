#!/bin/bash
set -e

echo "🛑 [1] Stopping Chroma container..."
docker stop chromadb

echo "📦 [2] Backing up Chroma data..."
./backup_chroma.sh

echo "🧹 [3] Stopping remaining containers..."
docker stop ingest-runner ocr-helper rag-api openwebui ollama

echo "✅ [4] All services shut down and chroma backup completed successfully."
