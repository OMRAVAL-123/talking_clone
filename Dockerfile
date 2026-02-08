# Use Python 3.10 for stable TTS operation
FROM python:3.10-slim

# Automatically agree to Coqui TTS TOS
ENV COQUI_TOS_AGREED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (cmake via apt, not pip)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    wget \
    curl \
    libsndfile1 \
    libgomp1 \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    cmake \
    build-essential \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Upgrade pip and setuptools (NOT cmake - use system cmake)
RUN pip install --upgrade pip setuptools wheel

# Install dlib using system cmake
RUN pip install --no-cache-dir dlib-bin

# Install TTS first to lock numpy version (TTS requires numpy==1.22.0 for Python 3.10)
RUN pip install --no-cache-dir TTS==0.22.0

# Install remaining Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Cache bust for checkpoint downloads - change this to force rebuild
ARG CACHEBUST=2026-02-08-v4

# Clone SadTalker
RUN git clone --depth 1 https://github.com/OpenTalker/SadTalker.git

# Download SadTalker models using official script
RUN cd SadTalker && \
    echo "Downloading SadTalker checkpoints using official script..." && \
    bash scripts/download_models.sh && \
    echo "✅ Verifying all checkpoints exist..." && \
    ls -lh checkpoints/ && \
    ls -lh gfpgan/weights/

# Copy application files
COPY . .

EXPOSE 7860
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
