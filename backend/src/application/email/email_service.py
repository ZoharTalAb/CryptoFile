import smtplib
from email.mime.text import MIMEText

from core.config import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_PASSWORD,
    SMTP_FROM_EMAIL,
    FRONTEND_BASE_URL,
)


class EmailService:
    def send_password_reset_email(self, to_email: str, token: str):
        reset_link = f"{FRONTEND_BASE_URL}/reset-password?token={token}"

        subject = "CryptoFile Password Reset"
        body = f"""
You requested a password reset.

Click the link below to reset your password:

{reset_link}

If you did not request this, please ignore this email.
"""

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SMTP_FROM_EMAIL
        msg["To"] = to_email

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
