import streamlit as st

from src.database.operations import insert_csv
from util import get_config

config = get_config()

def admin_content():
    admin_cfg = config['texts']['admin_content']
    st.markdown(admin_cfg['header'], unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(admin_cfg['upload_certs'])
        uploaded_file = st.file_uploader(admin_cfg['upload_csv'], type=["csv"],
                                         accept_multiple_files=True)
        institution = st.text_input(admin_cfg['institution'],)

        if st.button(label=admin_cfg['confirm_upload_button']):
            if institution and uploaded_file:
                insert_csv(uploaded_file, institution)
                st.success(admin_cfg['upload_success'])
            else:
                st.warning(admin_cfg['upload_warning'])