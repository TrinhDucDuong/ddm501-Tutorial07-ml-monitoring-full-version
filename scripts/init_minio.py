"""Idempotently create the private MLflow artifact bucket."""
import os
import boto3
from botocore.exceptions import ClientError

client = boto3.client("s3", endpoint_url=os.getenv("MLFLOW_S3_ENDPOINT_URL", "http://minio:9000"))
bucket = "mlflow-artifacts"
try:
    client.head_bucket(Bucket=bucket)
except ClientError as error:
    if error.response["ResponseMetadata"]["HTTPStatusCode"] != 404:
        raise
    client.create_bucket(Bucket=bucket)
print("MLflow artifact bucket ready")
