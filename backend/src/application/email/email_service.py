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
            "subject": "Reset your CryptoFile password",
            "text": (
                "You requested a password reset.\n\n"
                f"Open the link below to reset your password:\n\n{reset_link}\n\n"
                "If you did not request this, you can safely ignore this email."
            ),
            "html": f"""
                <div style="font-family:Arial,sans-serif;max-width:560px;margin:0 auto;padding:24px;color:#0f172a;">
                    <h2 style="margin-bottom:16px;">Reset your CryptoFile password</h2>
                    <p style="font-size:16px;line-height:1.6;margin-bottom:16px;">
                        We received a request to reset your CryptoFile password.
                    </p>
                    <p style="font-size:16px;line-height:1.6;margin-bottom:24px;">
                        Click the button below to choose a new password:
                    </p>
                    <a
                        href="{reset_link}"
                        style="display:inline-block;padding:12px 20px;background:#6d5efc;color:#ffffff;text-decoration:none;border-radius:10px;font-weight:600;"
                    >
                        Reset password
                    </a>
                    <p style="font-size:14px;line-height:1.6;margin-top:24px;color:#475569;">
                        If the button does not work, copy and paste this link into your browser:
                    </p>
                    <p style="font-size:14px;line-height:1.6;word-break:break-all;color:#0f172a;">
                        {reset_link}
                    </p>
                    <p style="font-size:14px;line-height:1.6;margin-top:24px;color:#475569;">
                        If you did not request this, you can safely ignore this email.
                    </p>
                </div>
            """,
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
