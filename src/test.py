from preprocess import preprocess_emails
from cluster import cluster_emails
from email_fetcher import fetch_emails
emails=fetch_emails(5)
processed = preprocess_emails(emails)
cleaned_texts = [email["cleaned"] for email in processed]
print(cleaned_texts)


'''clusters = cluster_emails(processed, num_clusters=2)
for i, (email, cluster) in enumerate(zip(processed, clusters)):
    print(f"Email {i+1}: {email[:50]}... -> Cluster {cluster}")'''