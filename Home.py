import streamlit as st
import assemblyai as aai
from pdf_manager import download_pdf
import os

aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

st.set_page_config("Phone Call Analyzer", layout="wide",page_icon="icons/ico.png")

st.markdown("#### Welcome to Customer Support Call Analyzer! 👋")
st.write("This app will analyze Customer Support Call and provide you with a report on the call. The report will include information on the call's content, sentiment, and sales techniques.")

def _transcriber(audio_file):
    if "audio" not in os.listdir():
        os.mkdir("audio")
    audio_file_path = os.path.join("audio", audio_file.name)
    with st.spinner("Audio file is being transcribed..."):
        try:
            with open(audio_file_path, "wb") as f:
                f.write(audio_file.read())

            config = aai.TranscriptionConfig(speaker_labels=True)
            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(audio_file_path, config).utterances 
            return "".join([f"Speaker {utterance.speaker}: {utterance.text}\n\n" for utterance in transcript])

        except Exception as e:
            st.warning("An error occurred:", e)
        finally:
            os.remove(audio_file_path)

def main():

    audio_file = st.file_uploader("**Please Upload Audio File**",type=["wav", "mp3", "m4a", "ogg"])

    if audio_file is not None:
        if "transcript" not in st.session_state:
            st.session_state.transcript = _transcriber(audio_file)

if __name__ == "__main__":
    main()

if "transcript" in st.session_state:
        with st.expander("View Audio Transcription"):
            st.write(st.session_state["transcript"])

            download_pdf(st.session_state["transcript"],"transcript")

        st.success("Audio successfully transcribed. Please navigate to the sidebar pages for actions.")
        st.sidebar.success("Select Above Options.")