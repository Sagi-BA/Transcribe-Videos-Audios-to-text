import streamlit as st
import os
import requests

UPLOAD_DIR = 'uploads'

def upload_files():
    st.header("העלאת קבצי אודיו/וידאו")

    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    # upload_option = st.radio("בחר אפשרות העלאה", ["קובץ מקומי", "קישור לענן"])

    uploaded_file_paths = []

    # if upload_option == "קובץ מקומי":
    uploaded_files = st.file_uploader("בחר עד 5 קבצי אודיו או וידאו", type=["mp3", "wav", "mp4"], accept_multiple_files=True)
    if uploaded_files is not None:
        for uploaded_file in uploaded_files:
            if len(uploaded_file_paths) >= 5:
                st.warning("ניתן להעלות עד 5 קבצים בלבד.")
                break
            file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            uploaded_file_paths.append(file_path)
            st.success(f"הקובץ {uploaded_file.name} הועלה בהצלחה.")
        return uploaded_file_paths

    return uploaded_file_paths
