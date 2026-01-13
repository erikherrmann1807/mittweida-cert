import time
import streamlit as st
from babel.dates import format_date

from src.database.operations import verify_cert
from util import t

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
                cert = verify_cert(search_query)

                if st.session_state.verify_counter >= MAX_ATTEMPTS:
                    state["blocked_until"] = time.time() + COOLDOWN_SECONDS
                    st.session_state.verify_counter = 0
                    st.error(t(f"texts.{st.session_state.language}.verify_cert.attempts_error", COOLDOWN_SECONDS=COOLDOWN_SECONDS))

                if cert:
                    (
                        cert_id,
                        name,
                        email,
                        course_name,
                        platform,
                        created_at,
                        cert_number,
                        institution,
                        logo_path,
                        user_id,
                        admin_id
                    ) = cert

                    date = format_date(created_at, locale='de_DE')
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
