import pandas as pd
import streamlit as st


def manage_database():
    st.subheader("Zertifikate Verwalten")

    df = pd.DataFrame()

    st.dataframe(df, use_container_width=True)
