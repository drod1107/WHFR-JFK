# rag-api/Dockerfile
FROM whfr-base:latest

WORKDIR /app

COPY . .

CMD ["uvicorn", "rag_api:app", "--host", "0.0.0.0", "--port", "5050"]
