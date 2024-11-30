import os
import requests
import json
import time
import boto3

from datetime import datetime, timezone, timedelta

nightscout_url = os.environ["NIGHTSCOUT_URL"]
# print(f"Nightscout URL: {nightscout_url}")  # Output the Nightscout URL on first read

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
previous_last_cgm_reading = None  # Initialize the previous last_cgm_reading

last_reboot_time = datetime.now(timezone.utc)  # Initialize the last reboot time

while True:
    response = requests.get(f"{nightscout_url}/api/v1/entries.json?count=1")
    if response.status_code == 200:
        glucose_data = response.json()[0]
        # Parse the datetime string correctly
        glucose_datetime = datetime.strptime(glucose_data["dateString"], "%Y-%m-%dT%H:%M:%S.%fZ").astimezone(timezone.utc)
        glucose_reading = {
            "mmol_l": glucose_data["sgv"] / 18.0,  # Convert mg/dL to mmol/L
            "trend_arrow": glucose_data["direction"],
            "trend_description": glucose_data["direction"],
            "datetime": glucose_datetime
        }
        display = f'{glucose_reading["mmol_l"]} {glucose_reading["trend_arrow"]}'
        now = datetime.now(timezone.utc)  # Make now offset-aware

        last_cgm_reading = glucose_reading["datetime"]

        # Compare with the previous last_cgm_reading
        if last_cgm_reading != previous_last_cgm_reading:
            currentReading = {
                "reading": {
                    "mmol_l": glucose_reading["mmol_l"],
                    "trend_arrow": glucose_reading["trend_arrow"],
                    "trend_description": glucose_reading["trend_description"],
                    "last_cgm_reading": last_cgm_reading.isoformat(),
                    "last_push": now.strftime("%Y-%m-%d %H:%M:%S"),
                }
            }
            if len(readingsArray) == 0:
                readingsArray = [currentReading["reading"]]
            else:
                readingsArray = [currentReading["reading"]] + readingsArray

            # Update the previous last_cgm_reading
            previous_last_cgm_reading = last_cgm_reading

        if len(readingsArray) > 12:
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
            os.system("sudo reboot -f")  # Adjust this command based on your OS

        # Check if more than a week has passed since the last reboot
        elapsed_week_time = now - last_reboot_time
        if elapsed_week_time > timedelta(weeks=1):
            print("Weekly system reboot...")
            os.system("sudo reboot -f")  # Adjust this command based on your OS
            last_reboot_time = now  # Update the last reboot time

        bucket.upload_file('readings.json', 'readings.json', ExtraArgs={'ACL': 'public-read'})
    else:
        print(f"Failed to fetch data: {response.status_code}, Response: {response.text}")  # Output the response if status code is not 200
    time.sleep(60)