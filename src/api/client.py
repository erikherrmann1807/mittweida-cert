import requests
import streamlit as st

API_CFG = st.secrets.get("api", {})

API_BASE = API_CFG.get("base_url", "")


def post(path, json=None, files=None, data=None):
    url = f"{API_BASE}{path}"
    if files is not None:
        r = requests.post(url, files=files, data=data, timeout=60)
    else:
        r = requests.post(url, json=json, timeout=30)
    r.raise_for_status()
    return r.json()


def get(path, params=None):
    r = requests.get(f"{API_BASE}{path}", params=params, timeout=30)
    r.raise_for_status()
    return r.json()
