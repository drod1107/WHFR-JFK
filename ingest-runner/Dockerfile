FROM whfr-base:latest

WORKDIR /ocr-helper

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run_ocr_ingest.py"]