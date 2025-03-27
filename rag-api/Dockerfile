# rag-api/Dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN apt update && apt install -y libgl1 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "rag_api:app", "--host", "0.0.0.0", "--port", "5050"]
