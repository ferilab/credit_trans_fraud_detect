# credit_trans_fraud_detect
A fraud detection model to recognize fraudulent credit card transactions. It is deployed on AWS API Gateway, and is retrained on pushing the updated model on GitHub or whenever the training data is updated on AWS S3 followed with a new model push to GitHub.

A full real-time fraud detection pipeline using:

    - Reading data from S3 and preparing it (data is already preprocessed and feature engineeried using PCA)
    - Model training on push via GitHub Actions using GitHub Run
    - Model storage in S3
    - Real-time inference via AWS Lambda + API Gateway (https endpoint)
    - Real-time prediction with no unnecessary dependencies

# Dataset

Includes 14708 transactions with 492 fraud cases (Class = 1). There is 30 variables (PCA) and a binary target (Class). This dataset is a downsampled version of the dataset Credit Card Fraud Detection available on https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud with all Class = 1 preserved.

The original dataset contains transactions made by credit cards in September 2013 by European cardholders.
This dataset presents transactions that occurred in two days, where we have 492 frauds out of 284,807 transactions. The dataset is highly unbalanced, the positive class (frauds) account for 0.172% of all transactions.

It contains only numerical input variables which are the result of a PCA transformation. Unfortunately, due to confidentiality issues, the original features and more background information about the data are not provided. Features V1, V2, … V28 are the principal components obtained with PCA, the only features which have not been transformed with PCA are 'Time' and 'Amount'. Feature 'Time' contains the seconds elapsed between each transaction and the first transaction in the dataset. The feature 'Amount' is the transaction Amount, this feature can be used for example-dependant cost-sensitive learning. Feature 'Class' is the response variable and it takes value 1 in case of fraud and 0 otherwise.

# Project structure

credit_trans_fraud_detect/
│
├──data/
│ └── creditcard.csv # To be uploded to your AWS S3 bucket upfront
│
├── models/
│ └── fraud_model.pkl # Saved model (actually in cloud run it will be uploaded to S3 then)
│
├── .github/workflows/
│ └── train_model.yml # GitHub Actions workflow for training
│
├──lambda/
│ └── lambda_function.py # Deployed to AWS Lambda for inference
│ └── function.zip       # The compressed lambda_function.py to be uploaded to your Lambda function's code
│
|── src/
│ └── train_model.py # Trains and exports model
| └── prepare_data.py # Loads data from S3 and splits variables from target
|
├── requirements.txt
├── main.py # The main module to load the data, train the model, and upload it to S3
├── run.ipynp # To test the endpoint from python
└── README.md

# Process flow

+---------------------+ +-------------------+ +-------------------+
| GitHub (main push) +-----> | GitHub Actions CI |-----> | Train model using sklearn + upload 
|  fraud_model.pkl |
+---------------------+ +-------------------+ +--------+----------+

+---------------------+
| S3: Model Storage |
| credit-fraud-...bk |
+--------+------------+

+------------------------+
| AWS Lambda |
| Loads model from S3 |
| Performs predictions |
+-----------+------------+

+-------------------------+
| API Gateway |
| /predict endpoint |
+-------------------------+

# Cloud setup (AWS)

You first need to fork the repo to your personal GitHub account. This repo will do the CI/CD including training and retraining of the odel for you.

1. Create an AWS account (a free trail if you already don't have)

2. Sign in with your IAM acccount

3. Give it full role access.

4. Creats a bucket in S3 (we named it credit-fraud-detection-bk, you can make yours and update the code accordingly).

5. Go to your AWS IAM Console, under Access Keys click Create access key and choose Command Line Interface (CLI). Now create access key and save the key id and access key. Then, set the secrets of your cloned repository (Settings - Secrets and variables - Actions). Name them AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_REGION (the region you choose for your S3 bucket or Lambda).

6. Create a Lambda function (for Architecture and Runtimes choose x86_64 and Python 3.10). I named it credit-trans-fraud-detect-lambda-func but you can use yours. Now you need to give it permission to access S3 (your bucket). Create a new role (through Roles) for the function and attach this json as its inline policy. You can name it whatever you want e.g., S3ReadAccess. 

{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::credit-fraud-detection-bk/*"
    }
  ]
}

7. Assign the created role to the Lambda function you already created.

8. zip the lambda_function.py as function.zip (if you don't have it under lambda folder or if you modified it). Upload it to the Code tab of the lambda function (select 'Upload from .zip')

9. We need to connect the function to API Gateway:
    - Create a HTTP API in Amazon API Gateway
    - Now we link the API to our Lambda function. Integration type is Lambda and Method is POST. Lets' call the Resource '/predict'.
    - Finally, you can deploy API that let's you to get a public URL (your real-time inference endpoint).

10. Lambda Layer
The trained model uses sklearn that includes Numpy, Scipy and joblib. Although the training process in done in GitHub run (not in Lambda), even with the trained model (uploaded to S3) the Lambda function will need those dependencies for inference. This is how we make required dependencies available for Lambda.

- Make sure Docker is installed and is running on your system. Also make sure it is already added to your system path. If not, run "export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"
That is for mac, now run docker --version to see if it works, then re-run docker with "docker run ..."
- In a terminal, go to the root of your package (e.g., credit_trand_fraud_detect)
- run "mkdir -p sklearn_layer/python"
- then run (note: we assume that you have chosen Python 3.10 and x86_64 for your Lambda function):
docker run --rm -v "$(pwd)/sklearn_layer/python:/asset" --entrypoint /bin/bash public.ecr.aws/lambda/python:3.10-x86_64 -c "pip install scikit-learn -t /asset && exit"
- The previous line installed the required dependencies (sklearn) in a folder named sklear_layer. zip it with:
cd sklearn_layer
zip -r ../sklearn_layer.zip .
- you can go one level back with "cd .." now. The generated sklearn_layer.zip is what you need to add to the Lambda function's layer. As it is > 50 MB, you can't directly upload it to the layer. Instead, you can upload it to S3, under your bucket, create a folder named 'layer' and upload it there.
- Go to Lambda in your AWS console, then to Layers and create a Layer. Give it a name and link it to the saved zip file on your S3 bucket. For Architecture and Runtimes choose x86_64 and Python 3.10. 
- Finally, go to Lambda -> Functions, choose the lambda function and at the bottom of the page use 'Add layer' -> Custom to assign the layer we just created to it.


# Inference Request Example

Endpoint: `https://<your-api-id>.execute-api.us-east-2.amazonaws.com/predict`

Sample test point:

Use it in your AWS Lambda function -> Test -> Event JSON 
{
  "features": [0.1, -1.2, 0.3, ..., 200.0]  // 30 values total
}

Sample expected response:

{
  "prediction": 0
}

Inference using Python:

Use the run notebook.


# Setup Instructions

git clone https://github.com/ferilab/credit_trans_fraud_detect.git
cd credit_trans_fraud_detect

# Local use

Prepare environment and run the main module.

pip install -r requirements.txt
python train_model.py

# Deploy model

- Manually upload the dataset (creditcard.csv) to your bucket on S3.

- Set upyour GitHub Actions secrets:
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION

- Now, on commit and push to main, the model will be retrained and uploaded to your bucket in S3.

- Infere a sample transaction using the Test tab of your Lambda function on AWS console. The sample transaction should be like this:
{
    "features": [
        118716.0, -0.39096448, -3.763199, -3.603844, 1.5876892, -0.47663704, -0.5617021, 2.1779633, -0.6973479, -0.018830955, -0.9399685, -0.35247976, 0.30234602, 0.7528182, -0.5717872, 0.4877511, 0.2844196, 0.6142388, 0.16805398, -0.70408744, 2.4774666, 0.77568394, -0.52257586, -1.0583348, 0.62635255, -0.2772192, 0.23843738, -0.30540255, 0.1863141, 1286.0
    ]
}

- You can test the endpoint using the notebook given in the package.
- Alternatively, you can est the endpoint directly on the terminal (note: you can modify values of the sample data):
curl -X POST -H "Content-Type: application/json" -d '{"features": [118716.0, -0.39096448, -3.763199, -3.603844, 1.5876892, -0.47663704, -0.5617021, 2.1779633, -0.6973479, -0.018830955, -0.9399685, -0.35247976, 0.30234602, 0.7528182, -0.5717872, 0.4877511, 0.2844196, 0.6142388, 0.16805398, -0.70408744, 2.4774666, 0.77568394, -0.52257586, -1.0583348, 0.62635255, -0.2772192, 0.23843738, -0.30540255, 0.1863141, 1286.0]}' https://i9j9jpazs3.execute-api.us-east-2.amazonaws.com/predict

 
# Notes

- The package is compatible with AWS Free Tier