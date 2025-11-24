import streamlit as st

from src.database.operations import insert_csv


def admin_content():
    st.markdown(f"<h1 class='no-fade'>Admin Dashboard</h1>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("## Zertifikate hochladen")
        uploaded_file = st.file_uploader("CSV-Datei mit Zertifikatsdaten hochladen", type=["csv"],
                                         accept_multiple_files=True)
        if uploaded_file:
            insert_csv(uploaded_file)
            st.success("Datei erfolgreich hochgeladen!")
