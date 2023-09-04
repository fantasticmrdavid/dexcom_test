#!/bin/bash
python3 main.py &
python3 uploader.py &
npx json-server --watch readings.json -p 3001