
from src.train_model import train_and_save_model

if __name__ == '__main__':
    BUCKET_NAME = 'credit-fraud-detection-bk'
    FILE_KEY = 'creditcard.csv'
    train_and_save_model(BUCKET_NAME, FILE_KEY)
