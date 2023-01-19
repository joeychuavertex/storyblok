import os
import glob

import requests
import csv
import streamlit as st
from stqdm import stqdm
import pandas as pd
from datetime import datetime

api_key = st.text_input('API Key')

if api_key:
    api = requests.Session()
    api.headers.update({
        "authorization": api_key,
        "Content-Type": "application/json",
        "User-Agent": "API Explorer"
    })

    spaces = {
        'ISRAEL': st.secrets["ISRAEL"],
        'HEALTHCARE(NEW)': st.secrets["HEALTHCARENEW"],
        'GROWTH(NEW)': st.secrets["GROWTHNEW"],
        'CHINA(NEW)': st.secrets["CHINANEW"],
        'SEA(NEW)': st.secrets["SEANEW"],
        'US(NEW)': st.secrets["USNEW"]
    }

    for fund, id in stqdm(spaces.items()):

        print('Retrieving from', fund)

        # Set the base URL for the Management API endpoint
        base_url = f"https://app.storyblok.com/v1/spaces/{id}"

        # Perform a HEAD request to get the total number of activities from the Response Headers
        res = api.head(f"{base_url}/activities/?created_at_gte=&created_at_lte=&per_page=100&page=1")

        # Total number of activities from response header
        total = int(res.headers["total"])

        # Calculate the maximum amount of pages
        max_page = total // 100 + 1

        # Prepare all requests that needs to be sent in total to request all activities
        content_requests = []
        for page in range(1, max_page + 1):
            content_requests.append(
                api.get(f"{base_url}/activities/?created_at_gte=&created_at_lte=&per_page=100&page={page}"))

        # Execute all requests that we've prepared before
        responses = []
        for r in content_requests:
            responses.append(r.json())

        # Flatten the JSON responses and add to a list
        flat_data = []
        for response in responses:
            for activity in response["activities"]:
                flat_activity = {}
                for key, value in activity.items():
                    if isinstance(value, dict):
                        for nested_key, nested_value in value.items():
                            flat_activity[key + "." + nested_key] = nested_value
                    else:
                        flat_activity[key] = value
                flat_data.append(flat_activity)

        # Get all fields of one object so we can define the header of the CSV
        fields = list(flat_data[0].keys())

        csvfilename = fund + '-' + str(datetime.today().strftime('%Y-%m-%d'))

        # Write the CSV file
        with open(csvfilename + '.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()
            for row in flat_data:
                try:
                    writer.writerow(row)
                except:
                    continue

        path = os.getcwd()
        st.write(pd.read_csv(path))
        st.download_button(
            label=f"Download {csv} as CSV",
            data=csvfile,
            file_name='file.csv',
            mime='text/csv',
        )


