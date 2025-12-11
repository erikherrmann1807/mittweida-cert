import streamlit as st
from streamlit import container

from src.auth.otp_mail.config import ADMIN_EMAIL
from src.auth.otp_mail.login_code import request_login_code, verify_login_code
from src.database.init_database import init_database
from src.database.operations import check_existing_user
from util import get_config, get_lang_options

config = get_config()

def login_gate():
    init_database()
    #init_session_states()

    if not st.session_state.auth_email and not st.session_state.admin_authenticated:
        with st.container(border=True):
            email_req = mail_section()
            code_section(email_req)
        st.stop()

def language_section():
    with st.container(border=True):
        locale = st.radio(label='Language', options=list(get_lang_options().keys()))
        st.session_state.language = locale.lower()
        if st.button(config['texts'][st.session_state.language]['login']['language_selection']):
            st.session_state.language_set = True
            st.rerun()


def code_section(email_req: str | None):
    if st.session_state.otp:
        code_input = st.text_input(config['texts'][st.session_state.language]['login']['code'],
                                   placeholder=config['texts'][st.session_state.language]['login']['code_placeholder'])
        if st.button(config['texts'][st.session_state.language]['login']['login_button'], use_container_width=True):
            if verify_login_code(email_req, code_input):
                if email_req.strip().lower() == ADMIN_EMAIL.strip().lower():
                    st.session_state.admin_authenticated = True
                st.session_state.auth_email = email_req.strip().lower()
                st.rerun()
            else:
                st.error(config['texts'][st.session_state.language]['login']['invalid_code_and_attempts'])


def mail_section() -> str | None:
    st.subheader(config['texts'][st.session_state.language]['login']['login_header'])
    email_req = st.text_input(config['texts'][st.session_state.language]['login']['mail_input_label'],
                              placeholder=config['texts'][st.session_state.language]['login']['mail_placeholder'],
                              disabled=st.session_state.otp)
    if st.button(config['texts'][st.session_state.language]['login']['send_code_button'], use_container_width=True):
        st.session_state.user_exists = check_existing_user(email=email_req)
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
    if st.session_state.get("success_message"):
        st.success(st.session_state.success_message)
    return email_req


def init_session_states():
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

    if "otp" not in st.session_state:
        st.session_state.otp = False

    if "success_message" not in st.session_state:
        st.session_state.success = None

    if "language" not in st.session_state:
        st.session_state.language = "german"

    if "language_set" not in st.session_state:
        st.session_state.language_set = False