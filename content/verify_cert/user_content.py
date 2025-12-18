import streamlit as st
from babel.dates import format_date

from src.database.operations import verify_cert
from util import t


def user_content(config):
    st.title("Mittweida Certificate Verification")
    with st.container(border=True):
        search_query = st.text_input(config['texts'][st.session_state.language]['verify_cert']['search'], key="search")
        if search_query:
            cert = verify_cert(search_query)
            if cert:
                cert_id, name, email, course_name, platform, created_at, cert_number, institution, logo_path, user_id = cert
                date = format_date(created_at, locale='de_DE')
                st.success(t(f"texts.{st.session_state.language}.verify_cert.success", search_query=search_query))
                st.markdown(t(f"texts.{st.session_state.language}.verify_cert.info", date=date, name=name,
                              course_name=course_name))

            else:
                st.error(config['texts'][st.session_state.language]['verify_cert']['error'])
