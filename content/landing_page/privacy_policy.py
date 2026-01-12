import streamlit as st

from util import get_config

config = get_config()

def privacy_policy_section():
    data_privacy_cfg = config['texts'][st.session_state.language]['landing_page']['data_privacy']
    with st.expander(f"{data_privacy_cfg['header']}"):
        st.markdown(f"{data_privacy_cfg['privacy_policy']}", unsafe_allow_html=True)
