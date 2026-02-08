FROM python:3.10

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg git wget

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN git clone https://github.com/Rudrabha/Wave2Lip.git
RUN wget https://storage.googleapis.com/wave2lip_models/wave2lip_gan.pth -P Wave2Lip

COPY . .

EXPOSE 7860

CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
