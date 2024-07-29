import asyncio
import streamlit as st
import os
import shutil

from utils.init import initialize
from utils.counter import initialize_user_count, increment_user_count, decrement_user_count, get_user_count
from utils.file_upload import upload_files
from utils.interview_processing import process_interviews
from utils.TelegramSender import TelegramSender

UPLOAD_DIR = "uploads"

# Initialize TelegramSender
if 'telegram_sender' not in st.session_state:
    st.session_state.telegram_sender = TelegramSender()

# Increment user count if this is a new session
if 'counted' not in st.session_state:
    st.session_state.counted = True
    increment_user_count()

# Initialize user count
initialize_user_count()

# Register a function to decrement the count when the session ends
def on_session_end():
    decrement_user_count()

st.session_state.on_session_end = on_session_end

def start_over():
    keys_to_keep = ['counted', 'on_session_end', 'telegram_sender']
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]
    st.session_state.active_tab = None
    print("Session state cleared for Start Over")

def delete_uploaded_files(file_paths):
    for file_path in file_paths:
        try:
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

def main():
    image_path, footer_content = initialize()
    
    if image_path:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(image_path, use_column_width=True)

    # st.markdown(header_content)

    if st.button("התחל מחדש", use_container_width=True):
        start_over()

    file_paths = upload_files()
    if file_paths:
        if len(file_paths) > 5:
            st.error("לא ניתן להעלות יותר מ-5 קבצים.")
            return
        st.session_state['file_paths'] = file_paths

    if st.button("תמלל", use_container_width=True):
        if 'file_paths' not in st.session_state or not st.session_state['file_paths']:
            st.error("נא להעלות קבצים תחילה.")
            return

        edited_texts = process_interviews(st.session_state['file_paths'])
        st.session_state['edited_texts'] = edited_texts

        if edited_texts:
            all_texts_combined = []
            for file_name, transcriptions in edited_texts.items():
                if isinstance(transcriptions, list):
                    transcriptions = [t for t in transcriptions if t is not None]
                    if all(isinstance(t, str) for t in transcriptions):
                        file_text = "\n".join(transcriptions)
                        st.text_area(f"טקסט שחולץ מ-{file_name}", value=file_text, height=200)
                        all_texts_combined.append(file_text)
                    else:
                        st.error(f"תמלול עבור {file_name} אינו במבנה נכון.")
                else:
                    st.error(f"לא ניתן לעבד את התמלול עבור {file_name}.")
            
            if all_texts_combined:
                all_texts_combined = "\n\n".join(all_texts_combined)
                st.session_state['all_texts_combined'] = all_texts_combined
                asyncio.run(send_telegram_message(all_texts_combined))
                
                # Delete uploaded files after successful processing
                delete_uploaded_files(st.session_state['file_paths'])
                st.success("הקבצים שהועלו נמחקו בהצלחה.")
                
                # Clear file_paths from session state
                del st.session_state['file_paths']
            else:
                st.error("לא הצלחנו לחלץ טקסט מהקבצים שהועלו.")

    user_count = get_user_count(formatted=True)
    footer_with_count = f"{footer_content}\n\n<p class='user-count'>סה\"כ משתמשים: {user_count}</p>"
    st.markdown(footer_with_count, unsafe_allow_html=True)

async def send_telegram_message(text):
    sender = st.session_state.telegram_sender
    try:
        await sender.send_message(text, "Transcribe Videos or Audios to text")
    finally:
        await sender.close_session()
        
if __name__ == "__main__":
    main()