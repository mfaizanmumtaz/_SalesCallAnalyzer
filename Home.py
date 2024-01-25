from deepgram import DeepgramClient,FileSource,PrerecordedOptions
import streamlit as st
from pdf_manager import download_pdf
import os,json
# from dotenv import load_dotenv
# load_dotenv()

st.set_page_config("Phone Call Analyzer", layout="wide",page_icon="icons/ico.png")

st.markdown("#### Welcome to Customer Support Call Analyzer! 👋")
st.write("This app will analyze Customer Support Call and provide you with a report on the call. The report will include information on the call's content, sentiment, and sales techniques.")

def _transcriber(audio_file):
    if "audio" not in os.listdir():
        os.mkdir("audio")
    audio_file_path = os.path.join("audio", audio_file.name)
    with st.spinner("Audio file is being transcribed..."):
        try:
            with open(audio_file_path, "wb") as file:
                file.write(audio_file.read())

            deepgram = DeepgramClient(os.environ.get("DG_API_KEY"))

            with open(audio_file_path, "rb") as file:
                buffer_data = file.read()

            payload: FileSource = {
                "buffer": buffer_data}

            options = PrerecordedOptions(
                smart_format = True,
                diarize=True,
                paragraphs=True,
                punctuate=True,
                model = 'nova-2',
            )
            file_response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)

            return json.loads(file_response.to_json())['results']['channels'][0]['alternatives'][0]["paragraphs"]["transcript"]

        except Exception as e:
            st.warning(f"An error occurred: {e}")
            return None
        
        finally:
            os.remove(audio_file_path)


audio_file = st.file_uploader("**Please Upload Audio File**",type=["wav", "mp3", "m4a", "ogg"])

if st.button("Submit"):
    if audio_file is not None:
        if "transcript" in st.session_state:
            del st.session_state["transcript"]

        if "transcript" not in st.session_state:
            response = _transcriber(audio_file)
            if response is not None:
                st.session_state.transcript = response
    
    else:
        st.warning("Please upload audio file.")

if "transcript" in st.session_state:
        with st.expander("View Audio Transcription"):
            transcript = st.session_state["transcript"]
            st.write(transcript)
            download_pdf(transcript,"transcript")

        st.success("Audio successfully transcribed. Please navigate to the sidebar pages for actions.")
        st.sidebar.success("Select Above Options.")