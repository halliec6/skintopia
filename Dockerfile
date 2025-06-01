# Use Python 3.10 slim image for LightFM compatibility
FROM python:3.10.0-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies required for LightFM
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy your project
COPY . .

# Command to start your API server
CMD ["uvicorn", "backend.src.api.recommender_lightfm_api:app", "--host=0.0.0.0", "--port=8000"]
