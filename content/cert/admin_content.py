import os
from io import BytesIO

import numpy as np
import requests
import streamlit as st
from pandas import DataFrame

from src.api.wrapper import import_csv_api, get_certificates_for_admin_email, apply_certificate_editor_changes, \
    get_admin_id
from util import get_config, t

config = get_config()


def admin_content():
    admin_cfg = config['texts'][st.session_state.language]['admin_content']
    st.markdown(admin_cfg['header'], unsafe_allow_html=True)

    with (st.container(border=True)):
        st.markdown(admin_cfg['upload_certs'])
        uploaded_file = st.file_uploader(admin_cfg['upload_csv'], type=["csv"],
                                         accept_multiple_files=True)
        institution = st.text_input(admin_cfg['institution'], )

        st.divider()

        template_choice = st.radio(
            f"{admin_cfg['template_section']['header']}",
            admin_cfg['template_section']['radio_button'],
            index=0
        )

        uploaded_logo = None
        if template_choice == admin_cfg['template_section']['radio_button'][0]:
            uploaded_logo = st.file_uploader(admin_cfg['upload_logo'], type=["png"])

        if uploaded_logo is None:
            logo_path = os.path.join("assets/images", "logo.png")
            with open(logo_path, "rb") as f:
                uploaded_logo = BytesIO(f.read())
            uploaded_logo.name = "logo.png"


        template_file = None
        template_type = "default"
        template_path = os.path.join("data", "Cert.odt")

        with open(template_path, "rb") as f:
            template_file = BytesIO(f.read())
        template_file.name = "Cert.odt"

        if template_choice == admin_cfg['template_section']['radio_button'][1]:
            template_type = "custom"

            st.markdown(f"{admin_cfg['template_section']['instruction_custom_template_header']}")
            st.write(f"{admin_cfg['template_section']['instruction_custom_template']}")

            confirmed = st.checkbox(f"{admin_cfg['template_section']['confirm_instructions']}")
            if confirmed:
                template_file = st.file_uploader(f"{admin_cfg['template_section']['upload_hint']}", type=["odt"])
            else:
                st.warning(f"{admin_cfg['template_section']['instruction_warning']}")


        if st.button(label=admin_cfg['confirm_upload_button']):
            if template_type == "custom":
                if template_file is None:
                    st.warning(f"{admin_cfg['template_section']['confirm_upload_warning']}")
                    return

                #os.makedirs(os.path.dirname(template_abs_path), exist_ok=True)
                #with open(template_abs_path, "wb") as f:
                    #f.write(custom_template_file.getbuffer())

            if institution and uploaded_file:
                try:
                    resp = import_csv_api(
                        uploaded_file=uploaded_file,
                        institution=institution,
                        logo_file=uploaded_logo,
                        template_type=template_type,
                        template_file=template_file,
                    )
                    st.success(admin_cfg['upload_success'])
                    st.json(resp)
                except requests.HTTPError as e:
                    st.error(e.response.text)
            else:
                st.warning(admin_cfg['upload_warning'])

    st.markdown("---")
    st.subheader(f"{admin_cfg['edit_cert_data_section']['header']}")

    state_key = f"cert_df_original__{st.session_state.auth_email}"

    if state_key not in st.session_state:
        data = get_certificates_for_admin_email()
        df = DataFrame(data)
        df = df.drop(columns=["user", "admin", "logo_path"], errors="ignore")
        st.session_state[state_key] = df

    df_original = st.session_state[state_key].copy()

    if df_original.empty:
        st.info(f"{admin_cfg['edit_cert_data_section']['empty_info']}")
        return

    disabled_cols = ["id", "created_at"]
    disabled_cols = [c for c in disabled_cols if c in df_original.columns]

    edited_df = st.data_editor(
        df_original,
        key="cert_editor",
        num_rows="dynamic",
        disabled=disabled_cols,
        use_container_width=True
    )

    st.caption(
        f"{admin_cfg['edit_cert_data_section']['cert_number_hint']}")

    if st.button(f"{admin_cfg['edit_cert_data_section']['save_changes_button']}", type="primary"):
        try:
            edited_lst = edited_df.replace({np.nan: None}).to_dict(orient="records")
            original_lst = df_original.replace({np.nan: None}).to_dict(orient="records")

            reset_ids = apply_certificate_editor_changes(edited_lst, original_lst)

            data = get_certificates_for_admin_email()
            df = DataFrame(data)
            df = df.drop(columns=["user", "admin", "logo_path"], errors="ignore")
            st.session_state[state_key] = df

            if reset_ids:
                preview = ", ".join(map(str, reset_ids[:20]))
                more = " …" if len(reset_ids) > 20 else ""
                st.warning(
                    t(f"texts.{st.session_state.language}.admin_content.edit_cert_data_section.reset_cert_number_warning",
                      reset_ids=len(reset_ids), preview=preview, more=more))

            st.success(f"{admin_cfg['edit_cert_data_section']['success']}")
            st.rerun()

        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"{admin_cfg['edit_cert_data_section']['error']}")
            st.exception(e)
