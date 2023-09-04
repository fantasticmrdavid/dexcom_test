import os
import boto3

access_key_id = os.environ["AWS_S3_ACCESS_KEY"]
secret_key = os.environ["AWS_S3_SECRET"]
s3bucket = os.environ["AWS_S3_BUCKET"]

session = boto3.Session(
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_key,
)

s3 = session.resource("s3")
bucket = s3.Bucket(s3bucket)
bucket.upload_file('readings.json', 'readings.json', ExtraArgs={'ACL':'public-read'})