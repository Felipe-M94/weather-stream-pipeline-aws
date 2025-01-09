import json
import requests
import boto3
import os

# Config API
latitude = -29.6846
longitude = -51.1419
TOMORROW_API_KEY = os.getenv("TOMORROW_API_KEY")
url = f"https://api.tomorrow.io/v4/weather/realtime?location={latitude},{longitude}&apikey={TOMORROW_API_KEY}"
headers = {"Accept": "application/json"}

# Config Kinesis
STREAM_NAME = os.getenv("STREAM_NAME")
REGION = os.getenv("REGION")

# Client Kinesis
kinesis = boto3.client("kinesis", region_name=REGION)


# Get data from API
def lambda_handler(event, context):
    response = requests.get(url, headers=headers)
    data = response.json()

    # Put data in Kinesis
    response = kinesis.put_record(
        StreamName=STREAM_NAME, Data=json.dumps(data), PartitionKey="partitionkey"
    )

    return {
        "statusCode": 200,
        "body": json.dumps("Dados enviados ao Kinesis, com sucesso!"),
    }
