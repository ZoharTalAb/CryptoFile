import json
from urllib import request, error

from core.config import (
    FRONTEND_BASE_URL,
    RESEND_API_KEY,
    RESEND_FROM_EMAIL,
)


class EmailService:
    def send_password_reset_email(self, to_email: str, token: str):
        if not RESEND_API_KEY:
            raise RuntimeError("RESEND_API_KEY is not configured")

        if not RESEND_FROM_EMAIL:
            raise RuntimeError("RESEND_FROM_EMAIL is not configured")

        reset_link = f"{FRONTEND_BASE_URL}/reset-password?token={token}"

        payload = {
            "from": RESEND_FROM_EMAIL,
            "to": [to_email],
            "subject": "CryptoFile Password Reset",
            "text": (
                "You requested a password reset.\n\n"
                f"Click the link below to reset your password:\n\n{reset_link}\n\n"
                "If you did not request this, please ignore this email."
            ),
        }

        body = json.dumps(payload).encode("utf-8")

        req = request.Request(
            url="https://api.resend.com/emails",
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
                "User-Agent": "CryptoFile/1.0",
            },
        )

        try:
            with request.urlopen(req, timeout=20) as response:
                response_body = response.read().decode("utf-8")
                print(f"[EMAIL] Resend response: {response.status} {response_body}")
        except error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            print(f"[EMAIL] Resend HTTPError: {exc.code} {error_body}")
            raise RuntimeError(
                f"Failed to send password reset email: {error_body}"
            ) from exc
        except error.URLError as exc:
            print(f"[EMAIL] Resend URLError: {exc}")
            raise RuntimeError("Failed to reach email provider") from exc
