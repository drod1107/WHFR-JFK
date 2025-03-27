FROM python:3.10-slim

WORKDIR /app

RUN apt update && apt install -y \
    poppler-utils \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run_ocr_ingest.py"]
