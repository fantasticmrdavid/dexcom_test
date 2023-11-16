import os
import boto3
import json
import time

from datetime import datetime, timezone, timedelta
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
readingsArray = []

last_reboot_time = datetime.now(timezone.utc)  # Initialize the last reboot time

while True:
    glucose_reading = dexcom.get_current_glucose_reading()
    if glucose_reading is not None :
        display = f'{glucose_reading.mmol_l} {glucose_reading.trend_arrow}'
        now = datetime.now(timezone.utc)  # Make now offset-aware

        # Create a timezone object for the local timezone
        local_timezone = timezone(datetime.now().astimezone().utcoffset())

        # Get the timezone offset and format it as a string
        timezone_offset = glucose_reading.datetime.strftime('%z')

        last_cgm_reading = glucose_reading.datetime.astimezone(timezone.utc)

        currentReading = {
            "reading": {
                "mmol_l": glucose_reading.mmol_l,
                "trend_arrow": glucose_reading.trend_arrow,
                "trend_description": glucose_reading.trend_description,
                "last_cgm_reading": last_cgm_reading.isoformat(),
                "last_push": now.strftime("%Y-%m-%d %H:%M:%S"),
            }
        }
        if len(readingsArray) > 0 :
            first = readingsArray[0]
            if glucose_reading.datetime.isoformat() != first["last_cgm_reading"] :
                readingsArray = [currentReading["reading"]] + readingsArray
        elif len(readingsArray) == 0 :
            readingsArray = [currentReading["reading"]]
        if len(readingsArray) > 12 :
            readingsArray = readingsArray[:12]

        writeOutput = {
            "readings": readingsArray
        }

        with open('readings.json', 'w') as outfile:
            json.dump(writeOutput, outfile)
        print(display)

        # Check if more than 30 minutes have elapsed since the last CGM reading
        elapsed_cgm_time = now - last_cgm_reading
        if elapsed_cgm_time > timedelta(minutes=30):
            print("More than 30 minutes since last CGM reading, rebooting...")
            os.system("sudo reboot")  # Adjust this command based on your OS

        # Check if more than a week has passed since the last reboot
        elapsed_week_time = now - last_reboot_time
        if elapsed_week_time > timedelta(weeks=1):
            print("Weekly system reboot...")
            os.system("sudo reboot")  # Adjust this command based on your OS
            last_reboot_time = now  # Update the last reboot time

        bucket.upload_file('readings.json', 'readings.json', ExtraArgs={'ACL':'public-read'})
    time.sleep(60)