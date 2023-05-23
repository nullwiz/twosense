# Data Engineer Challenge

## Overview

We need to build out a REST API endpoint to collect location data from our mobile app.
We've built the skeleton of the API as a Flask application,
but we need your help to build out the data pipeline and database to store the data.

## Solution

We need you to build out the components necessary to process and store the data. Specifically:

* Build out the API according to the [requirements](#api-requirements) below.
* Build a data pipeline to resolve the [data issues](#data-issues) listed below.
* Build a database to store the data.
* Build a `docker-compose` file to run the API and database.
* Write tests for the solution as you see fit.

## Data Issues

The data collection on the mobile app is not perfect. We have a few issues we need to address:

1. The data is not always consistent. Some fields are missing, and some fields are in the wrong format.
   The API should return an error if the data is not in the correct format.
2. There are some duplicate records in the data. If multiple records are sent with the same `timestamp` and `user_id`,
   we are only interested in the first submitted record. We can assume that the data is sent in chronological order.
3. The rate of data collection is very high. We don't need to store every single record.
   We're only interested in storing the _simple average_ of the data at a one-minute resolution.
4. _**BONUS**:_ The `timestamp` field is in the local timezone of the user's device. We want to store the data in UTC.

## Deliverables

A .zip file containing:

* All code used to build the application
* `.git` folder
* Instructions on how to run the application
* If any, known limitations and/or future enhancements
* Any other relevant documentation

To help you get started, we've provided a skeleton Flask application in [/api/main.py](/api/main.py) and some basic
tests in [/tests](/tests).

### Real Data Simulation

To help you test your solution, we've included a simple [script](simulation/simulate.py) to simulate making calls to the
API with [real data](simulation/data).
Feel free to examine the data and get familiar with it.
To run the simulator:

```shell
API_HOST=http://localhost:5000 poetry run python simulation/simulate.py
```

Replace `http://localhost:5000` with the URL of your deployed API.

## API Requirements

The API has one endpoint (`PUT /location`) that receives one location datapoint at a time.

### Request Example

```json
{
  "timestamp": "2017-01-01 13:05:12",
  "lat": 40.701,
  "long": -73.916,
  "accuracy": 11.3000021,
  "speed": 1.3999992,
  "user_id": "a1"
}
```

### Response Codes

| Status Code | Description                       |
|-------------|-----------------------------------|
| 200         | The data was stored successfully. |
| 400         | Invalid or malformatted data.     |
| 500         | Any other unexpected errors.      |

## Dev Environment Setup

* [Install Poetry](https://python-poetry.org/docs/#installation)
* Run `poetry install`

## Finally

We expect this challenge to take about 3-4 hours to complete, but you have the full 48 hours available to you. We
welcome feedback if you felt like the challenge was too much or too little work for the expected or allotted timeframes.

If you can't get to completing all the tasks, walk us through how you would approach each one.
Even if you don't submit a complete solution, we're interested in your thought processes as well as working code.

**Please do NOT share any of the code/data from this challenge.**

Good luck!

Copyright (C) 2022 Twosense, Inc.