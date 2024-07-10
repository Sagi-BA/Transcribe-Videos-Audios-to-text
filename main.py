import asyncio
import streamlit as st

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

def main():
    header_content, footer_content = initialize()
    st.markdown(header_content)

    # Add custom CSS for button styling
    st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #0099ff;
        color: white;
        font-size: 20px;
        font-weight: bold;
        border: 2px solid #0099ff;
        border-radius: 10px;
        padding: 10px 24px;
        margin: 10px 0px;
    }
    div.stButton > button:hover {
        background-color: #0077cc;
        border-color: #0077cc;
    }
    </style>""", unsafe_allow_html=True)

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
                # Join the list of transcriptions for each file
                file_text = "\n".join(transcriptions)
                st.text_area(f"טקסט שחולץ מ-{file_name}", value=file_text, height=200)
                all_texts_combined.append(file_text)

            # Join all file transcriptions
            all_texts_combined = "\n\n".join(all_texts_combined)
            st.session_state['all_texts_combined'] = all_texts_combined

            # Send text to Telegram asynchronously
            asyncio.run(send_telegram_message(all_texts_combined))            
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