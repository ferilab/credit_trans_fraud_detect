
# src/train_model.py
import os
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from src.prepare_data import load_data_from_s3, prepare_data

def train_and_save_model(bucket_name, file_key, output_path='models/fraud_model.pkl'):
    df = load_data_from_s3(bucket_name, file_key)
    X_train, X_test, y_train, y_test = prepare_data(df)

    model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'wb') as f:
        pickle.dump(model, f)

