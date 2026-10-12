---
title:   TalkingAvatar Studio
emoji: 🎭
colorFrom: purple
colorTo: pink
sdk: docker
pinned: false
license: mit
---

# 🎭   TalkingAvatar Studio

Create stunning talking avatar videos with **full facial expressions**, **head movements**, and **lip sync** from a single photo!

## ✨ Features

- **🎙️   Voice Cloning**: Uses XTTS v2 for high-quality   speech synthesis
- **🎭 Expressive Animations**: SadTalker generates realistic facial expressions (not just lip sync!)
- **🎯 Head Pose Generation**: Natural head movements synchronized with speech
- **⚡ Expression Control**: Adjust animation intensity from subtle to dramatic
- **💎 Face Enhancement**: Optional GFPGAN for improved output quality

## 🚀 How It Works

1. **Upload a Photo** - A clear, front-facing portrait works best
2. **Provide Voice Sample** - 10-20 seconds of reference audio (WAV)
3. **Add Your Lyrics** - Text in   for speech synthesis
4. **Generate!** - Get an expressive talking avatar video

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| TTS Engine | Coqui XTTS v2 |
| Facial Animation | SadTalker |
| Face Enhancement | GFPGAN |
| Framework | Streamlit |
| Runtime | Python 3.10 |

## 📦 Local Development

```bash
# Clone the repository
git clone <repo-url>
cd project

# Install dependencies
pip install -r requirements.txt

# Clone SadTalker and download models
git clone https://github.com/OpenTalker/SadTalker.git
# Download models following SadTalker documentation

# Run the app
streamlit run app.py
```

## 🐳 Docker

```bash
docker build -t talking-avatar .
docker run -p 7860:7860 talking-avatar
```

## ⚙️ Configuration

| Setting | Description |
|---------|-------------|
| Expression Intensity | 0.5-2.0x multiplier for facial movements |
| Still Mode | Reduces head motion while keeping facial animation |
| Face Enhancement | Uses GFPGAN to improve output quality |

## 📄 License

MIT License - Feel free to use and modify!

---

Check out the [Hugging Face Spaces config reference](https://huggingface.co/docs/hub/spaces-config-reference) for deployment options.
