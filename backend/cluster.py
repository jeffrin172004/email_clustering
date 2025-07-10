from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from utils import log_message

def cluster_emails(emails, num_clusters=5):
    """
    Cluster emails based on their content using TF-IDF and K-means.
    
    Args:
        emails (list): List of preprocessed email texts.
        num_clusters (int): Number of clusters to form (default: 5).
    
    Returns:
        list: Cluster assignments for each email.
    """
    try:
        if not emails:
            log_message("Error: No emails provided for clustering.", level="error")
            raise ValueError("No emails to cluster.")
        
        log_message(f"Clustering {len(emails)} emails into {num_clusters} clusters...")
        
        # Convert emails to TF-IDF features
        vectorizer = TfidfVectorizer(
            stop_words="english",
            max_df=0.8,  # Ignore terms that appear in >80% of emails
            min_df=2,    # Ignore terms that appear in <2 emails
            max_features=1000  # Limit to top 1000 features for efficiency
        )
        X = vectorizer.fit_transform(emails)
        
        # Apply K-means clustering
        kmeans = KMeans(n_clusters=num_clusters, random_state=42)
        clusters = kmeans.fit_predict(X)
        
        log_message(f"Successfully clustered {len(emails)} emails into {num_clusters} clusters.")
        return clusters.tolist()
    
    except Exception as e:
        log_message(f"Error clustering emails: {str(e)}", level="error")
        raise