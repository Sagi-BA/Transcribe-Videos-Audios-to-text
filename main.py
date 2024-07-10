import streamlit as st
from utils.init import initialize
from utils.counter import initialize_user_count, increment_user_count, decrement_user_count, get_user_count
from utils.file_upload import upload_files
from utils.interview_processing import process_interviews

from utils.TelegramSender import TelegramSender
from io import BytesIO

# Initialize logging
# logging.basicConfig(level=logging.INFO)
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
    # Keys to keep
    keys_to_keep = ['counted', 'on_session_end', 'google_model', 'telegram_sender']
    
    # Remove all keys except the ones we want to keep
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]
    
    # Reset the active_tab
    st.session_state.active_tab = None
    
    print("Session state cleared for Start Over")

def main():
    # Initialize Streamlit configuration and load resources
    header_content, footer_content = initialize()

    # Header
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

    # Handle the "Start Over" button click
    if st.button("התחל מחדש", use_container_width=True):
        start_over()        

    # Handle file upload    
    file_paths = upload_files()
    if file_paths:
        st.session_state['file_paths'] = file_paths

    if st.button("תמלל", use_container_width=True):
        print("תמלול")
        if not file_paths:
            st.error("נא להעלות קבצים תחילה.")
            return        
        
        st.info(f"מנסה לעבד קבצים: {st.session_state['file_paths']}")
        edited_texts = process_interviews(st.session_state['file_paths'])
        st.session_state['edited_texts'] = edited_texts
        for transcription in edited_texts.items():                        
            st.subheader(transcription)
            st.divider()

    user_count = get_user_count(formatted=True)
    
    footer_with_count = f"{footer_content}\n\n<p class='user-count'>סה\"כ משתמשים: {user_count}</p>"
    st.markdown(footer_with_count, unsafe_allow_html=True)

if __name__ == "__main__":
    main()