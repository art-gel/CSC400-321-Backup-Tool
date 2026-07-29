import smtplib
import json
import os
from email.mime.text import MIMEText

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backup_config.json")

# Get SMTP settings based on email domain
def get_smtp_settings(email: str):
    domain = email.split("@")[-1].lower()
    if domain == "gmail.com":
        return "smtp.gmail.com", 465, True
    elif domain in ("outlook.com", "hotmail.com", "live.com"):
        return "smtp.office365.com", 587, False
    elif domain == "yahoo.com":
        return "smtp.mail.yahoo.com", 465, True
    else:
        return f"smtp.{domain}", 587, False

# Send a backup notification email
def send_backup_email(success: bool, details: str = ""):
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
    except Exception:
        return

    if not config.get("email_enabled", False):
        return

    # Get email configuration
    sender    = config.get("email_sender", "").strip()
    password  = config.get("email_password", "").strip()
    recipient = config.get("email_recipient", "").strip()

    if not all([sender, password, recipient]):
        return

    # Check notification preferences
    if success and not config.get("notify_on_success", True):
        return
    if not success and not config.get("notify_on_failure", True):
        return

    # Prepare email content
    subject = "✓ Backup Completed Successfully" if success else "✗ Backup Failed"
    body = (
        f"Your 3-2-1 Backup Tool has completed a backup.\n\n"
        f"Status: Success\n"
        f"{details}\n\n"
        f"— 3-2-1 Backup Tool"
    ) if success else (
        f"Your 3-2-1 Backup Tool encountered an error.\n\n"
        f"Error: {details}\n\n"
        f"Please check your backup drive and settings.\n\n"
        f"— 3-2-1 Backup Tool"
    )

    try:
        send_email_direct(sender, password, recipient, subject, body)
        print(f"[EMAIL] Notification sent to {recipient}")
    except Exception as e:
        print(f"[EMAIL] Failed to send: {e}")

# Send an email directly
def send_email_direct(sender: str, password: str, recipient: str,
                      subject: str, body: str):
    
    host, port, use_ssl = get_smtp_settings(sender)
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"]    = sender
    msg["To"]      = recipient

    if use_ssl:
        with smtplib.SMTP_SSL(host, port) as server:
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
    else:
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())

# Validate email configuration
def validate_email_config(recipient: str, password: str):
    import system_checks
    if not recipient.strip():
        return False, "Email address is required."
    if "@" not in recipient:
        return False, "Enter a valid email address."
    ok, msg = system_checks.validate_app_password(password)
    if not ok:
        return False, msg
    return True, None
