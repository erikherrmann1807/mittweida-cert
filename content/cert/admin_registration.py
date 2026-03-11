import streamlit as st

from src.api.wrapper import check_existing_user, send_admin_registration
from util import get_config, validate_email

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
            elif not name_query or not email_query or not affiliation_query:
                st.error(admin_registration_cfg['error_form'])
            elif not validate_email(email=email_query):
                st.error(admin_registration_cfg['not_email'])
            else:
                try:
                    result = send_admin_registration(to_email=admin_registration_cfg['system_admin_email'],
                                                     email=email_query,
                                                     name=name_query, affiliation=affiliation_query,
                                                     systemadmin_email=admin_registration_cfg[
                                                         'system_admin_email'])
                    if result == "sent successfully":
                        st.success(admin_registration_cfg['success_registration'])
                except Exception as e:
                    st.error(str(e) + result)

    st.stop()
