import smtplib
import random
from email.mime.text import MIMEText

# ⚠️ DEMO CONFIG — replace with real SMTP credentials for production use.
# Leave blank to run in "console mode": OTP prints to terminal + is shown
# to the Super Admin on screen, so the flow can be demoed without a live inbox.
SENDER_EMAIL = ""       # e.g. "codecraft.security@gmail.com"
SENDER_PASSWORD = ""    # e.g. Gmail App Password (not your normal password)
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(to_email, name, otp_code):
    """
    Sends the OTP to the pending admin's university email.
    Returns (success: bool, mode: str) — mode is 'sent' or 'console'.
    """
    subject = "CodeCraft Admin Verification Code"
    body = (
        f"Hello {name},\n\n"
        f"A Super Admin is verifying your CodeCraft admin account request.\n"
        f"Your one-time verification code is: {otp_code}\n\n"
        f"This code expires in 10 minutes. If you did not request admin access, "
        f"please ignore this email.\n\n"
        f"— CodeCraft Security Team"
    )

    if not SENDER_EMAIL or not SENDER_PASSWORD:
        # Console/demo mode — no real SMTP configured
        print(f"\n[DEMO MODE] OTP for {to_email}: {otp_code}\n")
        return True, "console"

    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, [to_email], msg.as_string())
        return True, "sent"
    except Exception as e:
        print(f"[MAIL ERROR] {e} — falling back to console mode")
        print(f"[DEMO MODE] OTP for {to_email}: {otp_code}\n")
        return True, "console"