import imaplib
import email
from email.header import decode_header
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pickle
import os
from datetime import datetime
from .config import EMAIL_CONFIG
from .utils import log_message
import socket

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
            try:
                creds.refresh(Request())
            except Exception as e:
                log_message(f"Failed to refresh credentials: {str(e)}", level="error")
                creds = None
        if not creds:
            # Try multiple ports to avoid conflicts
            ports = range(8000, 8011)  # Try ports 8000 to 8010
            for port in ports:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        EMAIL_CONFIG["gmail_client_secret"], scopes
                    )
                    creds = flow.run_local_server(port=port, bind_addr="localhost")
                    with open(token_path, "wb") as token:
                        pickle.dump(creds, token)
                    log_message(f"Authenticated successfully on port {port}.")
                    break
                except socket.error as e:
                    log_message(f"Port {port} in use: {str(e)}", level="warning")
                    if port == ports[-1]:
                        raise Exception("All ports in range are in use. Please free up a port.")
                    continue
                except Exception as e:
                    log_message(f"Authentication failed on port {port}: {str(e)}", level="error")
                    raise

    return creds

def get_access_token():
    """Get access token for Gmail."""
    creds = get_gmail_credentials()
    if not creds:
        raise Exception("Failed to obtain valid credentials.")
    return creds.token

def fetch_emails(from_date: str, max_emails: int = 50):
    """
    Fetch emails from Gmail using IMAP with OAuth from a specified date to today.
    
    Args:
        from_date (str): Start date in YYYY-MM-DD format.
        max_emails (int): Maximum number of emails to fetch (default: 50).
    
    Returns:
        list: List of email data (dict with id, subject, from, date, body).
    """
    try:
        log_message("Connecting to Gmail IMAP server...")
        
        access_token = get_access_token()
        
        imap_server = EMAIL_CONFIG["imap_server"]
        username = EMAIL_CONFIG["username"]
        
        mail = imaplib.IMAP4_SSL(imap_server)
        auth_string = f"user={username}\1auth=Bearer {access_token}\1\1"
        mail.authenticate("XOAUTH2", lambda x: auth_string)
        mail.select("inbox")
        
        try:
            from_datetime = datetime.strptime(from_date, '%Y-%m-%d')
            if from_datetime > datetime.now():
                raise ValueError("Start date cannot be in the future.")
            imap_date = from_datetime.strftime('%d-%b-%Y')
        except ValueError as e:
            log_message(f"Invalid date format or value: {str(e)}", level="error")
            raise
        
        log_message(f"Fetching up to {max_emails} emails from {from_date}...")
        _, data = mail.search(None, f'(SINCE "{imap_date}")')
        email_ids = data[0].split()[-max_emails:]
        
        emails = []
        for eid in email_ids:
            _, msg_data = mail.fetch(eid, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            subject, encoding = decode_header(msg["subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")
            
            email_from = decode_header(msg["from"])[0][0]
            if isinstance(email_from, bytes):
                email_from = email_from.decode(encoding if encoding else "utf-8")
            
            date = msg["date"]
            
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                body = msg.get_payload(decode=True).decode()
            
            emails.append({
                'id': eid.decode(),
                'subject': subject,
                'from': email_from,
                'date': date,
                'body': body
            })
        
        mail.logout()
        log_message(f"Successfully fetched {len(emails)} emails from Gmail.")
        return emails
    
    except Exception as e:
        log_message(f"Error fetching emails from Gmail: {str(e)}", level="error")
        raise