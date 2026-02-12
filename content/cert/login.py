import time

import streamlit as st

from src.api.wrapper import request_otp, verify_otp
from util import get_config, get_lang_options, Role, validate_email

config = get_config()


def login_gate():
    if not st.session_state.auth_email:
        with st.container(border=True):
            email_req = mail_section()
            code_section(email_req)
        st.stop()


def language_section():
    @st.dialog(" ", dismissible=False)
    def language_dialog():
        locale = st.radio(label_visibility="hidden", label="Language", options=list(get_lang_options().keys()))
        st.session_state.language = locale.lower()
        if st.button(config['texts'][st.session_state.language]['login']['language_selection']):
            st.session_state.language_set = True
            st.rerun()

    language_dialog()


def code_section(email_req: str | None):
    if st.session_state.otp:
        code_input = st.text_input(
            config['texts'][st.session_state.language]['login']['code'],
            placeholder=config['texts'][st.session_state.language]['login']['code_placeholder']
        )

        if st.button(config['texts'][st.session_state.language]['login']['login_button'], use_container_width=True):
            try:
                email = (st.session_state.login_mail or email_req or "").strip().lower()
                if not email:
                    st.error("E-Mail fehlt.")
                    return

                resp = verify_otp(email=email, role=st.session_state.role, otp=code_input)

                st.session_state.access_token = resp["access_token"]
                st.session_state.auth_email = email

                if st.session_state.role == Role.Admin.name:
                    st.session_state.admin_authenticated = True
                elif st.session_state.role == Role.User.name:
                    st.session_state.user_authenticated = True

                st.rerun()

            except Exception as e:
                st.error(config['texts'][st.session_state.language]['login']['invalid_code_and_attempts'] + str(e))


def mail_section() -> str | None:
    cfg = config['texts'][st.session_state.language]['login']

    st.subheader(cfg['login_header'])
    email_req = st.text_input(
        cfg['mail_input_label'],
        placeholder=cfg['mail_placeholder'],
        disabled=st.session_state.otp,
    )

    now = time.time()
    remaining = int(st.session_state.otp_next_allowed_at - now)
    if remaining < 0:
        remaining = 0

    btn_label = cfg['send_code_button']
    if remaining > 0:
        btn_label = f"{cfg['send_code_button']} ({remaining}s)"

    if st.button(btn_label, use_container_width=True):
        if not validate_email(email_req):
            st.error(cfg['invalid_mail'])
            return None

        email = email_req.strip().lower()
        result = request_otp(email=email, role=st.session_state.role)

        if result["status"] == 200 and result.get("sent"):
            st.session_state.login_mail = email
            st.session_state.success_message = "Code wurde gesendet und ist für 10min gültig."
            st.session_state.otp = True

        elif result["status"] == 429:
            remaining = int(result.get("retry_after", 60))
            st.warning(f"Bitte warten: {remaining}s (Code wurde bereits gesendet)")

        else:
            st.error("Unerwartete Antwort vom Server.")

    if st.session_state.otp:
        st.success(st.session_state.success_message)

    return email_req
