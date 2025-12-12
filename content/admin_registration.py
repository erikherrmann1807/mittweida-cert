import streamlit as st

from src.auth.otp_mail.email import send_admin_registration_mail
from src.database.operations import check_existing_user


def admin_registration():
    #TODO: Send Mail to admin of the app to confirm registration
    st.write("Admin Registration")
    with st.form(key="admin_registration_form"):
        name_query = st.text_input("Name")
        email_query = st.text_input("Email")
        affiliation_query = st.text_input("Affliation")
        if st.form_submit_button("Submit"):
            if check_existing_user(email=email_query, role=st.session_state.role):
                st.error("Ein Nutzer mir dieser Email existiert bereits!")
            elif name_query and email_query and affiliation_query:
                send_admin_registration_mail("admin_herrman", email=email_query,
                                             name=name_query, affiliation=affiliation_query)
                st.success("Admin Registration erfolgreich angefragt!")
            else:
                st.error("Name, Email oder Zugehörigkeit fehlen!")

    st.stop()