import os
from typing import Any

import streamlit as st
from PIL import Image
from babel.dates import format_date

from src.database.operations import set_alias_email, get_data_per_user
from src.generate_pdf import convert_odt_to_pdf


def user_content():
    header()
    verify_and_alias()

    with st.container(border=True):
        search_query, selected_platform, selected_year = cert_filter_options()

        certs_per_row, rows = filter_logic(search_query, selected_platform, selected_year)
        display_certs(certs_per_row, rows)


def display_certs(certs_per_row: int, rows: list[list[tuple[Any, ...]]]):
    with st.container(height=625, border=False):
        for row in rows:
            cert_columns = st.columns(certs_per_row)
            for idx, cert in enumerate(row):
                with cert_columns[idx]:
                    with st.container(border=True, height=300, vertical_alignment="distribute"):
                        cert_id, name, email, course_name, platform, created_at, cert_number, user_id = cert
                        date = format_date(created_at, locale='de_DE')
                        st.markdown(f"#### {course_name}")
                        st.markdown(f"**Name: {name}**")
                        st.markdown(f"**Plattform: {platform}**")
                        st.markdown(f"**Datum:** {date}")
                        if st.button("Zertifikat generieren", key=f"download_{course_name}",
                                     use_container_width=True):
                            download_dialog(name=name, email=email, course_name=course_name,
                                            platform=platform, created_at=date, cert_number=cert_number)


def filter_logic(search_query: Any | None, selected_platform: Any | None, selected_year: str | None):
    certs_per_row = 2
    certs = get_data_per_user(st.session_state.auth_email)
    filtered_certs = [c for c in certs if
                      (selected_year == "Alle" or selected_year in c[5].isoformat()) and
                      (selected_platform == "Alle" or c[4] == selected_platform) and
                      (search_query.lower() in c[3].lower() if search_query else True)]
    rows = [filtered_certs[i:i + certs_per_row] for i in range(0, len(filtered_certs), certs_per_row)]
    return certs_per_row, rows


def cert_filter_options() -> tuple[Any | None, Any | None, str | None]:
    st.markdown(f"<h4 class='no-fade'>Meine Zertifikate</h4>", unsafe_allow_html=True)
    search_query = st.text_input("Suche", placeholder="Nach Kurs oder Thema suchen...", key="search")

    if search_query:
        st.write(f"Suchergebnisse für '{search_query}':")

    year_column, platform_column = st.columns([1, 1])
    with year_column:
        selected_year = st.selectbox("Jahr", ["Alle", "2025", "2024", "2023", "2022", "2021", "2020"])
    with platform_column:
        selected_platform = st.selectbox("Plattform", ["Alle", "Moodle", "Opal", "In Präsenz", "Andere"])
    return search_query, selected_platform, selected_year


def verify_and_alias():
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
        except FileNotFoundError:
            qrcode_column.write("")


def header():
    placeholder_column, logo_column = st.columns(2)
    try:
        logo = Image.open(os.path.join('assets', 'images/logo.png'))
        logo_column.image(logo, use_container_width=True)
    except FileNotFoundError:
        logo_column.write("")

    st.markdown(f"<h1 class='no-fade'>Mittweida Certificate Generator</h1>", unsafe_allow_html=True)


@st.dialog("Zertifikat herunterladen")
def download_dialog(name: str, email: str, course_name: str, platform: str, created_at: str,
                    cert_number: str):
    with st.spinner('Generating ...'):
        placeholder = {
            "{{name}}": name,
            "{{email}}": email,
            "{{course_name}}": course_name,
            "{{platform}}": platform,
            "{{created_at}}": created_at,
            "{{cert_number}}": cert_number,
        }

        template_file = "data/Cert.odt"

        pdf = convert_odt_to_pdf(
            template_path=template_file,
            placeholders=placeholder
        )
        st.write(f"Sie können Ihr Zertifikat für '{course_name}' nun herunterladen.")
        if st.download_button("PDF herunterladen", data=pdf,file_name=f"Zertifikat-{name}-{course_name}.pdf", mime="application/pdf"):
            st.rerun()
