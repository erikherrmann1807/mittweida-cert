import streamlit as st

from src.api.wrapper import create_admin
from src.auth.otp_mail.email import send_admin_confirmation_mail


def add_admin(config):
    st.subheader("Neuen Eintrag hinzufügen")

    with st.form(key="input_form"):
        name_query = st.text_input("Name")
        email_query = st.text_input("E-Mail")
        affiliation_query = st.text_input("Zugehörigkeit")

        submitted = st.form_submit_button("Speichern & Mail senden")

    if submitted:
        try:
            resp = create_admin(name_query, email_query, affiliation_query)
            st.success(f"Admin erstellt: ID={resp['id']}, Email={resp['email']}")
            send_admin_confirmation_mail(to_email=email_query)
        except Exception as e:
            st.error(f"Fehler: {e}")