import re
import json
import csv
import logging

def format_result_for_jsonl(raw_result: str) -> str:
    """
    Clean the raw text to extract multiple JSON objects, returning them 
    as newline-separated JSONL. 
    """
    matches = re.findall(r'\{.*?\}', raw_result, re.DOTALL)
    if not matches:
        raise ValueError("No valid JSON block found in the response.")

    # Join multiple JSON blocks, separate them by new lines
    json_content = "\n".join(matches).replace("\n\n", "\n")


    # Attempt to replace unquoted N/A with "N/A"
    corrected_json_content = re.sub(r'(?<!")\bN/A\b(?!")', '"N/A"', json_content)
    return corrected_json_content

def extract_low_result_json(raw_result: str) -> str:
    """
    Extract and return only the valid JSON from the input text.
    Removes any triple quotes or additional text around the JSON.
    """
    cleaned_result = raw_result.replace("'''json", "").strip()
    match = re.search(r'\{.*\}', cleaned_result, re.DOTALL)
    if not match:
        raise ValueError("No valid JSON structure found.")
    return match.group(0)

def jsonlist_to_csv(jsonl_list: list, output_file: str, logger: logging.Logger) -> None:
    """
    Convert a list of JSONL strings into a CSV file. 
    The columns are based on the keys of the first valid JSON object.
    """
    logger.info(f"Starting conversion of {len(jsonl_list)} JSONL strings to CSV: {output_file}")

    json_objects = []
    for index, jsonl_str in enumerate(jsonl_list):
        try:
            jsonl_str = jsonl_str.strip()
            parsed_obj = json.loads(jsonl_str)
            json_objects.append(parsed_obj)
            logger.debug(f"Successfully parsed JSONL at index {index}: {jsonl_str}")
        except json.JSONDecodeError as json_error:
            logger.error(f"JSON decoding error at index {index}: {json_error}")
        except Exception as e:
            logger.error(f"An unexpected error at index {index}: {e}")

    if not json_objects:
        logger.warning("No valid JSON objects to write. Aborting CSV creation.")
        return

    fieldnames = list(json_objects[0].keys())
    logger.info(f"Using fieldnames from the first JSON object: {fieldnames}")

    try:
        with open(output_file, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for obj in json_objects:
                writer.writerow(obj)
                logger.debug(f"Wrote row to CSV: {obj}")

        logger.info(f"CSV created successfully: {output_file}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during CSV writing: {e}")
