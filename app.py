import streamlit as st
import os
import subprocess
import sys
from TTS.api import TTS

st.set_page_config(page_title="Voice Clone Studio", layout="centered")

# ---------- UI STYLE ----------
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🎙️ Gujarati TalkingAvatar → Expressive Video")
st.caption("Powered by SadTalker for full facial expressions + head movements")

# ---------- FILE UPLOADERS ----------
col1, col2 = st.columns(2)
with col1:
    img = st.file_uploader("📷 Upload Photo", type=["jpg", "png", "jpeg"])
with col2:
    voice = st.file_uploader("🎤 Voice Sample (10–20s wav)", type=["wav"])

lyrics = st.file_uploader("📝 Upload lyrics.txt", type=["txt"])

# ---------- ADVANCED OPTIONS ----------
with st.expander("🎚️ Animation Settings"):
    expression_scale = st.slider(
        "Expression Intensity", 
        min_value=0.5, 
        max_value=2.0, 
        value=1.0, 
        step=0.1,
        help="Higher values = more expressive facial movements"
    )
    still_mode = st.checkbox(
        "Still Mode (reduce head motion)", 
        value=False,
        help="Keep head relatively still while animating face"
    )
    enhance_face = st.checkbox(
        "Enhance Face Quality (GFPGAN)", 
        value=True,
        help="Use GFPGAN to improve output face quality"
    )

generate = st.button("🚀 Generate Expressive Video", type="primary")

# ---------- MAIN PROCESSING ----------
if generate:

    if not (img and voice and lyrics):
        st.warning("⚠️ Please upload all 3 files: Photo, Voice Sample, and Lyrics")
        st.stop()

    os.makedirs("inputs", exist_ok=True)
    os.makedirs("results", exist_ok=True)

    # Save uploaded files
    face_path = "inputs/face.jpg"
    voice_path = "inputs/ref.wav"
    lyrics_path = "inputs/lyrics.txt"
    
    with open(face_path, "wb") as f:
        f.write(img.read())
    with open(voice_path, "wb") as f:
        f.write(voice.read())
    with open(lyrics_path, "wb") as f:
        f.write(lyrics.read())

    text = open(lyrics_path, encoding="utf-8").read()

    # ---------- TTS: Generate Speech ----------
    with st.spinner("🔊 Loading voice model (XTTS v2)..."):
        try:
            tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        except Exception as e:
            st.error(f"Failed to load TTS model: {e}")
            st.stop()

    speech_path = "speech.wav"
    with st.spinner("🎙️ Generating cloned speech..."):
        try:
            tts.tts_to_file(
                text=text,
                speaker_wav=voice_path,
                language="gu",
                file_path=speech_path
            )
        except Exception as e:
            st.error(f"Speech generation failed: {e}")
            st.stop()

    # ---------- SadTalker: Generate Expressive Animation ----------
    with st.spinner("🎭 Generating facial expressions and head movements..."):
        
        sadtalker_cmd = [
            sys.executable,
            "SadTalker/inference.py",
            "--driven_audio", speech_path,
            "--source_image", face_path,
            "--result_dir", "results",
            "--expression_scale", str(expression_scale),
        ]
        
        # Add optional flags
        if still_mode:
            sadtalker_cmd.append("--still")
        
        if enhance_face:
            sadtalker_cmd.extend(["--enhancer", "gfpgan"])
        
        try:
            result = subprocess.run(
                sadtalker_cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode != 0:
                st.error(f"SadTalker failed:\n{result.stderr}")
                st.stop()
                
        except subprocess.TimeoutExpired:
            st.error("Video generation timed out. Try a shorter audio or simpler image.")
            st.stop()
        except Exception as e:
            st.error(f"Animation failed: {e}")
            st.stop()

    # ---------- Find and Display Output ----------
    # SadTalker saves output in results/ directory
    output_files = []
    for f in os.listdir("results"):
        if f.endswith(".mp4"):
            output_files.append(os.path.join("results", f))
    
    if output_files:
        # Get the most recent output
        output_path = max(output_files, key=os.path.getctime)
        
        st.success("✅ Video generated successfully!")
        st.video(output_path)
        
        with open(output_path, "rb") as f:
            st.download_button(
                "📥 Download Video", 
                f, 
                "talking_avatar.mp4",
                mime="video/mp4"
            )
    else:
        st.error("No output video found. Check SadTalker logs.")

# ---------- FOOTER ----------
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
        <p>💡 <b>Tips:</b> Use a clear, front-facing photo for best results.</p>
        <p>SadTalker generates realistic head movements, facial expressions, and lip sync!</p>
    </div>
    """,
    unsafe_allow_html=True
)
