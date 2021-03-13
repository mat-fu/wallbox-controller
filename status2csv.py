import pandas as pd
import requests
import json
import csv

def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

token = "" #Insert your Cloud Token here
parameters_status = {
    "token": token
}

wb_status = requests.get("https://api.go-e.co/api_status", params=parameters_status).json()
jprint(wb_status)

wb_status_data = wb_status['data']
data_file = open('data_file_online.csv', 'w')
csv_writer = csv.writer(data_file)

csv_writer.writerow(wb_status_data.keys())
csv_writer.writerow(wb_status_data.values())
