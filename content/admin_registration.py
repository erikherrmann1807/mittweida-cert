import streamlit as st

from src.auth.otp_mail.email import send_admin_registration_mail
from src.database.operations import check_existing_user
from util import get_config

config = get_config()


def admin_registration():
    admin_registration_cfg = config['texts'][st.session_state.language]['admin_registration']
    st.write(admin_registration_cfg['header'])
    with st.form(key="admin_registration_form"):
        name_query = st.text_input(admin_registration_cfg['name'])
        email_query = st.text_input(admin_registration_cfg['email'])
        affiliation_query = st.text_input(admin_registration_cfg['affiliation'])
        if st.form_submit_button(admin_registration_cfg['submit_button']):
            if check_existing_user(email=email_query, role=st.session_state.role):
                st.error(admin_registration_cfg['error_email'])
            elif name_query and email_query and affiliation_query:
                send_admin_registration_mail(admin_registration_cfg['system_admin_email'], email=email_query,
                                             name=name_query, affiliation=affiliation_query)
                st.success(admin_registration_cfg['success_registration'])
            else:
                st.error(admin_registration_cfg['error_form'])

    st.stop()