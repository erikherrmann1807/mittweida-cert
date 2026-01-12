import streamlit as st

from content.landing_page.imprint import imprint_section
from content.landing_page.privacy_policy import privacy_policy_section
from content.landing_page.statistics import statistics_section


def show_landing_page():
    st.title("Herzlich Willkommen!")
    privacy_policy_section()
    imprint_section()
    statistics_section()
