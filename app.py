import streamlit as st
import os, subprocess
from TTS.api import TTS

st.set_page_config(page_title="Voice Clone Studio", layout="centered")

# ---------- UI STYLE ----------
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🎙️ Gujarati Voice Clone → Talking Photo")

img = st.file_uploader("Upload Photo", type=["jpg","png","jpeg"])
voice = st.file_uploader("Upload Voice Sample (10–20s wav)", type=["wav"])
lyrics = st.file_uploader("Upload lyrics.txt", type=["txt"])

generate = st.button("Generate Video")

# ---------- MAIN ----------
if generate:

    if not (img and voice and lyrics):
        st.warning("Upload all 3 files")
        st.stop()

    os.makedirs("inputs", exist_ok=True)

    open("inputs/face.jpg","wb").write(img.read())
    open("inputs/ref.wav","wb").write(voice.read())
    open("inputs/lyrics.txt","wb").write(lyrics.read())

    text = open("inputs/lyrics.txt", encoding="utf-8").read()

    st.info("Loading voice model...")
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

    st.info("Generating cloned speech...")
    tts.tts_to_file(
        text=text,
        speaker_wav="inputs/ref.wav",
        language="gu",
        file_path="speech.wav"
    )

    st.info("Running lip sync...")

    subprocess.run([
        "python","Wave2Lip/inference.py",
        "--checkpoint_path","Wave2Lip/checkpoints/wav2lip_gan.pth",
        "--face","inputs/face.jpg",
        "--audio","speech.wav",
        "--outfile","output.mp4"
    ])

    st.success("Done!")

    st.video("output.mp4")

    with open("output.mp4","rb") as f:
        st.download_button("Download Video", f, "output.mp4")
