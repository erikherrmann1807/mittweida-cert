import time

import streamlit as st

from src.api.wrapper import request_otp, verify_otp
from src.auth.otp_mail.email import send_mail_code
from util import get_config, get_lang_options, Role, validate_email

config = get_config()


def login_gate():
    if not st.session_state.auth_email and not st.session_state.admin_authenticated:
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


def role_selection():
    role_selection_cfg = config['texts'][st.session_state.language]['role_selection']

    @st.dialog(" ", dismissible=False)
    def role_dialog():
        role_columns = st.columns(3)
        with role_columns[0]:
            with st.container(border=True):
                st.image(image="assets/images/dummy_image.png")
                if st.button(label=role_selection_cfg['user_login'], key="user_login"):
                    st.session_state.role = Role.User
                    st.rerun()
        with role_columns[1]:
            with st.container(border=True):
                st.image(image="assets/images/dummy_image.png")
                if st.button(label=role_selection_cfg['admin_login'], key="admin_login"):
                    st.session_state.role = Role.Admin
                    st.rerun()
        with role_columns[2]:
            with st.container(border=True):
                st.image(image="assets/images/dummy_image.png")
                if st.button(label=role_selection_cfg['admin_registration'], key="register_admin"):
                    st.session_state.role = Role.Registration
                    st.rerun()

        st.stop()

    role_dialog()


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

                print(st.session_state.role)

                st.session_state.access_token = resp["access_token"]
                st.session_state.auth_email = email

                if st.session_state.role == Role.Admin.name:
                    st.session_state.admin_authenticated = True
                elif st.session_state.role == Role.User.name:
                    st.session_state.user_authenticated = True

                print(st.session_state.admin_authenticated)

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
            st.session_state.success_message = "Code wurde gesendet."
            st.session_state.otp = True
            send_mail_code(email, result.get("otp"))

        elif result["status"] == 429:
            remaining = int(result.get("retry_after", 60))
            st.warning(f"Bitte warten: {remaining}s (Code wurde bereits gesendet)")

        else:
            st.error("Unerwartete Antwort vom Server.")

    if st.session_state.otp:
        st.success(st.session_state.success_message)

    return email_req
