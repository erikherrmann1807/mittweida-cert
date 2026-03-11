import hashlib
import json
import os
import re
import ssl
from datetime import datetime
from enum import Enum
from pathlib import Path

import streamlit as st

from src.api.wrapper import logout_api


def get_placeholders(name: str, email: str, course_name: str, platform: str, created_at: str, cert_number: str,
                     institution: str) -> dict:
    placeholders = {
        "{{name}}": name,
        "{{email}}": email,
        "{{course_name}}": course_name,
        "{{platform}}": platform,
        "{{created_at}}": created_at,
        "{{cert_number}}": cert_number,
        "{{institution}}": institution,
    }
    return placeholders


def get_config():
    with open(os.path.join('.streamlit/', 'config.json'), 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)
    return config


def get_dummy_image_path():
    return "Pictures/100000010000011B0000008ECF685CA0.png"


def get_logo_path():
    return "logos"


def get_lang_options():
    lang_options = {
        "German": "de_DE",
        "English": "en_US",
    }
    return lang_options


strings_path = Path(".streamlit/config.json")
STRINGS = json.loads(strings_path.read_text(encoding="utf-8"))


def get_from_path(data: dict, path: str | list[str]):
    if isinstance(path, str):
        parts = path.split(".")
    else:
        parts = path

    node = data
    for part in parts:
        node = node[part]
    return node


def t(path: str | list[str], **kwargs) -> str:
    try:
        template = get_from_path(STRINGS, path)
    except KeyError:
        return f"[missing:{path}]"

    if not isinstance(template, str):
        return f"[not a string:{path}]"

    try:
        return template.format(**kwargs)
    except KeyError as e:
        missing = e.args[0]
        return f"[missing placeholder '{missing}' in '{path}']"


Role = Enum('Role', ['User', 'Admin', 'Registration'])


def init_session_states():
    st.session_state.setdefault("admin_authenticated", False)
    st.session_state.setdefault("user_authenticated", False)
    st.session_state.setdefault("auth_email", None)
    st.session_state.setdefault("user_exists", False)
    st.session_state.setdefault("login_mail", None)
    st.session_state.setdefault("login_hash_code", None)
    st.session_state.setdefault("code_created_at", None)
    st.session_state.setdefault("code_expired_at", None)
    st.session_state.setdefault("login_attempts", 0)
    st.session_state.setdefault("code_last_sent_at", None)
    st.session_state.setdefault("otp", False)
    st.session_state.setdefault("language", "german")
    st.session_state.setdefault("language_set", False)
    st.session_state.setdefault("role", None)
    st.session_state.setdefault("selected_page_prev", None)
    st.session_state.setdefault("verify_counter", 0)
    st.session_state.setdefault("access_token", None)
    st.session_state.setdefault("otp_next_allowed_at", 0.0)
    st.session_state.setdefault("otp_last_error", "")


def validate_email(email: str) -> bool:
    pattern = r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$"
    return re.match(pattern, email) is not None


def get_mail_context():
    context = ssl.create_default_context()
    return context


def reset_login():
    try:
        if st.session_state.get("access_token"):
            logout_api()
    except Exception:
        pass

    st.session_state.access_token = None
    st.session_state.auth_email = None
    st.session_state.user_authenticated = False
    st.session_state.admin_authenticated = False
    st.session_state.otp = False
    st.session_state.login_mail = None


def parse_dt(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    s = str(value).strip()
    if s.endswith("Z"):
        s = s.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None
