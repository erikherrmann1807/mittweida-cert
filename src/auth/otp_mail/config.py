import re
from pathlib import Path

import streamlit as st

# ==========================================
# ---------- OTP / SMTP CONFIG ----------
# ==========================================
SMTP_CFG = st.secrets.get("email_otp", {})
SMTP_HOST = SMTP_CFG.get("host")
SMTP_PORT = int(SMTP_CFG.get("port", 587))
SMTP_USER = SMTP_CFG.get("user", "")
SMTP_PASS = SMTP_CFG.get("password", "")
SMTP_FROM = SMTP_CFG.get("from", SMTP_USER)
USE_STARTTLS = bool(SMTP_CFG.get("use_starttls", True))

# ---------- OTP-Parameter ----------
CODE_LEN = 6
CODE_TTL_SECONDS = 10 * 60
MAX_ATTEMPTS = 6
RESEND_COOLDOWN = 30
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# ----------- Admin E-Mail(s) -----------
ADMIN_CFG = st.secrets.get("admin_mail", {})
ADMIN_EMAIL = ADMIN_CFG.get("admin_mail")