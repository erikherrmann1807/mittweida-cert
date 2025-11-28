import streamlit as st

from src.auth.otp_mail.config import ADMIN_EMAIL
from src.auth.otp_mail.login_code import request_login_code, verify_login_code
from src.database.init_database import init_database
from src.database.operations import check_existing_user


def login_gate():
    init_database()
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    if "auth_email" not in st.session_state:
        st.session_state.auth_email = None

    if "user_exists" not in st.session_state:
        st.session_state.user_exists = False

    if "login_mail" not in st.session_state:
        st.session_state.login_mail = None

    if "login_hash_code" not in st.session_state:
        st.session_state.login_hash_code = None

    if "code_created_at" not in st.session_state:
        st.session_state.code_created_at = None

    if "code_expired_at" not in st.session_state:
        st.session_state.code_expired_at = None

    if "login_attempts" not in st.session_state:
        st.session_state.login_attempts = 0

    if "code_last_sent_at" not in st.session_state:
        st.session_state.code_last_sent_at = None

    if not st.session_state.auth_email and not st.session_state.admin_authenticated:
        with st.container(border=True):
            st.subheader("🔐 Anmeldung")
            email_req = st.text_input("E-Mail", placeholder="john@example.de")
            if st.button("Code senden", use_container_width=True):
                st.session_state.user_exists = check_existing_user(email=email_req)
                if st.session_state.user_exists:
                    try:
                        st.session_state.login_mail = email_req.strip().lower()
                        msg = request_login_code(email_req)
                        st.success(msg)
                    except Exception as e:
                        st.error(f"Versand fehlgeschlagen: {e}")
                else:
                    st.error("Kein Nutzer mit dieser Email gefunden.")
            code_input = st.text_input("Anmeldecode", placeholder="6-stelliger Code")
            if st.button("Anmelden", use_container_width=True):
                if verify_login_code(email_req, code_input):
                    if email_req.strip().lower() == ADMIN_EMAIL.strip().lower():
                        st.session_state.admin_authenticated = True
                    st.session_state.auth_email = email_req.strip().lower()
                    st.success("Erfolgreich angemeldet!")
                    st.rerun()
                else:
                    st.error("Ungültiger Code oder zu viele Fehlversuche.")

        st.stop()