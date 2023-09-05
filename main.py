import os
import boto3
import json
import time

from datetime import datetime
from pydexcom import Dexcom

username = os.environ["DEXCOM_USERNAME"]
password = os.environ["DEXCOM_PASSWORD"]
dexcom = Dexcom(username, password, True)

access_key_id = os.environ["AWS_S3_ACCESS_KEY"]
secret_key = os.environ["AWS_S3_SECRET"]
s3bucket = os.environ["AWS_S3_BUCKET"]

session = boto3.Session(
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_key,
)

s3 = session.resource("s3")
bucket = s3.Bucket(s3bucket)

while True:
    glucose_reading = dexcom.get_current_glucose_reading()
    display = f'{glucose_reading.mmol_l} {glucose_reading.trend_arrow}'
    now = datetime.now()
    writeOutput = {
        "reading": {
            "mmol_l": glucose_reading.mmol_l,
            "trend_arrow": glucose_reading.trend_arrow,
            "trend_description": glucose_reading.trend_description,
            "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
        }
    }
    with open('readings.json', 'w') as outfile:
        json.dump(writeOutput, outfile)
    print(display)
    bucket.upload_file('readings.json', 'readings.json', ExtraArgs={'ACL':'public-read'})
    time.sleep(150)