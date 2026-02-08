FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    wget \
    libsndfile1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Clone Wave2Lip (but don't install its requirements as they conflict)
RUN git clone https://github.com/Rudrabha/Wav2Lip.git Wave2Lip

# Download Wave2Lip pretrained model
RUN mkdir -p Wave2Lip/checkpoints && \
    wget -O Wave2Lip/checkpoints/wav2lip_gan.pth \
    "https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0/wav2lip_gan.pth" || \
    wget -O Wave2Lip/checkpoints/wav2lip_gan.pth \
    "https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth" || \
    echo "Model download may require manual intervention"

# Install face_detection separately
RUN pip install --no-cache-dir face-alignment

COPY . .

EXPOSE 7860
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
