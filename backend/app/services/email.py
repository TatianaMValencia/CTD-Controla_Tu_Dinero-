"""Envío de código 2FA. Dev: log. Prod: Gmail SMTP (app password)."""
import logging
import smtplib
from email.mime.text import MIMEText

from app.core.config import settings

log = logging.getLogger("ctd.email")


def send_2fa_code(to_email: str, code: str) -> None:
    subject = "Tu código CTD"
    body = f"Tu código para entrar a CTD es: {code}\nVence en {settings.twofa_ttl_min} minutos. Si no lo pediste, ignóralo."
    if not settings.smtp_host or not settings.smtp_user:
        log.warning("SMTP no configurado. Código 2FA para %s: %s", to_email, code)
        print(f"[2FA DEV] {to_email}: {code}")
        return
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = to_email
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as s:
        s.starttls()
        s.login(settings.smtp_user, settings.smtp_password)
        s.send_message(msg)


def send_password_code(to_email: str, code: str) -> None:
    subject = "Cambia tu contraseña CTD"
    body = f"Tu código de 10 dígitos para cambiar tu contraseña es: {code}\nVence en {settings.twofa_ttl_min} minutos. Si no lo pediste, ignóralo y revisa tu cuenta."
    if not settings.smtp_host or not settings.smtp_user:
        log.warning("SMTP no configurado. Código password para %s: %s", to_email, code)
        print(f"[PW DEV] {to_email}: {code}")
        return
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = to_email
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as s:
        s.starttls()
        s.login(settings.smtp_user, settings.smtp_password)
        s.send_message(msg)
