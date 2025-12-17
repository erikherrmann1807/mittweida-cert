import streamlit as st
from streamlit_option_menu import option_menu

from content.landing_page.imprint import imprint_section
from content.landing_page.privacy_policy import privacy_policy_section
from content.landing_page.statistics import statistics_section
from content.login import login_gate
from util import Role
from content.admin_registration import admin_registration


def show_landing_page():


    st.title("Herzlich Willkommen!")
    privacy_policy_section()
    imprint_section()
    statistics_section()


