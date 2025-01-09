from calendar import month
import json
import boto3
import base64
import os
from datetime import datetime

s3_client = boto3.client("s3")

BUCKET_NAME = os.getenv("BUCKET_NAME")


def lambda_handler(event, context):
    for record in event["Records"]:
        # Get data from Kinesis
        payload = base64.b64decode(record["kinesis"]["data"]).decode("utf-8")
        data = json.loads(payload)

        # Get current date
        now = datetime.now()
        year = now.year
        month = now.month
        day = now.day

        # Create path in S3
        file_name = f"raw/year={year}/month={month}/day={day}/weather_data_{now.isoformat()}.json"

        # Save data in S3
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=file_name,
            Body=json.dumps(data),
        )

        return {
            "statusCode": 200,
            "body": json.dumps("Dados salvos no S3, com sucesso!"),
        }
