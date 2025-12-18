import smtplib
from email.message import EmailMessage

from src.auth.otp_mail.config import *
from util import get_mail_context


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


def build_admin_registration_message(to_email: str, email: str, name: str, affiliation: str):
    plain = (
        f"{name} beantragt einen Admin Zugriff\n\n"
        f"Eckdaten:\n\n"
        f"- Name: {name}\n\n"
        f"- Email: {email}\n\n"
        f"- Zugehörigkeit: {affiliation}\n\n"
    )
    html = f"""
        <html><body style="font-family:Arial, sans-serif;">
          <h2>{name} beantragt einen Admin Zugriff</h2>
          <p style="font-size:16px">Eckdaten:
          <hr/>
          <p>Name: {name}</p>
          <p>Email: {email}</p>
          <p>Zugehörigkeit: {affiliation}</p>
          <hr/>
        </body></html>
        """

    msg = EmailMessage()
    msg["Subject"] = f"Admin Registrierung für {name}"
    msg["From"] = SMTP_FROM
    msg["To"] = to_email
    msg.set_content(plain)
    msg.add_alternative(html, subtype="html")
    return msg


def build_admin_confirmation_message(to_email):
    plain = (
        f"Ihr Antrag auf Admin Zugriff wird hiermit bestätigt\n\n"
    )
    html = f"""
            <html><body style="font-family:Arial, sans-serif;">
              <h2>Ihr Antrag auf Admin Zugriff wird hiermit bestätigt</h2>
            </body></html>
            """

    msg = EmailMessage()
    msg["Subject"] = f"Freischaltung Admin Zugriff"
    msg["From"] = SMTP_FROM
    msg["To"] = to_email
    msg.set_content(plain)
    msg.add_alternative(html, subtype="html")
    return msg


def send_mail_code(to_email: str, code: str):
    msg = build_message(to_email, code)
    mail_setup(msg)


def send_admin_registration_mail(to_email: str, email: str, name: str, affiliation: str):
    msg = build_admin_registration_message(to_email, email, name, affiliation)
    mail_setup(msg)


def send_admin_confirmation_mail(to_email: str):
    msg = build_admin_confirmation_message(to_email)
    mail_setup(msg)


def mail_setup(msg: EmailMessage):
    context = get_mail_context()
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
