from transformers import pipeline
from utils import log_message

def summarize_clusters(emails, clusters):
    """
    Summarize emails in each cluster using an NLP model.
    
    Args:
        emails (list): List of preprocessed email texts.
        clusters (list): List of cluster assignments for each email.
    
    Returns:
        dict: Dictionary mapping cluster IDs to summaries.
    """
    try:
        if not emails or not clusters or len(emails) != len(clusters):
            log_message("Error: Invalid input for summarization (empty or mismatched emails/clusters).", level="error")
            raise ValueError("Invalid input for summarization.")
        
        log_message(f"Summarizing {len(emails)} emails across {len(set(clusters))} clusters...")
        
        # Initialize summarization model
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        
        # Group emails by cluster
        cluster_dict = {}
        for email, cluster_id in zip(emails, clusters):
            if cluster_id not in cluster_dict:
                cluster_dict[cluster_id] = []
            cluster_dict[cluster_id].append(email)
        
        # Summarize each cluster
        summaries = {}
        for cluster_id, cluster_emails in cluster_dict.items():
            # Combine emails in the cluster
            combined_text = " ".join(email for email in cluster_emails if email.strip())
            if not combined_text:
                log_message(f"Warning: Cluster {cluster_id} contains no valid text.", level="warning")
                summaries[cluster_id] = "No content to summarize."
                continue
            
            # Summarize (limit input length to avoid model errors)
            max_input_length = 1024  # BART's max input length
            if len(combined_text) > max_input_length:
                combined_text = combined_text[:max_input_length]
            
            try:
                summary = summarizer(
                    combined_text,
                    max_length=100,
                    min_length=25,
                    do_sample=False
                )[0]["summary_text"]
                summaries[cluster_id] = summary
            except Exception as e:
                log_message(f"Error summarizing cluster {cluster_id}: {str(e)}", level="warning")
                summaries[cluster_id] = "Summary generation failed."
        
        log_message("Summarization completed.")
        return summaries
    
    except Exception as e:
        log_message(f"Error in summarization: {str(e)}", level="error")
        raise