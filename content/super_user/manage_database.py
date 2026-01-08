import pandas as pd
import streamlit as st

from src.database.operations import get_data, apply_certificate_editor_changes


def manage_database():
    st.subheader("Zertifikate verwalten")

    state_key = f"cert_df_original__{st.session_state.auth_email}"

    if state_key not in st.session_state:
        df = get_data( as_df=True)
        df = df.drop(columns=["user_id", "admin_id", "logo_path"], errors="ignore")
        st.session_state[state_key] = df

    df_original = st.session_state[state_key].copy()

    if df_original.empty:
        st.info("Noch keine Zertifikate vorhanden")
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
                edited_df=edited_df,
                original_df=df_original
            )

            df = get_data(as_df=True)
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
