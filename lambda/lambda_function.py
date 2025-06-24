
# lambda_function.py

import json
import boto3
import pickle
import os
import tempfile

# Constants
BUCKET_NAME = 'credit-fraud-detection-bk'
MODEL_KEY = 'models/fraud_model.pkl'

# Load model from S3
s3 = boto3.client('s3', region_name='us-east-2')
model_path = os.path.join(tempfile.gettempdir(), 'fraud_model.pkl')

if not os.path.exists(model_path):
    s3.download_file(BUCKET_NAME, MODEL_KEY, model_path)

with open(model_path, 'rb') as f:
    model = pickle.load(f)

def lambda_handler(event, context):
    try:
        # Get features from request
        body = json.loads(event['body']) if 'body' in event else event
        features = body['features']  # Must be a list of 30 numbers

        if not isinstance(features, list) or len(features) != 30:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Expected a list of 30 features'})
            }

        # Make prediction
        prediction = model.predict([features])[0]

        return {
            'statusCode': 200,
            'body': json.dumps({'prediction': int(prediction)})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }









# import json
# import boto3
# import joblib
# import os
# import tempfile
# import numpy as np

# # Constants
# BUCKET_NAME = 'credit-fraud-detection-bk'
# MODEL_KEY = 'models/fraud_model.pkl'

# # Load model from S3 once (cold start)
# s3 = boto3.client('s3', region_name='us-east-2')
# model_path = os.path.join(tempfile.gettempdir(), 'fraud_model.pkl')

# if not os.path.exists(model_path):
#     s3.download_file(BUCKET_NAME, MODEL_KEY, model_path)
# model = joblib.load(model_path)

# def lambda_handler(event, context):
#     try:
#         # Parse input
#         body = json.loads(event['body']) if 'body' in event else event
#         features = body['features']  # Expect list of numerical features

#         # Convert input to 2D array for prediction
#         input_array = np.array(features).reshape(1, -1)
#         prediction = model.predict(input_array)[0]

#         return {
#             'statusCode': 200,
#             'body': json.dumps({'prediction': int(prediction)})
#         }
#     except Exception as e:
#         return {
#             'statusCode': 500,
#             'body': json.dumps({'error': str(e)})
#         }
