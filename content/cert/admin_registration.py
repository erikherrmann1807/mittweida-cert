import streamlit as st

from src.api.wrapper import check_existing_user, send_admin_registration, create_admin, check_admin_status
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
            admin_status = check_admin_status(email=email_query, role=st.session_state.role)
            if check_existing_user(email=email_query, role=st.session_state.role):
                #st.error(admin_registration_cfg['error_email'])
                if admin_status == "pending":
                    st.info("Sie haben bereits eine Anfrage gesendet. Diese wird momentan bearbeitet")
                elif admin_status == "accepted":
                    st.success("Sie sind bereits als Admin registrieren und können sich einloggen.")
                else:
                    st.error("Ihr Anfrage auf Registrerirung wurde abgelehnt")
            elif not name_query or not email_query or not affiliation_query:
                st.error(admin_registration_cfg['error_form'])
            elif not validate_email(email=email_query):
                st.error(admin_registration_cfg['not_email'])
            else:
                try:
                    result_reg = send_admin_registration(to_email=admin_registration_cfg['system_admin_email'],
                                                     email=email_query,
                                                     name=name_query, affiliation=affiliation_query,
                                                     systemadmin_email=admin_registration_cfg[
                                                         'system_admin_email'])
                    result_create = create_admin(name=name_query, email= email_query, affiliation=affiliation_query)
                    if result_reg == "sent successfully" and result_create.get("detail") == "admin created":
                        st.success(admin_registration_cfg['success_registration'])
                except Exception as e:
                    st.error(str(e) + result_reg)

    st.stop()
