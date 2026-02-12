"""SMTP email service — same logic as TG bot."""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings

logger = logging.getLogger(__name__)


def send_email_to_it(user, issue):
    """Send email notification to IT team. Returns True if sent, False if failed."""
    sender_email = settings.SENDER_EMAIL
    sender_password = settings.SENDER_PASSWORD
    receiver_email = settings.RECEIVER_EMAIL

    if not all([sender_email, sender_password, receiver_email]):
        logger.error("Email config missing: SENDER_EMAIL, SENDER_PASSWORD, or RECEIVER_EMAIL not set")
        return False

    subject = f"CRITICAL ISSUE: {issue.upper()}"
    body = f"""
A critical issue was detected.

User: {user}
Issue Category: {issue}

Please check the problem immediately.
"""

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT, timeout=10)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        logger.info(f"Email sent successfully for user: {user}")
        return True
    except Exception as e:
        logger.error(f"Email send failed: {e}")
        return False
