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
ARG CACHEBUST=2026-02-08-v3

# Clone SadTalker
RUN git clone --depth 1 https://github.com/OpenTalker/SadTalker.git

# Create checkpoint directories
RUN mkdir -p SadTalker/checkpoints SadTalker/gfpgan/weights

# Download SadTalker models (NO || true - we WANT failures to be visible)
RUN cd SadTalker && \
    echo "Downloading SadTalker checkpoints..." && \
    wget --no-verbose --show-progress -O checkpoints/auido2exp_00300-model.pth \
    "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/auido2exp_00300-model.pth" && \
    wget --no-verbose --show-progress -O checkpoints/auido2pose_00140-model.pth \
    "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/auido2pose_00140-model.pth" && \
    wget --no-verbose --show-progress -O checkpoints/mapping_00229-model.pth.tar \
    "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00229-model.pth.tar" && \
    wget --no-verbose --show-progress -O checkpoints/mapping_00109-model.pth.tar \
    "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00109-model.pth.tar" && \
    wget --no-verbose --show-progress -O checkpoints/facevid2vid_00189-model.pth.tar \
    "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/facevid2vid_00189-model.pth.tar" && \
    wget --no-verbose --show-progress -O checkpoints/epoch_20.pth \
    "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/epoch_20.pth" && \
    wget --no-verbose --show-progress -O gfpgan/weights/GFPGANv1.4.pth \
    "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.4/GFPGANv1.4.pth" && \
    echo "✅ Verifying all checkpoints exist..." && \
    ls -lh checkpoints/ && \
    ls -lh gfpgan/weights/

# Copy application files
COPY . .

EXPOSE 7860
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
