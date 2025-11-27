import hmac
import time
import streamlit as st

from src.auth.otp_mail.config import RESEND_COOLDOWN, EMAIL_RE, CODE_LEN, CODE_TTL_SECONDS, MAX_ATTEMPTS
from src.auth.otp_mail.email import send_mail_code
from util import random_numeric_code, hash_code


def request_login_code(email: str) -> str:
    email = email.strip().lower()
    if not EMAIL_RE.match(email):
        return "Ungültige E-Mail-Adresse."
    now = int(time.time())

    if st.session_state.code_last_sent_at is not None and now - st.session_state.code_last_sent_at < RESEND_COOLDOWN:
        return "Bitte warte kurz, bevor du einen neuen Code anforderst."

    code = random_numeric_code(CODE_LEN)
    code_hash = hash_code(email, code)
    send_mail_code(email, code)
    st.session_state.login_mail = email
    st.session_state.login_hash_code = code_hash
    st.session_state.code_created_at = now
    st.session_state.code_expired_at = now + CODE_TTL_SECONDS
    st.session_state.code_last_sent_at = now
    return f"Code an {email} gesendet (gültig {CODE_TTL_SECONDS // 60} Min)."


def verify_login_code(email: str, code: str) -> bool:
    email = email.strip().lower()

    if not st.session_state.login_mail or not st.session_state.login_hash_code:
        return False
    now = int(time.time())

    if now > st.session_state.code_expired_at:
        st.session_state.login_mail = None
        st.session_state.login_hash_code = None
        st.session_state.code_created_at = None
        st.session_state.code_expired_at = None
        st.session_state.login_attempts = 0
        st.session_state.code_last_sent_at = None
        return False

    if st.session_state.login_attempts >= MAX_ATTEMPTS:
        return False

    ok = hmac.compare_digest(st.session_state.login_hash_code, hash_code(email, code.strip()))
    if ok:
        st.session_state.login_mail = None
        st.session_state.login_hash_code = None
        st.session_state.code_created_at = None
        st.session_state.code_expired_at = None
        st.session_state.login_attempts = 0
        st.session_state.code_last_sent_at = None
        return True

    st.session_state.login_attempts += 1
    return False