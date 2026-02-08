import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="streamlit.watcher.local_sources_watcher")
warnings.filterwarnings("ignore", message=".*Torchaudio.*backend.*")

import streamlit as st
import os
import subprocess
import sys
from TTS.api import TTS

st.set_page_config(
    page_title="Voice Clone Studio", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- UI STYLE ----------
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown("""
    <div class="header-container">
        <h1 class="main-title">🎙️ Voice Clone Studio</h1>
        <p class="subtitle">Transform your photos into expressive talking avatars with AI-powered voice cloning</p>
        <div class="tech-badges">
            <span class="badge">🎭 SadTalker</span>
            <span class="badge">🗣️ XTTS v2</span>
            <span class="badge">✨ GFPGAN</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# ---------- MAIN CONTENT ----------
# Create three columns for better layout
left_spacer, main_col, right_spacer = st.columns([1, 6, 1])

with main_col:
    # ---------- FILE UPLOADERS ----------
    st.markdown('<div class="section-title">📤 Upload Your Assets</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="upload-card">', unsafe_allow_html=True)
        img = st.file_uploader("📷 Photo", type=["jpg", "png", "jpeg"], help="Upload a clear, front-facing photo")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="upload-card">', unsafe_allow_html=True)
        voice = st.file_uploader("🎤 Voice Sample", type=["wav"], help="10-20 seconds of clear speech")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="upload-card">', unsafe_allow_html=True)
        lyrics = st.file_uploader("📝 Script/Lyrics", type=["txt"], help="Text to be spoken")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------- ADVANCED OPTIONS ----------
    with st.expander("⚙️ Advanced Animation Settings", expanded=False):
        col_a, col_b = st.columns(2)
        
        with col_a:
            expression_scale = st.slider(
                "Expression Intensity", 
                min_value=0.5, 
                max_value=2.0, 
                value=1.0, 
                step=0.1,
                help="Higher values = more expressive facial movements"
            )
        
        with col_b:
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

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Generate button
    generate = st.button("🚀 Generate Expressive Video", type="primary", use_container_width=True)

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
                language="hi",  # Using Hindi for Gujarati text (XTTS clones voice regardless of language)
                file_path=speech_path
            )
        except Exception as e:
            st.error(f"Speech generation failed: {e}")
            st.stop()

    # ---------- SadTalker: Generate Expressive Animation ----------
    with st.spinner("🎭 Generating facial expressions and head movements..."):
        
        sadtalker_cmd = [
            sys.executable,
            "inference.py",  # Run from SadTalker directory
            "--driven_audio", f"../{speech_path}",  # Relative to SadTalker/
            "--source_image", f"../{face_path}",    # Relative to SadTalker/
            "--result_dir", "../results",            # Relative to SadTalker/
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
                cwd="SadTalker",  # ⭐ THIS IS THE KEY FIX - run from SadTalker directory
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
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<div class="success-container">', unsafe_allow_html=True)
        st.markdown("""
            <div class="success-header">
                <h2>✅ Video Generated Successfully!</h2>
                <p>Your expressive talking avatar is ready</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Video player in centered container
        st.markdown('<div class="video-container">', unsafe_allow_html=True)
        st.video(output_path)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Prominent download section
        st.markdown("<br>", unsafe_allow_html=True)
        col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
        with col_dl2:
            with open(output_path, "rb") as f:
                st.download_button(
                    label="📥 Download Your Video",
                    data=f,
                    file_name="talking_avatar.mp4",
                    mime="video/mp4",
                    use_container_width=True
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error("❌ No output video found. Check SadTalker logs for details.")

# ---------- FOOTER ----------
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div class="footer-container">
        <div class="tips-section">
            <h3>💡 Pro Tips</h3>
            <ul>
                <li>📸 Use a clear, well-lit, front-facing photo for best results</li>
                <li>🎤 Provide 10-20 seconds of clear voice sample without background noise</li>
                <li>🎭 Adjust expression intensity for more or less dramatic facial movements</li>
                <li>✨ Enable GFPGAN enhancement for higher quality output</li>
            </ul>
        </div>
        <div class="tech-info">
            <p><strong>Powered by:</strong> SadTalker (facial animation) • XTTS v2 (voice cloning) • GFPGAN (face enhancement)</p>
        </div>
    </div>
""", unsafe_allow_html=True)
