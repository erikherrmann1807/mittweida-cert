import time

import streamlit as st
from babel.dates import format_date

from src.api.wrapper import get_certificate_by_cert_number
from util import t, parse_dt

MAX_ATTEMPTS = 5
COOLDOWN_SECONDS = 60


@st.cache_resource
def get_cooldown_state():
    return {"blocked_until": 0}


def user_content(config):
    st.title(config['texts'][st.session_state.language]['verify_cert']['title'])

    state = get_cooldown_state()
    now = time.time()
    in_cooldown = now < state["blocked_until"]

    with st.container(border=True):
        search_query = st.text_input(
            config['texts'][st.session_state.language]['verify_cert']['search'],
            key="search"
        )

        verify_clicked = st.button(config['texts'][st.session_state.language]['verify_cert']['verify_button'])

        if in_cooldown:
            remaining = int(state["blocked_until"] - now)
            st.error(t(f"texts.{st.session_state.language}.verify_cert.cooldown_error", remaining=remaining))
            return

        if verify_clicked and not in_cooldown:
            st.session_state.verify_counter += 1

            if search_query:
                # cert = verify_cert(search_query)
                cert = get_certificate_by_cert_number(search_query)

                if st.session_state.verify_counter >= MAX_ATTEMPTS:
                    state["blocked_until"] = time.time() + COOLDOWN_SECONDS
                    st.session_state.verify_counter = 0
                    st.error(t(f"texts.{st.session_state.language}.verify_cert.attempts_error",
                               COOLDOWN_SECONDS=COOLDOWN_SECONDS))

                if cert:
                    name = cert.get("name")
                    course_name = cert.get("course_name")
                    created_at = cert.get("created_at")

                    dt = parse_dt(created_at)
                    date = format_date(dt.date(), locale="de_DE") if dt else ""
                    st.success(
                        t(
                            f"texts.{st.session_state.language}.verify_cert.success",
                            search_query=search_query
                        )
                    )
                    st.markdown(
                        t(
                            f"texts.{st.session_state.language}.verify_cert.info",
                            date=date,
                            name=name,
                            course_name=course_name
                        )
                    )
                else:
                    st.error(config['texts'][st.session_state.language]['verify_cert']['error'])
