import hmac
import time

from src.auth.otp_database.init_database import init_sqlitedb
from src.auth.otp_database.operations import *
from src.auth.otp_mail.config import RESEND_COOLDOWN, EMAIL_RE, CODE_LEN, CODE_TTL_SECONDS, MAX_ATTEMPTS
from src.auth.otp_mail.email import send_mail_code
from src.auth.otp_mail.util import hash_code, random_numeric_code


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