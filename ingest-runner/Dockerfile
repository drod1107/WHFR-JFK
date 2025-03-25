# ./ingest-runner/Dockerfile
FROM python:3.10-slim

RUN apt update && apt install -y poppler-utils && \
    apt clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run_ocr_ingest.py"]
