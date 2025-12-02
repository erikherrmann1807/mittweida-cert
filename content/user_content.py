import os
from typing import Any

import streamlit as st
from PIL import Image
from babel.dates import format_date

from src.database.operations import set_alias_email, get_data_per_user
from src.generate_pdf import convert_odt_to_pdf
from util import get_config

config = get_config()


def user_content():
    header()
    verify_and_alias()

    with st.container(border=True):
        search_query, selected_platform, selected_year = cert_filter_options()

        certs_per_row, rows = filter_logic(search_query, selected_platform, selected_year)
        display_certs(certs_per_row, rows)


def display_certs(certs_per_row: int, rows: list[list[tuple[Any, ...]]]):
    cert_cfg = config['texts']['user_content']['cert_infos']
    with st.container(height=670, border=False):
        for row in rows:
            cert_columns = st.columns(certs_per_row)
            for idx, cert in enumerate(row):
                with cert_columns[idx]:
                    with st.container(border=True, height=320, vertical_alignment="distribute"):
                        cert_id, name, email, course_name, platform, created_at, cert_number, institution,user_id, logo = cert
                        date = format_date(created_at, locale='de_DE')
                        st.markdown(f"#### {course_name}")
                        st.markdown(f"{cert_cfg['name']} {name}")
                        st.markdown(f"{cert_cfg['platform']} {platform}")
                        st.markdown(f"{cert_cfg['date']} {date}")
                        st.markdown(f"{cert_cfg['institution']} {institution}")
                        if st.button(cert_cfg['generate_button'], key=f"download_{course_name}",
                                     use_container_width=True):
                            download_dialog(name=name, email=email, course_name=course_name,
                                            platform=platform, created_at=date, cert_number=cert_number,
                                            institution=institution)


def filter_logic(search_query: Any | None, selected_platform: Any | None, selected_year: str | None):
    filter_cfg = config['texts']['user_content']['filter_options']
    certs_per_row = 2
    certs = get_data_per_user(st.session_state.auth_email)
    filtered_certs = [c for c in certs if
                      (selected_year == filter_cfg['filter_dropdowns_all'] or selected_year in c[5].isoformat()) and
                      (selected_platform == filter_cfg['filter_dropdowns_all'] or c[4] == selected_platform) and
                      (search_query.lower() in c[3].lower() if search_query else True)]
    rows = [filtered_certs[i:i + certs_per_row] for i in range(0, len(filtered_certs), certs_per_row)]
    return certs_per_row, rows


def cert_filter_options() -> tuple[Any | None, Any | None, str | None]:
    filter_cfg = config['texts']['user_content']['filter_options']
    st.markdown(filter_cfg['filter_caption'], unsafe_allow_html=True)
    search_query = st.text_input(filter_cfg['filter_search'],
                                 placeholder=config['texts']['user_content']['filter_options']['filter_placeholder'],
                                 key="search")

    if search_query:
        st.write(f"Suchergebnisse für '{search_query}':")

    year_column, platform_column = st.columns([1, 1])
    with year_column:
        selected_year = st.selectbox(filter_cfg['year_dropdown_label'],
        filter_cfg['year_dropdown_values'])
    with platform_column:
        selected_platform = st.selectbox(filter_cfg['platform_dropdown_label'], filter_cfg['platform_dropdown_values'])
    return search_query, selected_platform, selected_year


def verify_and_alias():
    with st.container(border=True):
        header_column, qrcode_column = st.columns([3, 1])
        with header_column.container(vertical_alignment="distribute"):
            st.markdown(config['texts']['user_content']['verify_alias_header'],
                        unsafe_allow_html=True)
            alternate_email = st.text_input(config['texts']['user_content']['alternative_mail']['label'], value="", key="alternative_email",
                                            help=config['texts']['user_content']['alternative_mail']['help'])
            if alternate_email:
                set_alias_email(main_email=st.session_state.auth_email, alias_email=alternate_email)
                st.success(f"Alternative E-Mail '{alternate_email}' hinterlegt.")
        try:
            qr_image = Image.open(os.path.join('assets', 'images/qrcode.png'))
            qrcode_column.image(qr_image, caption=config['texts']['user_content']['qrcode_caption'], width='stretch')
        except FileNotFoundError:
            qrcode_column.write("")


def header():
    placeholder_column, logo_column = st.columns(2)
    try:
        logo = Image.open(os.path.join('assets', 'images/logo.png'))
        logo_column.image(logo, width='stretch')
    except FileNotFoundError:
        logo_column.write("")

    st.markdown(config['texts']['user_content']['header'], unsafe_allow_html=True)


@st.dialog(config['texts']['user_content']['download_cert']['dialog_header'])
def download_dialog(name: str, email: str, course_name: str, platform: str, created_at: str,
                    cert_number: str, institution: str, logo):
    download_cfg = config['texts']['user_content']['download_cert']
    with st.spinner(download_cfg['generating_cert']):
        placeholder = {
            "{{name}}": name,
            "{{email}}": email,
            "{{course_name}}": course_name,
            "{{platform}}": platform,
            "{{created_at}}": created_at,
            "{{cert_number}}": cert_number,
            "{{institution}}": institution
        }

        template_file = "data/Cert.odt"

        pdf = convert_odt_to_pdf(
            template_path=template_file,
            placeholders=placeholder
        )
        st.write(download_cfg['generating_success'])
        if st.download_button(download_cfg['download_button'], data=pdf,file_name=f"Zertifikat-{name}-{course_name}.pdf", mime="application/pdf"):
            st.rerun()
