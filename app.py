import streamlit as st
from streamlit_option_menu import option_menu

from content.cert.admin_content import admin_content
from content.cert.admin_registration import admin_registration
from content.cert.login import language_section, login_gate
from content.cert.user_content import user_content
from content.landing_page.landing_page import show_landing_page
from util import get_config, Role, init_session_states, reset_login

config = get_config()

init_session_states()

st.set_page_config(page_title=config['texts'][st.session_state.language]['general']['cert_name'], page_icon="🎓")

if not st.session_state.language_set:
    language_section()
    st.stop()

if st.session_state.language_set:
    with st.sidebar.title("Navigation"):
        selected_page = option_menu(
            menu_title="Navigation",
            options=["Landing Page", "User Login", "Admin Login", "Admin Registrierung"],
            icons=["house", "box-arrow-in-right", "box-arrow-in-right", "person-add"],
            menu_icon=" ",
            default_index=0
        )

if st.session_state.selected_page_prev != selected_page:
    if not st.session_state.selected_page_prev is None:
        reset_login()
    st.session_state.selected_page_prev = selected_page

if selected_page == "Landing Page":
    show_landing_page()

elif selected_page == "Admin Registrierung":
    st.session_state.role = Role.Registration
    admin_registration()

elif selected_page == "User Login":
    st.session_state.role = Role.User
    login_gate(Role.User)

    if st.session_state.user_authenticated:
        user_content()

elif selected_page == "Admin Login":
    st.session_state.role = Role.Admin
    login_gate(Role.Admin)

    if st.session_state.admin_authenticated:
        admin_content()
