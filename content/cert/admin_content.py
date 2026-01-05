import os

import streamlit as st

from src.database.operations import insert_csv, apply_certificate_editor_changes, get_data_per_admin
from util import get_config, get_logo_path

config = get_config()


def admin_content():
    admin_cfg = config['texts'][st.session_state.language]['admin_content']
    st.markdown(admin_cfg['header'], unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(admin_cfg['upload_certs'])
        uploaded_file = st.file_uploader(admin_cfg['upload_csv'], type=["csv"],
                                         accept_multiple_files=True)
        uploaded_logo = st.file_uploader(admin_cfg['upload_logo'], type=["png"], )
        institution = st.text_input(admin_cfg['institution'], )

        if st.button(label=admin_cfg['confirm_upload_button']):
            file_name = uploaded_logo.name
            logo_path = os.path.join(get_logo_path(), file_name)
            with open(logo_path, "wb") as file:
                file.write(uploaded_logo.getbuffer())
            if institution and uploaded_file:
                insert_csv(uploaded_file, institution, logo_path, st.session_state.auth_email)
                st.success(admin_cfg['upload_success'])
            else:
                st.warning(admin_cfg['upload_warning'])

    st.markdown("---")
    st.subheader("Zertifikate bearbeiten")

    state_key = f"cert_df_original__{st.session_state.auth_email}"

    if state_key not in st.session_state:
        df = get_data_per_admin(st.session_state.auth_email, as_df=True)
        df = df.drop(columns=["user_id", "admin_id"], errors="ignore")
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
