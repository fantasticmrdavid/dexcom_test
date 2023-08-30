import os
import json
import time
username = os.environ["DEXCOM_USERNAME"]
password = os.environ["DEXCOM_PASSWORD"]

from pydexcom import Dexcom
dexcom = Dexcom(username, password, True)

while True:
    glucose_reading = dexcom.get_current_glucose_reading()
    display = f'{glucose_reading.mmol_l} {glucose_reading.trend_arrow}'
    with open('output.json', 'w') as outfile:
        json.dump(display, outfile)
    print(display)
    time.sleep(300)