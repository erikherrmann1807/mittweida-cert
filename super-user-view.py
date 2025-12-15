import streamlit as st

from content.super_user.add_admin import add_admin
from content.super_user.navigation import navigation
from util import get_config, init_session_states

init_session_states()

config = get_config()

st.set_page_config(page_title=config['texts'][st.session_state.language]['super_user']['page_info'], page_icon="🎓")

navigation(config)
