FROM python:3.10-slim

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

# Clone and setup Wave2Lip
RUN git clone https://github.com/Rudrabha/Wav2Lip.git Wave2Lip && \
    cd Wave2Lip && \
    pip install --no-cache-dir -r requirements.txt

# Download Wave2Lip pretrained model
RUN mkdir -p Wave2Lip/checkpoints && \
    wget -O Wave2Lip/checkpoints/wav2lip_gan.pth \
    "https://iiitaphyd-my.sharepoint.com/personal/radrabha_m_research_iiit_ac_in/_layouts/15/download.aspx?share=EdjI7bZlgApMqsVoEUUXpLsBxqXbn5z8VTmoxp55YNDcIA" || \
    echo "Model download may require manual intervention"

COPY . .

EXPOSE 7860
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
