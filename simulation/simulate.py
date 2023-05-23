"""Simulate sending location data to the API."""
import os
from pathlib import Path

import pandas as pd
import requests
from pandas import Series, DataFrame
from datetime import datetime

DATA_DIR = Path(__file__).parent / 'data'

API_HOST = os.environ.get('API_HOST')
assert API_HOST, "API_HOST is not set"


def main():
    """Run the simulation."""
    location_data = read_user_data()
    # Take elapsed time
    start_time = datetime.now()
    print("Sending location data to API...")
    for _, row in location_data.iterrows():
        send_to_api(row)
    end_time = datetime.now()

    print("DONE!")
    print("Elapsed time: ", end_time - start_time)


def read_user_data() -> DataFrame:
    print("Reading user data...")
    user_dataframes = []
    for file in DATA_DIR.glob('*.csv'):
        user_dataframes.append(pd.read_csv(file))
    data = pd.concat(user_dataframes)

    return data.sort_values(by='timestamp')


def send_to_api(row: Series):
    response = requests.put(F"{API_HOST}/location", json=row.to_dict())
    assert response.status_code == 200, response.text


if __name__ == '__main__':
    main()
