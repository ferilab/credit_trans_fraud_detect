
# src/prepare_data.py
import boto3
import pandas as pd
from io import StringIO
from sklearn.model_selection import train_test_split

def load_data_from_s3(bucket_name, file_key, region='us-east-2'):
    s3 = boto3.client('s3', region_name=region)
    obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    data = pd.read_csv(StringIO(obj['Body'].read().decode('utf-8')))
    return data

def prepare_data(df):
    X = df.drop(columns=['Class'])
    y = df['Class']
    return train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)
