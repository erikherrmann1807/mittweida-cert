import hashlib
import hmac
import os
import re
import secrets
import smtplib
import sqlite3
import ssl
import string
import time

import pandas as pd
import psycopg2
from email.message import EmailMessage
from pathlib import Path
from typing import Optional

import streamlit as st
from PIL import Image

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
DB_PATH = Path("otp.db")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# ----------- Admin E-Mail(s) -----------
ADMIN_CFG = st.secrets.get("admin_mail", {})
ADMIN_EMAIL = ADMIN_CFG.get("admin_mail")

# ==========================================
# ---------- Database CONFIG ----------
# ==========================================
DATABASE_CFG = st.secrets.get("database", {})
DB = DATABASE_CFG.get("database", "mwcertlocal")
DB_USER = DATABASE_CFG.get("user", "postgres")
DB_HOST = DATABASE_CFG.get("host", "localhost")
DB_PASSWORD = DATABASE_CFG.get("password", "mwcertlocal")
DB_PORT = DATABASE_CFG.get("port", "5430")


# ==========================================
# ---------- DB-Layer (PostgresSQL) ----------
# ==========================================

# ---------- Debug Methods ----------
def show_data():
    with postgres() as con:
        with con.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE main_email = 'erik@example.de'")
            row = cur.fetchone()
            print("User Id:")
            for user in row:
                print(user)

            user_id = row[0]
            cur.execute("SELECT * FROM certificates WHERE user_id = %s", (user_id,))
            certificates = cur.fetchall()
            print("\nCertificates:")
            for cert in certificates:
                print(cert)


def delete_data():
    with postgres() as con:
        with con.cursor() as cur:
            cur.execute("DELETE FROM certificates")
            cur.execute("DELETE FROM users")

        con.commit()


def postgres():
    return psycopg2.connect(database=DB,
                            user=DB_USER,
                            host=DB_HOST,
                            password=DB_PASSWORD,
                            port=DB_PORT)


def get_or_create_user_id(cur, main_email, alias_email):
    cur.execute(
        "SELECT id FROM users WHERE main_email = %s",
        (main_email,)
    )
    row = cur.fetchone()

    if row:
        return row[0]

    cur.execute(
        """
        INSERT INTO users (main_email, alias_email, created_at)
        VALUES (%s, %s, NOW())
        RETURNING id;
        """,
        (main_email, alias_email)
    )
    return cur.fetchone()[0]


def insert_csv(path_to_csv):
    with postgres() as con:
        with con.cursor() as cur:
            df = pd.read_csv(path_to_csv[0], delimiter=',')
            for _, row in df.iterrows():
                name = row['name']
                email = row['email']
                course_name = row['course_name']
                user_id = get_or_create_user_id(cur, email, None)

                cur.execute(
                    """
                    INSERT INTO certificates (name, email, course_name, created_at, user_id) 
                    VALUES (%s, %s, %s, NOW(), %s)
                    """,
                    (name, email, course_name, user_id)
                )


# ==========================================
# ---------- DB-Layer (SQLite) ----------
# ==========================================
def sqlitedb():
    return sqlite3.connect(DB_PATH)


def init_sqlitedb():
    with sqlitedb() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS email_otps (
            email TEXT PRIMARY KEY,
            code_hash TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            expires_at INTEGER NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 0,
            last_sent_at INTEGER NOT NULL
        )
        """)
        con.commit()


def save_otp(email: str, code_hash: str, now_ts: int, exp_ts: int):
    with sqlitedb() as con:
        con.execute("""
        INSERT INTO email_otps(email, code_hash, created_at, expires_at, attempts, last_sent_at)
        VALUES (?, ?, ?, ?, 0, ?)
        ON CONFLICT(email) DO UPDATE SET
            code_hash=excluded.code_hash,
            created_at=excluded.created_at,
            expires_at=excluded.expires_at,
            attempts=0,
            last_sent_at=excluded.last_sent_at
        """, (email, code_hash, now_ts, exp_ts, now_ts))
        con.commit()


def load_otp(email: str) -> Optional[dict]:
    with sqlitedb() as con:
        cur = con.execute(
            "SELECT code_hash, created_at, expires_at, attempts, last_sent_at FROM email_otps WHERE email = ?",
            (email,))
        row = cur.fetchone()
        if not row:
            return None
        return dict(code_hash=row[0], created_at=row[1], expires_at=row[2], attempts=row[3], last_sent_at=row[4])


def inc_attempt(email: str):
    with sqlitedb() as con:
        con.execute("UPDATE email_otps SET attempts = attempts + 1 WHERE email = ?", (email,))
        con.commit()


def delete_otp(email: str):
    with sqlitedb() as con:
        con.execute("DELETE FROM email_otps WHERE email = ?", (email,))
        con.commit()


# ==========================================
# ---------- OTP / Mail ----------
# ==========================================
def random_numeric_code(n=CODE_LEN) -> str:
    return "".join(secrets.choice(string.digits) for _ in range(n))


def hash_code(email: str, code: str) -> str:
    return hashlib.sha256((email + ":" + code).encode("utf-8")).hexdigest()


def build_message(to_email: str, code: str) -> EmailMessage:
    plain = (
        f"Hier ist dein Einmal-Code: {code}\n\n"
        f"Er ist {CODE_TTL_SECONDS // 60} Minuten gültig. "
        "Wenn du das nicht warst, ignoriere diese Mail."
    )
    html = f"""
    <html><body style="font-family:Arial, sans-serif;">
      <h2>Dein Anmeldecode</h2>
      <p style="font-size:16px">Code:
         <strong style="font-size:22px;letter-spacing:2px">{code}</strong></p>
      <p>Gültig für {CODE_TTL_SECONDS // 60} Minuten.</p>
      <hr/>
      <p style="color:#666;font-size:12px">Falls du das nicht warst, ignoriere diese E-Mail.</p>
    </body></html>
    """
    msg = EmailMessage()
    msg["Subject"] = "Dein Anmeldecode"
    msg["From"] = SMTP_FROM
    msg["To"] = to_email
    msg.set_content(plain)
    msg.add_alternative(html, subtype="html")
    return msg


def send_mail_code(to_email: str, code: str):
    msg = build_message(to_email, code)
    context = ssl.create_default_context()

    if USE_STARTTLS:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.ehlo()
            s.starttls(context=context)
            s.ehlo()
            if SMTP_USER:
                s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
    else:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.ehlo()
            if SMTP_USER:
                try:
                    s.login(SMTP_USER, SMTP_PASS)
                except smtplib.SMTPNotSupportedError:
                    pass
            s.send_message(msg)


def request_login_code(email: str) -> str:
    email = email.strip().lower()
    if not EMAIL_RE.match(email):
        return "Ungültige E-Mail-Adresse."
    init_sqlitedb()
    now = int(time.time())
    row = load_otp(email)
    if row and now - row["last_sent_at"] < RESEND_COOLDOWN:
        return "Bitte warte kurz, bevor du einen neuen Code anforderst."

    code = random_numeric_code(CODE_LEN)
    code_hash = hash_code(email, code)
    send_mail_code(email, code)
    save_otp(email, code_hash, now, now + CODE_TTL_SECONDS)
    return f"Code an {email} gesendet (gültig {CODE_TTL_SECONDS // 60} Min)."


def verify_login_code(email: str, code: str) -> bool:
    email = email.strip().lower()
    init_sqlitedb()
    row = load_otp(email)
    if not row:
        return False
    now = int(time.time())
    if now > row["expires_at"]:
        delete_otp(email)
        return False
    if row["attempts"] >= MAX_ATTEMPTS:
        return False
    ok = hmac.compare_digest(row["code_hash"], hash_code(email, code.strip()))
    if ok:
        delete_otp(email)
        return True
    inc_attempt(email)
    return False


# ==========================================
# ---------- STREAMLIT APP ----------
# ==========================================
st.set_page_config(page_title="Mittweida Certificate Generator", page_icon="🎓")

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

if "auth_email" not in st.session_state:
    st.session_state.auth_email = None

# --- Login-Gate ---
if not st.session_state.auth_email and not st.session_state.admin_authenticated:
    with st.container(border=True):
        st.subheader("🔐 Anmeldung")
        email_req = st.text_input("E-Mail", placeholder="john@example.de")
        if email_req.strip().lower() == ADMIN_EMAIL.strip().lower():
            st.session_state.admin_authenticated = True
            st.rerun()
        if st.button("Code senden", use_container_width=True):
            try:
                msg = request_login_code(email_req)
                st.success(msg)
            except Exception as e:
                st.error(f"Versand fehlgeschlagen: {e}")
        code_input = st.text_input("Anmeldecode", placeholder="6-stelliger Code")
        if st.button("Anmelden", use_container_width=True):
            if verify_login_code(email_req, code_input):
                st.session_state.auth_email = email_req.strip().lower()
                st.success("Erfolgreich angemeldet!")
                st.rerun()
            else:
                st.error("Ungültiger Code oder zu viele Fehlversuche.")

    st.stop()


def user_content():
    if not st.session_state.admin_authenticated:
        placeholder_column, logo_column = st.columns(2)
        try:
            hsmw_logo = Image.open(os.path.join('resources', 'logo.png'))
            logo_column.image(hsmw_logo, use_container_width=True)
        except Exception:
            logo_column.write("")

        st.markdown(f"<h1 class='no-fade'>Mittweida Certificate Generator</h1>", unsafe_allow_html=True)
        with st.container(border=True):
            header_column, qrcode_column = st.columns([3, 1])
            with header_column.container(vertical_alignment="distribute"):
                st.markdown(f"<h3 class='no-fade'>Zertifikatsservice der Hochschule Mittweida</h3>",
                            unsafe_allow_html=True)
                alternate_email = st.text_input("Alternative E-Mail hinterlegen", value="", key="alternative_email",
                                                help="Hier können Sie eine alternative E-Mail-Adresse hinterlegen, welche Ihnen Zugriff auf Ihre Zertifikate ermöglicht.")
                if alternate_email:
                    # TODO: Alternative E-Mail in DB speichern
                    st.success(f"Alternative E-Mail '{alternate_email}' hinterlegt.")
            try:
                qr_image = Image.open(os.path.join('resources', 'qrcode.png'))
                qrcode_column.image(qr_image, caption="Hier Zertifikat verifizieren!", use_container_width=True)
            except Exception:
                qrcode_column.write("")

        with st.container(border=True):
            st.markdown(f"<h4 class='no-fade'>Meine Zertifikate</h4>", unsafe_allow_html=True)
            search_query = st.text_input("Suche", placeholder="Nach Kurs oder Thema suchen...", key="search")

            if search_query:
                st.write(f"Suchergebnisse für '{search_query}':")

            year_column, platform_column = st.columns([1, 1])
            with year_column:
                selected_year = st.selectbox("Jahr", ["Alle", "2025", "2024", "2023", "2022", "2021", "2020"])
            with platform_column:
                selected_platform = st.selectbox("Plattform", ["Alle", "Moodle", "Opal", "Andere"])

            certs_per_row = 2
            certs = [
                {"title": "Datenbanken 101", "platform": "Moodle", "year": "2023"},
                {"title": "Einführung in Python", "platform": "Opal", "year": "2022"},
                {"title": "Webentwicklung Basics", "platform": "Andere", "year": "2021"},
                {"title": "Maschinelles Lernen", "platform": "Moodle", "year": "2024"},
                {"title": "Netzwerktechnik", "platform": "Opal", "year": "2020"},
            ]
            filtered_certs = [c for c in certs if
                              (selected_year == "Alle" or c["year"] == selected_year) and
                              (selected_platform == "Alle" or c["platform"] == selected_platform) and
                              (search_query.lower() in c["title"].lower() if search_query else True)]
            rows = [filtered_certs[i:i + certs_per_row] for i in range(0, len(filtered_certs), certs_per_row)]
            with st.container(height=550, border=False):
                for row in rows:
                    cert_columns = st.columns(certs_per_row)
                    for idx, cert in enumerate(row):
                        with cert_columns[idx]:
                            with st.container(border=True, height=250, vertical_alignment="distribute"):
                                st.markdown(f"#### {cert['title']}")
                                st.markdown(f"**Plattform:** {cert['platform']}")
                                st.markdown(f"**Jahr:** {cert['year']}")
                                if st.button("Zertifikat ansehen", key=f"download_{cert['title']}",
                                             use_container_width=True):
                                    st.session_state['show_cert_details'] = cert['title']

        if 'show_cert_details' in st.session_state:
            cert_title = st.session_state['show_cert_details']
            cert_info = next((c for c in certs if c['title'] == cert_title), None)
            if cert_info:
                with st.container(border=True):
                    left, right = st.columns([2, 1])
                    with left:
                        st.markdown(f"<h4>{cert_info['title']}</h4>", unsafe_allow_html=True)
                        st.markdown(f"**Plattform:** {cert_info['platform']}")
                        st.markdown(f"**Jahr:** {cert_info['year']}")
                    with right:
                        st.image("https://placehold.co/200x120?text=Zertifikat", caption="Vorschau",
                                 use_container_width=True)
                        st.button("Als PDF herunterladen", key="pdf_download", use_container_width=True)


def admin_content():
    st.markdown(f"<h1 class='no-fade'>Admin Dashboard</h1>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("## Zertifikate hochladen")
        uploaded_file = st.file_uploader("CSV-Datei mit Zertifikatsdaten hochladen", type=["csv"],
                                         accept_multiple_files=True)
        if uploaded_file:
            insert_csv(uploaded_file)
            st.success("Datei erfolgreich hochgeladen!")


if st.session_state.admin_authenticated:
    admin_content()
else:
    user_content()
