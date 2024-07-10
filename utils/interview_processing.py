import json
from dotenv import load_dotenv
import streamlit as st
import os
from utils.gradio_client_wrapper import GradioClientWrapper

client_wrapper = GradioClientWrapper("benderrodriguez/transcribe")

# Load environment variables
load_dotenv()

# Define the path for the temporary audio files
TEMP_AUDIO_DIR = os.path.join(os.getcwd(), "temp_audio")

# Ensure the temporary directory exists
if not os.path.exists(TEMP_AUDIO_DIR):
    os.makedirs(TEMP_AUDIO_DIR)

def process_interviews(audio_file_paths):
    # st.header("עיבוד ראיונות")
    # st.info(f"מנסה לעבד את הקבצים: {audio_file_paths}")

    try:
        with st.spinner('Transcribing...'):
            transcriptions = client_wrapper.transcribe_audio(audio_file_paths)
            st.info("הקבצים תומללו מקול לטקסט STT!")

        edited_texts = {}
        for file_path, transcription in transcriptions.items():
            edited_texts[file_path] = transcription

        st.success("עיבוד הראיונות הושלם בהצלחה!")
        return edited_texts

    except Exception as e:
        st.error(f"שגיאה בעיבוד קובץ האודיו: {str(e)}")
        return ""

def edit_text(text, style, character_type):
    style_description = style.get('description', 'סגנון לא מוגדר')
    return f"{style_description}: {text} (דמות: {character_type})"

def save_results(data, filename):
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # This is for testing purposes. In the actual app, this function will be called from main.py
    st.write("This is a test run of the interview processing module.")
    # You would need to provide actual values for these parameters in a real run
    file_path = os.path.join("uploads", "iris bar on_small.mp3")
    process_interviews(file_path, {"some_style": {"description": "Test style"}}, "Test character", 60)
