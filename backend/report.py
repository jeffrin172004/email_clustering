import pandas as pd

def cluster_report(emails, labels):
    df = pd.DataFrame(emails)
    df['cluster'] = labels
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.floor('H')
    return df.groupby(['hour', 'cluster']).size().reset_index(name='count')