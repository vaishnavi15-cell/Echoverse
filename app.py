import streamlit as st
from kittentts import KittenTTS
import io
import soundfile as sf
import random

# --- Streamlit page config ---
st.set_page_config(page_title="EchoVerse – AI Audiobook Tool", layout="wide", page_icon="🎙")

# --- Load TTS ---
@st.cache_resource
def load_tts():
    return KittenTTS("KittenML/kitten-tts-nano-0.1")

tts_model = load_tts()

# --- Offline Text Rewriting Function ---
def rewrite_text(text, tone):
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    rewritten_sentences = []

    if tone == "Neutral":
        rewritten_sentences = sentences

    elif tone == "Suspenseful":
        suspense_prefixes = ["Suddenly, ", "In the shadows, ", "Unbeknownst to all, "]
        suspense_suffixes = ["… tension filled the air.", "… no one could predict what happens next.", "… something felt off."]
        for s in sentences:
            prefix = random.choice(suspense_prefixes)
            suffix = random.choice(suspense_suffixes)
            rewritten_sentences.append(f"{prefix}{s}{suffix}")

    elif tone == "Inspiring":
        inspiring_prefixes = ["Believe in yourself: ", "With courage, ", "Every challenge is an opportunity: "]
        inspiring_suffixes = [" – you can achieve greatness.", " – keep moving forward!", " – your potential is limitless."]
        for s in sentences:
            prefix = random.choice(inspiring_prefixes)
            suffix = random.choice(inspiring_suffixes)
            rewritten_sentences.append(f"{prefix}{s}{suffix}")

    return ' '.join(rewritten_sentences)

# --- Background Image ---
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://plus.unsplash.com/premium_photo-1669863547357-b7d064cedaac?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NXx8bGlnaHQlMjBiYWNrZ3JvdW5kc3xlbnwwfHwwfHx8MA%3D%3D");
         background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --- Sidebar ---
st.sidebar.header("Settings")
tone = st.sidebar.radio("Choose Tone", ["Neutral", "Suspenseful", "Inspiring"])
voices = tts_model.available_voices
voice_choice = st.sidebar.selectbox("Choose Voice", voices if voices else ["expr-voice-2-f"])

# --- Main App ---
st.title("🎧 EchoVerse – AI-Powered Audiobook Creation")

text_input = st.text_area("Enter text:", height=150)

if st.button("Rewrite Text"):
    if text_input.strip():
        rewritten = rewrite_text(text_input, tone)
        st.session_state["rewritten"] = rewritten

        st.subheader("📜 Original vs Rewritten")
        col1, col2 = st.columns(2)
        with col1:
            st.text_area("Original Text", text_input, height=200)
        with col2:
            st.text_area(f"{tone} Rewrite", rewritten, height=200)
    else:
        st.warning("⚠️ Please enter some text.")

if st.button("Generate Audio"):
    if "rewritten" in st.session_state:
        try:
            rewritten = st.session_state["rewritten"]
            audio_array = tts_model.generate(rewritten, voice=voice_choice)

            # Convert NumPy array to WAV
            wav_buffer = io.BytesIO()
            sf.write(wav_buffer, audio_array, samplerate=22050, format="WAV")
            wav_buffer.seek(0)

            # Play + Download
            st.success("✅ Audio generated successfully!")
            st.audio(wav_buffer, format="audio/wav")
            st.download_button(
                label="💾 Download Audio",
                data=wav_buffer,
                file_name="echoverse_output.wav",
                mime="audio/wav"
            )
        except Exception as e:
            st.error(f"TTS generation failed: {e}")
    else:
        st.warning("⚠️ Please rewrite text first before generating audio.")
