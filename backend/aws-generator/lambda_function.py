import json
import boto3
from datetime import datetime
import os
from generators import (
    generate_csv_from_theme_low_quality,
    generate_csv_from_theme_high_quality,
    generate_csv_from_theme_internet,
    traducir_texto,
)

import logging

# Configure logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize S3 client
s3_client = boto3.client("s3")


def upload_to_s3(local_file_path, bucket_name, s3_file_name):
    """
    Uploads a file to S3 and generates a pre-signed URL.
    """
    try:
        # Upload the file
        s3_client.upload_file(local_file_path, bucket_name, s3_file_name)
        
        # Generate a pre-signed URL valid for 1 hour
        pre_signed_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': s3_file_name},
            ExpiresIn=3600  # 1 hour in seconds
        )
        
        return pre_signed_url
    except Exception as e:
        logger.error(f"Failed to upload file to S3: {e}")
        raise Exception(f"Failed to upload file to S3: {e}")


def validate_inputs(body):
    """
    Validates input parameters from the event body.
    """
    generator_type = body.get("generator_type", "").lower()
    if generator_type not in ["merlin", "gold", "premium", "oracle"]:
        raise ValueError(f"Invalid generator type: {generator_type}")

    rows = int(body.get("rows", 100))
    if rows < 1:
        raise ValueError("Number of rows must be greater than 0.")

    theme = body.get("theme", "Default theme").strip()
    if not theme:
        raise ValueError("Theme cannot be empty.")

    return generator_type, theme, rows


def lambda_handler(event, context):
    """
    Lambda handler to process requests and generate CSV files.
    """
    try:
        # Parse input
        body = json.loads(event["body"])

        # Validate inputs
        generator_type, theme, rows = validate_inputs(body)

        # Optionally translate the theme
        translated_theme = traducir_texto(theme)
        logger.info(f"Translated theme: {translated_theme}")

        # Generate timestamped filename based on generator type
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        bucket_name = "datapground-generated-files"

        if generator_type == "merlin":
            local_filename = f"/tmp/synthetic_data_low_{timestamp}.csv"
            s3_file_name = f"synthetic_data_low_{timestamp}.csv"
            logger.info(f"Using file name: {local_filename}")
            generate_csv_from_theme_low_quality(translated_theme, rows=rows, file_name=local_filename)
        elif generator_type == "gold":
            local_filename = f"/tmp/synthetic_data_high_{timestamp}.csv"
            s3_file_name = f"synthetic_data_high_{timestamp}.csv"
            logger.info(f"Using file name: {local_filename}")
            generate_csv_from_theme_high_quality(translated_theme, rows=rows, filename=local_filename)
        elif generator_type == "premium":
            local_filename = f"/tmp/synthetic_data_high_{timestamp}.csv"
            s3_file_name = f"synthetic_data_high_{timestamp}.csv"
            logger.info(f"Using file name: {local_filename}")
            generate_csv_from_theme_high_quality(
                translated_theme, rows=rows, pro=True, filename=local_filename
            )
        elif generator_type == "oracle":
            local_filename = f"/tmp/synthetic_data_high_internet_{timestamp}.csv"
            s3_file_name = f"synthetic_data_high_internet_{timestamp}.csv"
            logger.info(f"Using file name: {local_filename}")
            generate_csv_from_theme_internet(translated_theme, rows=rows, filename=local_filename)

        # Validate file creation
        if not os.path.exists(local_filename):
            raise Exception(f"File {local_filename} was not created.")

        # Upload to S3 and get pre-signed URL
        pre_signed_url = upload_to_s3(local_filename, bucket_name, s3_file_name)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "File generated successfully.",
                "s3_path": f"s3://{bucket_name}/{s3_file_name}",
                "download_url": pre_signed_url
            }),
        }

    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(ve)}),
        }
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }
