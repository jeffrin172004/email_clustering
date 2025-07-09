from email_fetcher import fetch_emails
from preprocess import preprocess_emails
from cluster import cluster_emails
#from summarizer import summarize_clusters  # Placeholder for next module
from utils import log_message

def main():
    log_message("Starting email analysis system...")
    
    # Fetch emails
    log_message("Fetching emails...")
    raw_emails = fetch_emails()
    
    # Preprocess emails
    log_message("Preprocessing emails...")
    processed_emails = preprocess_emails(raw_emails)
    
    # Cluster emails
    log_message("Clustering emails...")
    clusters = cluster_emails(processed_emails)
    
    # Summarize clusters (placeholder)
   # log_message("Summarizing clusters...")
   # summaries = summarize_clusters(processed_emails, clusters)
    
    # Output results
    for cluster_id, summary in summaries.items():
        print(f"Cluster {cluster_id}:")
        print(f"Summary: {summary}\n")
    
    log_message("Email analysis completed.")

if __name__ == "__main__":
    main()