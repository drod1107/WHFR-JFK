# Use official lightweight Python image
FROM python:3.13-slim-bookworm

# Set working directory inside container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy in the app code
COPY . .

# Expose the FastAPI port
EXPOSE 5051

# Default command (redundant if also set in docker-compose)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5051"]
