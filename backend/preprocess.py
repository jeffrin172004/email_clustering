import re
import nltk
from nltk.corpus import stopwords
from utils import log_message

# Download NLTK stopwords (run once during setup)
try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")

def preprocess_text(email_text, remove_stopwords=False):
    """
    Clean and normalize email text for further processing.
    
    Args:
        email_text (str): Raw email body text.
        remove_stopwords (bool): Whether to remove stopwords (default: False).
    
    Returns:
        str: Cleaned and normalized text.
    """
    try:
        log_message("Preprocessing email text...")
        
        # Remove HTML tags
        text = re.sub(r"<[^>]+>", "", email_text)
        
        # Remove email signatures (basic heuristic: lines starting with "--" or "Sent from")
        text = re.sub(r"(?m)^--.*$|^Sent from.*$|^On .* wrote:.*$", "", text, flags=re.MULTILINE)
        
        # Remove quoted replies (lines starting with ">")
        text = re.sub(r"(?m)^>.*$", "", text, flags=re.MULTILINE)
        
        # Remove URLs
        text = re.sub(r"http[s]?://\S+", "", text)
        
        # Remove email addresses
        text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "", text)
        
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()
        
        # Convert to lowercase
        text = text.lower()
        
        # Optionally remove stopwords
        if remove_stopwords:
            stop_words = set(stopwords.words("english"))
            words = text.split()
            text = " ".join(word for word in words if word not in stop_words)
        
        if not text:
            log_message("Warning: Preprocessed text is empty.", level="warning")
            return ""
        
        log_message("Text preprocessing completed.")
        return text
    
    except Exception as e:
        log_message(f"Error preprocessing text: {str(e)}", level="error")
        raise

def preprocess_emails(email_dicts, remove_stopwords=False):
    """
    Preprocess a list of email dictionaries (subject + body).

    Args:
        email_dicts (list): List of email dictionaries.
        remove_stopwords (bool): Whether to remove stopwords from text.

    Returns:
        list: List of email dicts with added 'cleaned' field.
    """
    try:
        log_message(f"Preprocessing {len(email_dicts)} emails (with metadata)...")
        preprocessed = []

        for email in email_dicts:
            if not email.get("subject") and not email.get("body"):
                log_message("Warning: Skipping empty email.", level="warning")
                continue

            # Combine subject and body
            combined_text = f"{email.get('subject', '')} {email.get('body', '')}"
            cleaned_text = preprocess_text(combined_text, remove_stopwords)

            if cleaned_text:
                email["cleaned"] = cleaned_text
                preprocessed.append(email)
            else:
                log_message("Warning: Email was filtered out during preprocessing.", level="warning")

        log_message(f"Successfully preprocessed {len(preprocessed)} emails.")
        return preprocessed

    except Exception as e:
        log_message(f"Error preprocessing emails: {str(e)}", level="error")
        raise
