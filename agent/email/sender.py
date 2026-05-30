"""
Email sender — Gmail SMTP with app password.
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send(subject: str, html_body: str) -> bool:
    """
    Send email via Gmail SMTP.

    Returns:
        True if sent successfully, False otherwise.
    """
    smtp_user = os.getenv("SMTP_USER", "").strip()
    smtp_pass = os.getenv("SMTP_PASS", "").strip()
    from_email = os.getenv("FROM_EMAIL", smtp_user).strip()
    to_email = os.getenv("TO_EMAIL", smtp_user).strip()

    if not smtp_user or not smtp_pass:
        print("[EMAIL] Missing SMTP_USER or SMTP_PASS — cannot send email")
        return False

    if not to_email:
        print("[EMAIL] Missing TO_EMAIL — cannot send email")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    # Plain text fallback
    plain = f"{subject}\n\nOpen this email in an HTML-capable client to view your digest."
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, to_email, msg.as_string())
        print(f"[EMAIL] Digest sent to {to_email}")
        return True
    except smtplib.SMTPAuthenticationError:
        print("[EMAIL] Authentication failed — check SMTP_USER and SMTP_PASS (use Gmail App Password, not account password)")
        return False
    except Exception as e:
        print(f"[EMAIL] Failed to send: {e}")
        return False
