import streamlit as st

from src.auth.otp_mail.login_code import request_login_code, verify_login_code
from src.database.operations import check_existing_user
from util import get_config, get_lang_options, Role, validate_email

config = get_config()


def login_gate(role: str):
    if not st.session_state.auth_email and not st.session_state.admin_authenticated:
        with st.container(border=True):
            email_req = mail_section(role=role)
            code_section(email_req)
        st.stop()


def language_section():
    @st.dialog(" ", dismissible=False)
    def language_dialog():
        locale = st.radio(label_visibility="hidden", label="", options=list(get_lang_options().keys()))
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
        code_input = st.text_input(config['texts'][st.session_state.language]['login']['code'],
                                   placeholder=config['texts'][st.session_state.language]['login']['code_placeholder'])
        if st.button(config['texts'][st.session_state.language]['login']['login_button'], use_container_width=True):
            if verify_login_code(email_req, code_input):
                if st.session_state.role == Role.Admin:
                    st.session_state.admin_authenticated = True
                elif st.session_state.role == Role.User:
                    st.session_state.user_authenticated = True
                st.session_state.auth_email = email_req.strip().lower()
                st.rerun()
            else:
                st.error(config['texts'][st.session_state.language]['login']['invalid_code_and_attempts'])


def mail_section(role: str) -> str | None:
    st.subheader(config['texts'][st.session_state.language]['login']['login_header'])
    email_req = st.text_input(config['texts'][st.session_state.language]['login']['mail_input_label'],
                              placeholder=config['texts'][st.session_state.language]['login']['mail_placeholder'],
                              disabled=st.session_state.otp)

    if st.button(config['texts'][st.session_state.language]['login']['send_code_button'], use_container_width=True):
        if not validate_email(email_req):
            st.error(config['texts'][st.session_state.language]['login']['invalid_mail'])
            return None
        st.session_state.user_exists = check_existing_user(email=email_req, role=role)
        if st.session_state.user_exists:
            try:
                st.session_state.login_mail = email_req.strip().lower()
                st.session_state.success_message = request_login_code(email_req)
                st.session_state.otp = True
            except Exception as e:
                st.error(config['texts'][st.session_state.language]['login']['send_code_failure'] + e)
            st.rerun()
        else:
            st.error(config['texts'][st.session_state.language]['login']['user_not_existing'])
    if st.session_state.otp:
        st.success(st.session_state.success_message)
    return email_req
