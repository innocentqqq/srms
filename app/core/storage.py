import boto3
import os
from botocore.exceptions import NoCredentialsError

S3_BUCKET = os.getenv("S3_BUCKET")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_ENDPOINT = os.getenv("S3_ENDPOINT")  # For R2 or other S3-compatible services

s3_client = boto3.client(
    "s3",
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    endpoint_url=S3_ENDPOINT
)

def upload_file_to_s3(file_path, object_name=None):
    if not S3_BUCKET:
        print("S3_BUCKET not configured. Skipping upload.")
        return file_path
    
    if object_name is None:
        object_name = os.path.basename(file_path)
    
    try:
        s3_client.upload_file(file_path, S3_BUCKET, object_name)
        # Assuming public read or presigned URLs will be used
        return f"https://{S3_BUCKET}.s3.amazonaws.com/{object_name}"
    except Exception as e:
        print(f"S3 upload error: {e}")
        return file_path

def get_s3_presigned_url(object_name, expiration=3600):
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': object_name},
            ExpiresIn=expiration
        )
        return response
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return None
