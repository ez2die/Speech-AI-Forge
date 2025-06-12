# Multi-stage build for Speech-AI-Forge
FROM python:3.10-slim as base

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    rubberband-cli \
    git \
    wget \
    curl \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# GPU variant (CUDA)
FROM base as gpu
RUN pip install torch torchaudio torchvision --index-url https://download.pytorch.org/whl/cu121

# CPU variant
FROM base as cpu  
RUN pip install torch torchaudio torchvision --index-url https://download.pytorch.org/whl/cpu

# Choose the appropriate base stage based on build argument
ARG COMPUTE_TYPE=cpu
FROM ${COMPUTE_TYPE} as final

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p /app/data/speakers /app/models /app/logs

# Set permissions
RUN chmod +x /app/launch.py /app/webui.py

# Expose ports
EXPOSE 7870 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7870/health || exit 1

# Default command
CMD ["python", "launch.py"]
