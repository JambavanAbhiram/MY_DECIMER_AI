FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# ------------------------------------------------------------
# System dependencies
# ------------------------------------------------------------

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    wget \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libx11-6 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# Copy requirements
# ------------------------------------------------------------

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

# ------------------------------------------------------------
# Copy project
# ------------------------------------------------------------

COPY . .

# ------------------------------------------------------------
# Create required folders
# ------------------------------------------------------------

RUN mkdir -p \
    core/output \
    core/outputs \
    core/temp \
    core/logs

# ------------------------------------------------------------
# Default command
# ------------------------------------------------------------

CMD ["python", "main.py"]