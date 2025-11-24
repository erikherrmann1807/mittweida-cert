import smtplib
import ssl
from email.message import EmailMessage

from src.auth.otp_mail.config import *


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