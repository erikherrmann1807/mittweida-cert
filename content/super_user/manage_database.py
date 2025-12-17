import streamlit as st
import pandas as pd



def manage_database():
    st.subheader("Zertifikate Verwalten")

    df = pd.DataFrame()

    st.dataframe(df, use_container_width=True)