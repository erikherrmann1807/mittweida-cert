import streamlit as st

DATABASE_CFG = st.secrets.get("database", {})
DB = DATABASE_CFG.get("database", "mwcertlocal")
DB_USER = DATABASE_CFG.get("user", "postgres")
DB_HOST = DATABASE_CFG.get("host", "localhost")
DB_PASSWORD = DATABASE_CFG.get("password", "mwcertlocal")
DB_PORT = DATABASE_CFG.get("port", "5430")