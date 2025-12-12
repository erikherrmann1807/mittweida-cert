import streamlit as st

from src.auth.otp_mail.email import send_admin_registration_mail
from src.database.operations import create_admin


def admin_registration():
    #TODO: Send Mail to admin of the app to confirm registration
    st.write("Admin Registration")
    with st.form(key="admin_registration_form"):
        name_query = st.text_input("Name")
        email_query = st.text_input("Email")
        affiliation_query = st.text_input("Affliation")
        if st.form_submit_button("Submit"):
            if name_query and email_query and affiliation_query:
                send_admin_registration_mail("admin_herrman", email=email_query,
                                             name=name_query, affiliation=affiliation_query)
                #create_admin(name_query, email_query, affiliation_query)
                st.success("Admin Registration Successful")
            else:
                st.error("Name or Email or Affliation missing")
    st.stop()