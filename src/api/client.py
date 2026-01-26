import requests
import streamlit as st

API_CFG = st.secrets.get("api", {})

API_BASE = API_CFG.get("base_url", "")


def _headers():
    token = st.session_state.get("access_token")
    h = {"Accept": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def get(path, params=None):
    url = f"{API_BASE}{path}"
    r = requests.get(url, params=params, headers=_headers(), timeout=30)
    r.raise_for_status()
    return r.json()


def post(path, json=None, files=None, data=None):
    url = f"{API_BASE}{path}"
    if files is not None:
        r = requests.post(url, files=files, data=data, headers=_headers(), timeout=60)
    else:
        r = requests.post(url, json=json, headers=_headers(), timeout=30)
    r.raise_for_status()
    return r.json()
