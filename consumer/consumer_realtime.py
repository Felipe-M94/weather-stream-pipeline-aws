import json
import base64
import os
import boto3

sns_client = boto3.client("sns")

SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")

PRECIPITATION_PROBABILITY_THRESHOLD = int(
    os.getenv("PRECIPITATION_PROBABILITY_THRESHOLD", 10)
)
WIND_SPEED_THRESHOLD = int(os.getenv("WIND_SPEED_THRESHOLD", 10))
WIND_GUST_THRESHOLD = int(os.getenv("WIND_GUST_THRESHOLD", 10))
RAIN_INTENSITY_THRESHOLD = int(os.getenv("RAIN_INTENSITY_THRESHOLD", 10))


def lambda_handler(event, context):
    if "Records" not in event:
        return {"statusCode": 400, "body": json.dumps("No records found in event")}

    for record in event["Records"]:
        payload = base64.b64decode(record["kinesis"]["data"]).decode("utf-8")
        data = json.loads(payload)

        precipitation_probability = data["data"]["values"].get(
            "precipitationProbability", 0
        )
        wind_speed = data["data"]["values"].get("windSpeed", 0)
        wind_gust = data["data"]["values"].get("windGust", 0)
        rain_intensity = data["data"]["values"].get("rainIntensity", 0)

        if (
            precipitation_probability >= PRECIPITATION_PROBABILITY_THRESHOLD
            or wind_speed >= WIND_SPEED_THRESHOLD
            or wind_gust >= WIND_GUST_THRESHOLD
            or rain_intensity >= RAIN_INTENSITY_THRESHOLD
        ):

            message = (
                f"Condições climáticas adversas detectadas:\n"
                f"Probabilidade de chuva: {precipitation_probability}%\n"
                f"Velocidade do vento: {wind_speed} m/s\n"
                f"Rajada de vento: {wind_gust} m/s\n"
                f"Intensidade da chuva: {rain_intensity} mm/h"
            )

            response = sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=message,
                Subject="Alerta de condições climáticas adversas",
            )

            print(f"Alerta enviado: {response}")

    return {"statusCode": 200, "body": json.dumps("Alertas enviados com sucesso!")}
