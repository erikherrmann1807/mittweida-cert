import os

import streamlit as st

from src.database.operations import insert_csv, apply_certificate_editor_changes, get_data_per_admin, get_admin_id
from util import get_config, get_logo_path

config = get_config()


def admin_content():
    admin_cfg = config['texts'][st.session_state.language]['admin_content']
    st.markdown(admin_cfg['header'], unsafe_allow_html=True)
    admin_id = get_admin_id(st.session_state.auth_email)

    template_rel_path = os.path.join("admins", f"{admin_id}", "template.odt")
    template_abs_path = os.path.abspath(template_rel_path)

    with st.container(border=True):
        st.markdown(admin_cfg['upload_certs'])
        uploaded_file = st.file_uploader(admin_cfg['upload_csv'], type=["csv"],
                                         accept_multiple_files=True)
        institution = st.text_input(admin_cfg['institution'], )

        st.divider()

        template_choice = st.radio(
            "Template auswählen",
            ["Standard-Template verwenden", "Eigenes Template hochladen"],
            index=0
        )

        uploaded_logo = None
        if template_choice == "Standard-Template verwenden":
            uploaded_logo = st.file_uploader(admin_cfg['upload_logo'], type=["png"], )

        template_type = "default"
        template_path = os.path.join("data", "Cert.odt")

        custom_template_file = None
        if template_choice == "Eigenes Template hochladen":
            template_type = "custom"

            st.markdown("**Anleitung für das Custom-Template**")
            st.write(
                "- Dokument gemäß Vorgaben vorbereiten\n"
                "- Platzhalter korrekt setzen\n"
                "- Format: LibreOffice (.odt)\n"
            )

            confirmed = st.checkbox("Ich habe die Anleitung gelesen und verstanden.")
            if confirmed:
                custom_template_file = st.file_uploader("Custom Template (odt) hochladen", type=["odt"])
            else:
                st.warning("Bitte bestätige zuerst die Anleitung, um den Upload freizuschalten.")

            template_path = template_rel_path

        if st.button(label=admin_cfg['confirm_upload_button']):
            if template_type == "custom":
                if custom_template_file is None:
                    st.warning("Bitte lade ein Custom Template hoch (DOCX), bevor du bestätigst.")
                    return

                os.makedirs(os.path.dirname(template_abs_path), exist_ok=True)
                with open(template_abs_path, "wb") as f:
                    f.write(custom_template_file.getbuffer())

            logo_path = None
            if uploaded_logo is not None:
                file_name = uploaded_logo.name
                logo_path = os.path.join(get_logo_path(), file_name)
                with open(logo_path, "wb") as file:
                    file.write(uploaded_logo.getbuffer())
            if institution and uploaded_file:
                insert_csv(uploaded_file, institution, logo_path, st.session_state.auth_email, template_type, template_path)
                st.success(admin_cfg['upload_success'])
            else:
                st.warning(admin_cfg['upload_warning'])


    st.markdown("---")
    st.subheader("Zertifikate bearbeiten")

    state_key = f"cert_df_original__{st.session_state.auth_email}"

    if state_key not in st.session_state:
        df = get_data_per_admin(st.session_state.auth_email, as_df=True)
        df = df.drop(columns=["user_id", "admin_id", "logo_path"], errors="ignore")
        st.session_state[state_key] = df

    df_original = st.session_state[state_key].copy()

    if df_original.empty:
        st.info("Noch keine Zertifikate vorhanden (oder keine für diesen Admin gefunden).")
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
        "Hinweis: cert_number von bestehenden Zertifikaten wird beim Speichern automatisch zurückgesetzt.")

    if st.button("Änderungen speichern", type="primary"):
        try:
            reset_ids = apply_certificate_editor_changes(
                admin_mail=st.session_state.auth_email,
                edited_df=edited_df,
                original_df=df_original
            )

            df = get_data_per_admin(st.session_state.auth_email, as_df=True)
            df = df.drop(columns=["user_id", "admin_id"], errors="ignore")
            st.session_state[state_key] = df

            if reset_ids:
                preview = ", ".join(map(str, reset_ids[:20]))
                more = " …" if len(reset_ids) > 20 else ""
                st.warning(
                    f"cert_number wurde bei {len(reset_ids)} bestehenden Zertifikaten zurückgesetzt (IDs: {preview}{more}).")

            st.success("Gespeichert.")
            st.rerun()

        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error("Beim Speichern ist ein unerwarteter Fehler aufgetreten.")
            st.exception(e)
