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

# Clone Wav2Lip
RUN git clone https://github.com/Rudrabha/Wav2Lip.git

# Download Wav2Lip models from Hugging Face with authentication
# Note: HF_TOKEN is automatically available as a build secret in HF Spaces
RUN mkdir -p Wav2Lip/checkpoints && \
    wget --header="Authorization: Bearer ${HF_TOKEN}" \
    'https://huggingface.co/Nekochu/Wav2Lip/resolve/main/wav2lip_gan.pth' \
    -O 'Wav2Lip/checkpoints/wav2lip_gan.pth' && \
    mkdir -p Wav2Lip/face_detection/detection/sfd && \
    wget --header="Authorization: Bearer ${HF_TOKEN}" \
    'https://huggingface.co/Nekochu/Wav2Lip/resolve/main/s3fd.pth' \
    -O 'Wav2Lip/face_detection/detection/sfd/s3fd.pth' && \
    echo "✅ Wav2Lip models downloaded successfully"

# Fix numpy compatibility issue in SadTalker (replace deprecated np.float with float)
RUN sed -i "s/np.float/float/g" SadTalker/src/face3d/util/my_awing_arch.py && \
    sed -i "s/trans_params = np.array(\[w0, h0, s, t\[0\], t\[1\]\])/trans_params = np.array([float(w0), float(h0), float(s), float(t[0]), float(t[1])])/g" SadTalker/src/face3d/util/preprocess.py

# Copy application files
COPY . .

EXPOSE 7860
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
