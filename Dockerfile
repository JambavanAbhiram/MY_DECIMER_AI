# --------------------------------------------------
# Base Image
# --------------------------------------------------
FROM python:3.12-slim

# --------------------------------------------------
# Environment Variables
# --------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# --------------------------------------------------
# Install System Dependencies
# --------------------------------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    git \
    libgl1 \
    libglib2.0-0 \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# --------------------------------------------------
# Working Directory
# --------------------------------------------------
WORKDIR /app

# --------------------------------------------------
# Copy Requirements
# --------------------------------------------------
COPY requirements.txt .

# --------------------------------------------------
# Upgrade pip
# --------------------------------------------------
RUN pip install --upgrade pip setuptools wheel

# --------------------------------------------------
# Install Python Dependencies
# --------------------------------------------------
RUN pip install --no-cache-dir -r requirements.txt

# --------------------------------------------------
# Copy Source Code
# --------------------------------------------------
COPY . .

# --------------------------------------------------
# Create Output Directory
# --------------------------------------------------
RUN mkdir -p /app/output

# --------------------------------------------------
# Default Command
# --------------------------------------------------
CMD ["python", "main.py"]