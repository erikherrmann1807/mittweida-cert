import streamlit as st

from content.landing_page.contact import contact_section
from content.landing_page.imprint import imprint_section
from content.landing_page.privacy_policy import privacy_policy_section
from content.landing_page.statistics import statistics_section


from util import get_config

config = get_config()


def show_landing_page():
    st.title(f"{config['texts'][st.session_state.language]['landing_page']['title']}")
    privacy_policy_section()
    imprint_section()
    #statistics_section()
    contact_section()
