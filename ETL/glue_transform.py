import sys
import boto3
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import col, year, month, dayofmonth

args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Init Parameters
input_database = ""
output_path = ""

glue_client = boto3.client("glue")

tables = glue_client.get_tables(DatabaseName=input_database)["TableList"]

for table in tables:
    table_name = table["Name"]

    datasource = glueContext.create_dynamic_frame.from_catalog(
        database=input_database, table_name=table_name, transformation_ctx="datasource"
    )

    df = datasource.toDF()

    # Extract year, month, and day from the timestamp
    flattened_df = df.select(
        col("data.time").alias("time"),
        col("data.values.cloudBase").alias("cloudBase"),
        col("data.values.cloudCeiling").alias("cloudCeiling"),
        col("data.values.cloudCover").alias("cloudCover"),
        col("data.values.dewPoint").alias("dewPoint"),
        col("data.values.freezingRainIntensity").alias("freezingRainIntensity"),
        col("data.values.humidity").alias("humidity"),
        col("data.values.precipitationProbability").alias("precipitationProbability"),
        col("data.values.pressureSurfaceLevel").alias("pressureSurfaceLevel"),
        col("data.values.rainIntensity").alias("rainIntensity"),
        col("data.values.sleetIntensity").alias("sleetIntensity"),
        col("data.values.snowIntensity").alias("snowIntensity"),
        col("data.values.temperature").alias("temperature"),
        col("data.values.temperatureApparent").alias("temperatureApparent"),
        col("data.values.uvHealthConcern").alias("uvHealthConcern"),
        col("data.values.uvIndex").alias("uvIndex"),
        col("data.values.visibility").alias("visibility"),
        col("data.values.weatherCode").alias("weatherCode"),
        col("data.values.windDirection").alias("windDirection"),
        col("data.values.windGust").alias("windGust"),
        col("data.values.windSpeed").alias("windSpeed"),
        col("location.lat").alias("latitude"),
        col("location.lon").alias("longitude"),
    )

    flattened_df = flattened_df.withColumn("year", year(flattened_df["time"]))
    flattened_df = flattened_df.withColumn("month", month(flattened_df["time"]))
    flattened_df = flattened_df.withColumn("day", dayofmonth(flattened_df["time"]))

    dynamic_frame = DynamicFrame.fromDF(flattened_df, glueContext, "dynamic_frame")

    # Write data to S3 from parquet format
    glueContext.write_dynamic_frame.from_options(
        frame=dynamic_frame,
        connection_type="s3",
        connection_options={"path": f"{output_path}/{table_name}"},
        format="parquet",
    )

    job.commit()
