import streamlit as st

from content.cert.admin_content import admin_content
from content.cert.admin_registration import admin_registration
from content.cert.login import language_section, role_selection, login_gate
from content.cert.user_content import user_content
from util import get_config, init_session_states, Role

config = get_config()

init_session_states()

st.set_page_config(page_title=config['texts'][st.session_state.language]['general']['cert_name'], page_icon="🎓")

if not st.session_state.language_set:
    language_section()

if st.session_state.language_set:

    if not st.session_state.role:
        role_selection()

    if st.session_state.role == Role.Registration:
        admin_registration()

    if st.session_state.role == Role.User or st.session_state.role == Role.Admin:
        login_gate(st.session_state.role)

    if st.session_state.admin_authenticated:
        admin_content()
    else:
        user_content()
