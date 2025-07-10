import imaplib
import email
from email.header import decode_header
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os
from config import EMAIL_CONFIG
from utils import log_message


def get_gmail_credentials():
    """Obtain or refresh Gmail OAuth credentials."""
    creds = None
    token_path = "token.pickle"
    scopes = ["https://mail.google.com/"]

    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                EMAIL_CONFIG["gmail_client_secret"], scopes
            )
            creds = flow.run_local_server(port=8000)
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)

    return creds


def extract_plain_text(msg):
    """
    Extract only the plain text part of the email, ignoring HTML and attachments.
    """
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    return part.get_payload(decode=True).decode(errors="ignore")
                except Exception:
                    continue
    else:
        if msg.get_content_type() == "text/plain":
            return msg.get_payload(decode=True).decode(errors="ignore")

    return ""  # Return empty if no suitable plain text found


def fetch_emails(num_emails=50):
    """
    Fetch emails from Gmail using IMAP with OAuth.

    Args:
        num_emails (int): Number of emails to fetch (default: 50).

    Returns:
        list: List of email dictionaries with subject, body, and timestamp.
    """
    try:
        log_message("Connecting to Gmail IMAP server...")

        creds = get_gmail_credentials()
        access_token = creds.token

        imap_server = EMAIL_CONFIG["imap_server"]
        username = EMAIL_CONFIG["username"]

        mail = imaplib.IMAP4_SSL(imap_server)
        auth_string = f"user={username}\1auth=Bearer {access_token}\1\1"
        mail.authenticate("XOAUTH2", lambda x: auth_string)
        mail.select("inbox")

        log_message(f"Fetching {num_emails} emails...")
        _, data = mail.search(None, "ALL")
        email_ids = data[0].split()[-num_emails:]

        emails = []
        for eid in email_ids:
            _, msg_data = mail.fetch(eid, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject, encoding = decode_header(msg["subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")

            body = extract_plain_text(msg)

            emails.append({
                "subject": subject,
                "body": body,
                "timestamp": msg["Date"]
            })

        mail.logout()
        log_message(f"Successfully fetched {len(emails)} emails from Gmail.")
        return emails

    except Exception as e:
        log_message(f"Error fetching emails from Gmail: {str(e)}", level="error")
        raise
