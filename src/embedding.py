from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_emails(email_texts):
    return model.encode(email_texts)