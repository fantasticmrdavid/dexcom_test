import os
import json
import time

from datetime import datetime
from pydexcom import Dexcom

username = os.environ["DEXCOM_USERNAME"]
password = os.environ["DEXCOM_PASSWORD"]
dexcom = Dexcom(username, password, True)

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
    time.sleep(300)