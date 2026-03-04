import streamlit as st

from util import get_config

config = get_config()


def contact_section():
    contact_cfg = config['texts'][st.session_state.language]['landing_page']['contact']
    with st.expander(f"{contact_cfg['header']}"):
        st.markdown(f"{contact_cfg['contact_information']}", unsafe_allow_html=True)
