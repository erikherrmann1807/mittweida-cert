import hashlib
import json
import os
import secrets
import string

from src.auth.otp_mail.config import CODE_LEN
from src.database.init_database import postgres


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

def random_numeric_code(n=CODE_LEN) -> str:
    return "".join(secrets.choice(string.digits) for _ in range(n))


def hash_code(email: str, code: str) -> str:
    return hashlib.sha256((email + ":" + code).encode("utf-8")).hexdigest()

def get_placeholders(name: str, email: str, course_name: str, platform: str, created_at: str, cert_number: str) -> dict:
    placeholders = {
        "{{name}}": name,
        "{{email}}": email,
        "{{course_name}}": course_name,
        "{{platform}}": platform,
        "{{created_at}}": created_at,
        "{{cert_number}}": cert_number,
    }

    return placeholders


def get_config():
    with open(os.path.join('.streamlit/', 'config.json'), 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)
    return config