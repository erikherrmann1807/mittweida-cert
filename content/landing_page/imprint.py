import streamlit as st

from util import get_config

config = get_config()

def imprint_section():
    imprint_cfg = config['texts'][st.session_state.language]['landing_page']['imprint']
    with st.expander(f"{imprint_cfg['header']}"):
        st.markdown(f"{imprint_cfg['imprint_notice']}", unsafe_allow_html=True)
