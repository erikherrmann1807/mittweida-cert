import hashlib
import secrets
import string

from src.auth.otp_mail.config import CODE_LEN


def random_numeric_code(n=CODE_LEN) -> str:
    return "".join(secrets.choice(string.digits) for _ in range(n))


def hash_code(email: str, code: str) -> str:
    return hashlib.sha256((email + ":" + code).encode("utf-8")).hexdigest()