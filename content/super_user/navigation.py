import streamlit as st
from streamlit_option_menu import option_menu

from content.super_user.add_admin import add_admin
from content.super_user.manage_database import manage_database


def navigation(config):
    with st.sidebar.title("Navigation"):
        selected_page = option_menu(
            menu_title="Navigation",
            options=["Admin hinzufügen", "Zertifikate verwalten"],
            icons=["person-fill-add", "database-fill-gear"],
            menu_icon=" ",
            default_index=0
        )

    st.title(config['texts'][st.session_state.language]['super_user']['header'])

    if selected_page == "Admin hinzufügen":
        add_admin(config)
    if selected_page == "Zertifikate verwalten":
        manage_database()
