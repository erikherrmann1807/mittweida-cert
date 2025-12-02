import os

import streamlit as st

from src.database.operations import insert_csv
from util import get_config, get_logo_path

config = get_config()

def admin_content():
    admin_cfg = config['texts']['admin_content']
    st.markdown(admin_cfg['header'], unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(admin_cfg['upload_certs'])
        uploaded_file = st.file_uploader(admin_cfg['upload_csv'], type=["csv"],
                                         accept_multiple_files=True)
        uploaded_logo = st.file_uploader(admin_cfg['upload_logo'], type=["png"],)
        institution = st.text_input(admin_cfg['institution'],)

        if st.button(label=admin_cfg['confirm_upload_button']):
            file_name = uploaded_logo.name
            logo_path = os.path.join(get_logo_path(), file_name)
            with open(logo_path, "wb") as file:
                file.write(uploaded_logo.getbuffer())
            if institution and uploaded_file:
                insert_csv(uploaded_file, institution, logo_path)
                st.success(admin_cfg['upload_success'])
            else:
                st.warning(admin_cfg['upload_warning'])