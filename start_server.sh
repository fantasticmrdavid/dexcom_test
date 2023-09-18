#!/bin/bash
python3 main.py &
npx json-server --watch readings.json -p 3001