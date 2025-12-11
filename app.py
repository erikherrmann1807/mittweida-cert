import streamlit as st

from content.admin_content import admin_content
from content.admin_registration import admin_registration
from content.login import login_gate, language_section, init_session_states, role_selection
from content.user_content import user_content
from util import get_config

config = get_config()

st.set_page_config(page_title=config['texts']['general']['cert_name'], page_icon="🎓")

login_gate()

if st.session_state.admin_authenticated:
    admin_content()
else:
    user_content()

if st.session_state.language_set:
    role_selection()


    if not st.session_state.role:
        admin_registration()

    if st.session_state.role:
        login_gate()

    if st.session_state.admin_authenticated:
        admin_content()
    else:
        user_content()
