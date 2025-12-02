import streamlit as st
from babel.dates import format_date

from src.database.operations import verify_cert

st.set_page_config(page_title="Mittweida Certificate Generator", page_icon="🎓")

st.title("Mittweida Certificate Verification")

with st.container(border=True):
    search_query = st.text_input("Zertifikatsnummer eingeben", key="search")
    if search_query:
        cert = verify_cert(search_query)
        if cert:
            cert_id, name, email, course_name, platform, created_at, cert_number, institution, user_id = cert
            date = format_date(created_at, locale='de_DE')
            st.success(f"Zertifikat {search_query} existiert!")
            st.markdown(f"Es wurde am {date} ausgestellt für {name}. Im Rahmen des Kurses '{course_name}'.")

        else:
            st.error("Kein Zertifikat gefunden! Bitte Zertifikatsnummer korrigieren oder beim Support melden.")