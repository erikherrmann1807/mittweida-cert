import os

import streamlit as st
from PIL import Image

from src.database.operations import set_alias_email, get_data_per_user


def user_content():
    if not st.session_state.admin_authenticated:
        placeholder_column, logo_column = st.columns(2)
        try:
            hsmw_logo = Image.open(os.path.join('assets', 'images/logo.png'))
            logo_column.image(hsmw_logo, use_container_width=True)
        except Exception:
            logo_column.write("")

        st.markdown(f"<h1 class='no-fade'>Mittweida Certificate Generator</h1>", unsafe_allow_html=True)
        with st.container(border=True):
            header_column, qrcode_column = st.columns([3, 1])
            with header_column.container(vertical_alignment="distribute"):
                st.markdown(f"<h3 class='no-fade'>Zertifikatsservice der Hochschule Mittweida</h3>",
                            unsafe_allow_html=True)
                alternate_email = st.text_input("Alternative E-Mail hinterlegen", value="", key="alternative_email",
                                                help="Hier können Sie eine alternative E-Mail-Adresse hinterlegen, welche Ihnen Zugriff auf Ihre Zertifikate ermöglicht.")
                if alternate_email:
                    set_alias_email(main_email=st.session_state.auth_email, alias_email=alternate_email)
                    st.success(f"Alternative E-Mail '{alternate_email}' hinterlegt.")
            try:
                qr_image = Image.open(os.path.join('assets', 'images/qrcode.png'))
                qrcode_column.image(qr_image, caption="Hier Zertifikat verifizieren!", use_container_width=True)
            except Exception:
                qrcode_column.write("")

        with st.container(border=True):
            st.markdown(f"<h4 class='no-fade'>Meine Zertifikate</h4>", unsafe_allow_html=True)
            search_query = st.text_input("Suche", placeholder="Nach Kurs oder Thema suchen...", key="search")

            if search_query:
                st.write(f"Suchergebnisse für '{search_query}':")

            year_column, platform_column = st.columns([1, 1])
            with year_column:
                selected_year = st.selectbox("Jahr", ["Alle", "2025", "2024", "2023", "2022", "2021", "2020"])
            with platform_column:
                selected_platform = st.selectbox("Plattform", ["Alle", "Moodle", "Opal", "Andere"])

            certs_per_row = 2
            certs = get_data_per_user(st.session_state.auth_email)
            # filtered_certs = [c for c in certs if
            #                   (selected_year == "Alle" or c["year"] == selected_year) and
            #                   (selected_platform == "Alle" or c["platform"] == selected_platform) and
            #                   (search_query.lower() in c["title"].lower() if search_query else True)]
            rows = [certs[i:i + certs_per_row] for i in range(0, len(certs), certs_per_row)]
            with st.container(height=550, border=False):
                for row in rows:
                    cert_columns = st.columns(certs_per_row)
                    for idx, cert in enumerate(row):
                        with cert_columns[idx]:
                            with st.container(border=True, height=250, vertical_alignment="distribute"):
                                print(rows)
                                cert_id, name, email, course_name, created_at, user_id = cert
                                st.markdown(f"#### {course_name}")
                                st.markdown(f"**Plattform:** ")
                                st.markdown(f"**Jahr:** {created_at}")
                                if st.button("Zertifikat ansehen", key=f"download_{course_name}",
                                             use_container_width=True):
                                    st.session_state['show_cert_details'] = course_name

        if 'show_cert_details' in st.session_state:
            cert_title = st.session_state['show_cert_details']
            cert_info = next((c for c in certs if c[3] == cert_title), None)
            cert_id, name, email, course_name, created_at, user_id = cert_info
            if cert_info:
                with st.container(border=True):
                    left, right = st.columns([2, 1])
                    with left:
                        st.markdown(f"<h4>{course_name}</h4>", unsafe_allow_html=True)
                        st.markdown(f"**Plattform:** ")
                        st.markdown(f"**Jahr:** {created_at}")
                    with right:
                        st.image("https://placehold.co/200x120?text=Zertifikat", caption="Vorschau",
                                 use_container_width=True)
                        st.button("Als PDF herunterladen", key="pdf_download", use_container_width=True)