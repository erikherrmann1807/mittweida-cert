import streamlit as st

from src.auth.otp_mail.email import send_admin_confirmation_mail
from src.database.operations import create_admin


def add_admin(config):
    st.subheader("Neuen Eintrag hinzufügen")

    with st.form(key="input_form"):
        name_query = st.text_input("Name")
        email_query = st.text_input("E-Mail")
        affiliation_query = st.text_input("Zugehörigkeit")

        submitted = st.form_submit_button("Speichern & Mail senden")

    if submitted:
        create_admin(name=name_query, email=email_query, affiliation=affiliation_query)

        send_admin_confirmation_mail(to_email=email_query)

        st.success("Admin erfolgreich hinzugefügt")
