import streamlit as st

from content.cert.login import language_section
from content.verify_cert.user_content import user_content
from util import get_config, t, init_session_states

init_session_states()

st.set_page_config(page_title="Mittweida Certificate Generator", page_icon="🎓")

if not st.session_state.language_set:
    language_section()

if st.session_state.language_set:
    config = get_config()

    user_content(config)