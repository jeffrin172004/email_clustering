import json
from preprocess import clean_text
from embedding import embed_emails
from cluster import cluster_embeddings
from report import cluster_report

with open('data/emails.json') as f:
    emails = json.load(f)

texts = [clean_text(email['subject'] + ' ' + email['body']) for email in emails]
print(texts)

embeddings = embed_emails(texts)
labels = cluster_embeddings(embeddings)
report = cluster_report(emails, labels)
print(report)