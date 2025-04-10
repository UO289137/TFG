import pandas as pd
from openai import OpenAI
from faker import Faker
from nltk.corpus import names
from deep_translator import GoogleTranslator

import datetime
import os
import json
import random
import pycountry
import subprocess
import re
import requests
import csv
import tiktoken
import logging
import nltk
import numpy as np

#nltk.download('names')

nltk.data.path.append('/var/task/nltk_data')

# 1. Configure the logger.
logging.basicConfig(
    level=logging.DEBUG,  # Nivel de registro (puede ser DEBUG, INFO, WARNING, ERROR, CRITICAL). Los niveles por debajo no se registrarán.
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Formato del log
    filename='app.log',  # Archivo donde se guardarán los logs (si se desea log a un archivo)
    filemode='a'  # 'w' para sobrescribir el archivo cada vez o 'a' para añadir al log existente
)

# 2. Crear el logger (opcional: especificar un nombre)
logger = logging.getLogger('logger_dpg')

def chat_openai(message, model_name="gpt-4o-mini"):
    logger.info(f"chat_openai called with message: '{message}' and model: '{model_name}'")
    
    try:
        # Initialize OpenAI client
        client = OpenAI()  # Automatically sets up the API key
        logger.debug("OpenAI client successfully initialized.")

        if model_name == "gpt-4o-mini":
            messages_openai=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message}
            ]
        elif model_name == "o1-mini":
            messages_openai=[
                {"role": "user", "content": message}
            ]
        # Make API call to OpenAI
        logger.info("Sending request to OpenAI API...")
        completion = client.chat.completions.create(
            model=model_name,
            messages= messages_openai
        )
        
        # Extract and log the response
        response = completion.choices[0].message.content
        logger.info(f"Response received: {response}")

        return response
    except Exception as e:
        # Handle and log any exception
        error_message = "Error: Unable to get a response from the OpenAI model."
        logger.error(f"{error_message} Exception: {e}")
        logger.info(f"Returning default error message: {error_message}")
        return error_message


def chat_fireworks(message):
    logger.info(f"chat_fireworks called with message: '{message}'")
    
    url = "https://api.fireworks.ai/inference/v1/chat/completions"

    payload = {
        "model": "accounts/fireworks/models/llama-v3p1-405b-instruct",
        "max_tokens": 16384,  # Default is 4096
        "top_p": 1,  # Default is 1
        "top_k": 40,  # Default is 40. Lower value reduces the pool of words to select from.
        "presence_penalty": 0,  # Default is 0. Penalizes previously mentioned themes.
        "frequency_penalty": 0,  # Default is 0. Penalizes frequent word repetition.
        "temperature": 0.6,  # Default is 0.6. Higher value increases variability in word selection.
        "messages": [
            {"role": "user", "content": message}
        ]
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f'Bearer {os.getenv("FIREWORKS_API_KEY")}'
    }

    try:
        # Make the API request
        logger.info("Sending request to Fireworks AI API...")
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors
        logger.info("Response received from Fireworks API.")

        # Convert response to JSON
        response_json = response.json()
        logger.debug(f"Raw response JSON: {response_json}")

        # Extract the response message
        result = response_json["choices"][0]["message"]["content"]
        logger.info(f"Extracted message: {result}")

        return result

    except requests.exceptions.RequestException as e:
        # Log the error
        error_message = "Error: Unable to get a response from the Fireworks AI model."
        logger.error(f"{error_message} Exception: {e}")
        logger.info(f"Returning default error message: {error_message}")
        return error_message

    except json.JSONDecodeError as e:
        # Log JSON decoding errors
        error_message = "Error: Failed to parse the response from the Fireworks AI API."
        logger.error(f"{error_message} Exception: {e}")
        logger.info(f"Returning default error message: {error_message}")
        return error_message
        
def chat_perplexity(message):
    logger.info(f"chat_perplexity called with message: '{message}'")
    
    url = "https://api.perplexity.ai/chat/completions"

    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": "Do what I ask you to do, no extra explanations. Attend to the formats I ask for in the response."
            },
            {
                "role": "user",
                "content": message
            }
        ],
        "max_tokens": None,
        "temperature": 0.2,
        "top_p": 0.9,
        "return_citations": True,
        "search_domain_filter": [],
        "return_images": False,
        "return_related_questions": False,
        "search_recency_filter": "day",
        "top_k": 0,
        "stream": False,
        "presence_penalty": 0,
        "frequency_penalty": 1
    }

    headers = {
        "Authorization": f'Bearer {os.getenv("PERPLEXITY_API_KEY")}',
        "Content-Type": "application/json"
    }

    try:
        # Make the API request
        logger.info("Sending request to Perplexity API...")
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        logger.info("Response received from Perplexity API.")

        # Convert response to JSON
        response_json = response.json()
        logger.debug(f"Raw response JSON: {response_json}")

        # Extract the response message
        result = response_json["choices"][0]["message"]["content"]
        logger.info(f"Extracted message: {result}")

        return result

    except requests.exceptions.RequestException as e:
        # Log the error
        error_message = "Error: Unable to get a response from the Perplexity AI model."
        logger.error(f"{error_message} Exception: {e}")
        logger.info(f"Returning default error message: {error_message}")
        return error_message

    except json.JSONDecodeError as e:
        # Log JSON decoding errors
        error_message = "Error: Failed to parse the response from the Perplexity AI API."
        logger.error(f"{error_message} Exception: {e}")
        logger.info(f"Returning default error message: {error_message}")
        return error_message
    
def chat_deepseek(message):

    client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": f"{message}"},
        ],
        max_tokens = 8192,
        stream=False
    )

    return response.choices[0].message.content


def count_tokens(message, model = "gpt-4o-mini"):
    # Load the encoding for the model you're using
    # For example, using the 'gpt-3.5-turbo' or 'gpt-4' encoding
    encoding = tiktoken.encoding_for_model(model)

    # Define your input string
    input_string = message

    # Encode the string and count the tokens
    tokens = encoding.encode(input_string)
    num_tokens = len(tokens)

    print(f"The string has {num_tokens} tokens.")
    
name_list = set(name.lower() for name in names.words())

def traducir_texto(text, target_language="en"):
    """
    Translate the given text to the target language using deep-translator.
    """
    logger.info(f"translate_text called with input: '{text}'")
    try:
        translator = GoogleTranslator(source='auto', target=target_language)
        translated_text = translator.translate(text)
        logger.info(f"Translation successful: '{translated_text}'")
        return str(translated_text)
    except Exception as e:
        error_message = f"Translation failed: {str(e)}"
        logger.error(error_message)
        return error_message

def is_name(string):
    return string.lower() in name_list
    
def is_id(column_name):
    return column_name.lower() == 'id' or column_name.lower().endswith("_id") or column_name.lower().startswith("id_") or (column_name.endswith("Id") and len(column_name)>2 and column_name[-3].islower()) or ((column_name.startswith("Id") or column_name.startswith("id")) and len(column_name) > 2 and column_name[2].isupper())
    
def is_country(nombre):
    english_name = traducir_texto(nombre)
    try:
        # Intenta buscar el país por nombre
        pais = pycountry.countries.lookup(english_name)
        return True
    except LookupError:
        return False
    
# Obtén todos los países disponibles en pycountry
paises = list(pycountry.countries)

def generate_country():
    # Selecciona un país aleatorio
    pais_aleatorio = random.choice(paises)
    pais_aleatorio = pais_aleatorio.name.replace('"','')
    return pais_aleatorio
    
def generate_ids(cadena, max_val):
    # Verificar si la cadena contiene solo dígitos
    if cadena.isdigit():
        # Generar secuencia numérica desde 0 hasta max_val
        return [str(i).zfill(len(cadena)) for i in range(1, max_val + 1)]
    
    # Buscar todas las partes de la cadena (letras + dígitos)
    match = re.search(r'(\D*)(\d+)(\D*)', cadena)
    
    if match:
        # Partes antes, durante y después de los dígitos
        parte_inicial = match.group(1)  # Parte antes de los dígitos (puede estar vacía)
        numero = int(match.group(2))    # Parte numérica inicial
        parte_final = match.group(3)    # Parte después de los dígitos (puede estar vacía)
    else:
        # Si no hay dígitos, devolver la cadena como está
        return [cadena]
    
    # Generar nuevas cadenas incrementando el número hasta el máximo valor
    resultado = [f"{parte_inicial}{str(i).zfill(len(match.group(2)))}{parte_final}" for i in range(1, max_val + 1)]
    
    return resultado
    
def generate_data(config, names_variety, countries_variety, num_rows, filename):
    
    # Initialize the Faker library
    fake = Faker()

    data = {}

    # Iterate through the columns in the configuration dictionary
    for column_name, properties in config['columns'].items():
        if properties['type'] == 'string':
            values = [value.split(" ")[0] for value in properties['values']]
            name_count = sum(1 for value in values if is_name(value))

            country_count = sum(1 for value in properties['values'] if is_country(value))

            # La mitad
            threshold = 0.5 

            # Cantidad total
            total_amount = len(properties['values'])

            if  names_variety and (name_count/total_amount) >= threshold:
                # Generar nombres aleatorios
                data[column_name] = [fake.name() for _ in range(num_rows)]
            elif countries_variety and (country_count/total_amount) >= threshold:
                # Generar nombres de paises aleatorios
                data[column_name] = [generate_country() for _ in range(num_rows)]
            # Verificar si el nombre de la columna es id, Id, ID o finaliza o comienza por "_id", "_Id", "_ID", o "ID_", "Id_" o "id_" o IdX o xxxxId
            elif is_id(column_name):
                data[column_name] = generate_ids(properties['values'][0], num_rows)
            else:
                # Generar cadenas aleatorias a partir de los valores proporcionados
                data[column_name] = [random.choice(properties['values']) for _ in range(num_rows)]

        elif properties['type'] == 'int':

            if is_id(column_name):
                data[column_name] = generate_ids('0', num_rows)
            else:
                # Generate random integers within the provided range
                data[column_name] = [random.randint(properties['min'], properties['max']) for _ in range(num_rows)]

        elif properties['type'] == 'float':
            # Generate random floats within the provided range
            data[column_name] = [round(random.uniform(properties['min'], properties['max']), 2) for _ in range(num_rows)]

        elif properties['type'] == 'boolean':
            # Generate random boolean values (True/False)
            data[column_name] = [random.choice([True, False]) for _ in range(num_rows)]

        elif properties['type'] == 'date':
            # Generate random dates within the provided range
            start_date = datetime.datetime.strptime(properties['start'], '%Y-%m-%d')
            end_date = datetime.datetime.strptime(properties['end'], '%Y-%m-%d')
            data[column_name] = [fake.date_between(start_date=start_date, end_date=end_date) for _ in range(num_rows)]

    # Create a DataFrame from the generated data
    df = pd.DataFrame(data)

    # Store file in ficheros
    # filename = "ficheros/" + filename

    # For lambda function Store file in tmp
    # if not filename.startswith("/tmp/"):
    filename = filename

    # Save the DataFrame to a CSV file
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    
def test_appropriate_dict(config_dict):
    # Iterar sobre las columnas en el diccionario de configuración
    for column_name, properties in config_dict.get('columns', {}).items():
        # Validación para el tipo 'string'
        if properties.get('type') == 'string':
            # Si no hay una lista de 'values' o está vacía, devuelve False
            if not properties.get('values'):
                return False

        # Validación para el tipo 'int'
        elif properties.get('type') == 'int':
            # Comprueba que 'min' y 'max' existan
            if 'min' not in properties or 'max' not in properties:
                return False

        # Validación para el tipo 'float'
        elif properties.get('type') == 'float':
            # Comprueba que 'min' y 'max' existan
            if 'min' not in properties or 'max' not in properties:
                return False

        # Validación para el tipo 'date'
        elif properties.get('type') == 'date':
            # Comprueba que 'start' y 'end' existan
            if 'start' not in properties or 'end' not in properties:
                return False

        # Si el tipo no coincide con ninguno de los especificados, devuelve False
        elif properties.get('type') == 'boolean':
            continue

    # Si todas las validaciones pasan, devuelve True
    return True

def format_result(result):
    """Limpia el resultado para que contenga únicamente entradas JSON separadas por un salto de línea.
    Ignora todo el texto anterior al primer '{' y elimina los saltos de línea dobles.
    """
    # Busca múltiples bloques JSON separados
    matches = re.findall(r'\{.*?\}', result, re.DOTALL)  # .*? para encontrar múltiples bloques sin ser greedy
    
    if matches:
        # Une múltiples bloques JSON en un solo string con salto de línea entre ellos
        json_content = "\n".join(matches).replace("\n\n", "\n")  # Asegura que no haya saltos de línea dobles
        
        # Reemplaza 'N/A' no precedido y no seguido por comillas dobles
        corrected_json_content = re.sub(r'(?<!")\bN/A\b(?!")', '"N/A"', json_content)
        
        return corrected_json_content
    else:
        raise ValueError("No se encontró un bloque JSON válido en el resultado.")

def format_low_result(result):
    """Extracts and returns only the valid JSON format from the input text.
    It removes any occurrence of `'''json` and any additional text before or after the JSON block.
    """
    # Remove the '''json part if it exists
    cleaned_result = result.replace("'''json", "").strip()
    
    # Use regular expression to find and extract the JSON block
    match = re.search(r'\{.*\}', cleaned_result, re.DOTALL)  # Extract content between '{' and '}'
    
    if match:
        # Return the valid JSON part only
        json_content = match.group(0)
        return json_content
    else:
        # If no valid JSON found, raise an error
        raise ValueError("No valid JSON format found in the input.")
        
def contar_lineas_csv(archivo_csv):
    try:
        df = pd.read_csv(archivo_csv)
        return len(df)
    except Exception:
        return 0
        
def jsonlist_to_csv(jsonl_list, output_file):
    """
    Converts a list of JSONL strings into a CSV file with the columns in the order of the first JSONL object.
    
    Parameters:
        jsonl_list (list): A list of JSONL strings.
        output_file (str): The path to the output CSV file.
    """
    logger.info(f"Starting conversion of {len(jsonl_list)} JSONL strings to CSV file: '{output_file}'.")
    
    # Parse the JSONL strings into Python dictionaries
    json_objects = []

    for index, jsonl in enumerate(jsonl_list):
        # Process the JSONL
        json_loaded = jsonl.strip()  # Remove leading/trailing whitespace

        try:
            # Attempt to parse the JSON
            json_objects.append(json.loads(json_loaded)) 
            logger.debug(f"Successfully parsed JSONL at index {index}: {json_loaded}")
        except json.JSONDecodeError as json_error:
            logger.error(f"JSON decoding error at index {index}: {json_error}. Input: {json_loaded}")
        except Exception as e:
            logger.error(f"An unexpected error occurred at index {index}: {e}. Input: {json_loaded}")

    # Check if there are any valid JSON objects to write to CSV
    if not json_objects:
        logger.warning("No valid JSONL objects to process. Conversion aborted.")
        return

    # Get fieldnames from the first JSON object to preserve order
    fieldnames = list(json_objects[0].keys())
    logger.info(f"Using fieldnames from the first JSON object: {fieldnames}")

    # Write to CSV
    try:
        with open(output_file, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            # Write header
            writer.writeheader()

            # Write each row (JSON object) to the CSV
            for obj in json_objects:
                writer.writerow(obj)
                logger.debug(f"Wrote row to CSV: {obj}")

        logger.info(f"CSV conversion successful. Output file: '{output_file}'.")

    except IOError as io_error:
        logger.error(f"IO error occurred while writing to '{output_file}': {io_error}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during CSV writing: {e}")
json_example = {
    "columns": {
        "name": {
            "type": "string",
            "values": ["Alice", "Bob", "Charlie", "David", "Eve"]
        },
        "age": {
            "type": "int",
            "min": 18,
            "max": 65
        },
        "salary": {
            "type": "float",
            "min": 30000,
            "max": 120000
        },
        "is_manager": {
            "type": "boolean"
        },
        "hire_date": {
            "type": "date",
            "start": "2010-01-01",
            "end": "2023-12-31"
        }
    }
}

def create_response_final(theme, num_columns):
    # Call chat_openai to get the JSON response
    logger.info("Requesting JSON format from OpenAI.")
    response_chat = chat_openai(
        f"""Please only provide a valid JSON format based on the following example in your response:

        {json_example}

        Ensure the following:
        - Create a JSON similar to the example, themed around {theme}.
        - Maintain the specified fields associated with each type in the JSON structure.
        - The generated fields should be independent and not dependent on each other.
        - Include {num_columns} columns of data in the output."""
    )

    # Format the result:
    response_chat = format_low_result(response_chat)
    
    # Parse the response to a Python dictionary
    logger.info("Parsing the JSON response.")
    response_final = json.loads(response_chat)
    
    # Validate the format of the dictionary
    logger.info("Validating the format of the generated JSON.")
    return response_final

def ensure_directory_exists(filepath):
    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Directory created: {directory}")

def generate_csv_from_theme_low_quality(theme, variated_names=True, variated_countries=True, rows=1000, num_columns=10, file_name="/tmp/synthetic_data_low.csv"):
    logger.info(f"Starting CSV generation for theme: '{theme}' with {num_columns} columns and {rows} rows.")
    try:
        logger.info(f"Initial file name: {file_name}")
        
        # Ensure the directory exists
        ensure_directory_exists(file_name)

        response_final = create_response_final(theme, num_columns)

        tries = 2
        while not test_appropriate_dict(response_final) and tries > 0:
            tries -= 1
            response_final = create_response_final(theme, num_columns)

        logger.info("Generating data based on the provided configuration.")
        generate_data(response_final, variated_names, variated_countries, rows, filename=file_name)

        logger.info(f"CSV generation successful. Output file: '{file_name}'.")
        return file_name
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise

def generate_csv_from_theme_high_quality(theme, rows=50, pro=False, filename="/tmp/synthetic_data_high.csv"):
    logger.info(f"Starting CSV generation for theme: '{theme}' with {rows} rows (Pro model: {pro}).")

    #CONSTANTS
    MAX_PRO_ROWS = 50 # Maximum output rows for the Elixir Generator. The pro version of this function.
    MAX_NOT_PRO_ROWS = 200 # Maximum output rows for the Gold Generator. The non-pro version of this function.
    MINIMUM_ROWS = 1 # Minimum rows that have to be generated by the generator.

    # Validate input
    if rows < MINIMUM_ROWS:
        error_message = "Negative or 0 rows are not allowed."
        logger.error("error_message")
        logger.info(f"Returning default error message: {error_message}")
        return error_message
    elif (pro and rows > MAX_PRO_ROWS) or (not pro and rows > MAX_NOT_PRO_ROWS):
        error_message = "Row limit exceeded. Max 200 for non-pro model or 300 for pro model."
        logger.error(error_message)
        logger.info(f"Returning default error message: {error_message}")
        return error_message

    try:
        ensure_directory_exists(filename)

        prompt = (
            f"""Generate {rows} valid, newline-separated JSONL entries about: {theme}. 
            Use real-world data whenever possible. Only make up details if no real data is available.
            Ensure each entry has a unique 'id' field, unless in the theme you are asked not to do so.
            Make sure all entries have the exact same fields. Each entry should be on its own line, separated by a newline character."""
        )
        logger.info("Requesting JSON format from OpenAI.")
        result = chat_openai(prompt) if not pro else chat_deepseek(prompt)
        result = format_result(result)

        jsonl_entries = result.split("\n")
        logger.info(f"Generated {len(jsonl_entries)} JSONL entries.")
        jsonlist_to_csv(jsonl_entries, filename)

        row_count = contar_lineas_csv(filename)
        logger.info(f"Row count in generated CSV: {row_count}")
        if row_count < rows * 0.75:
            raise Exception("Generated CSV does not meet the minimum row requirement.")
        
        logger.info(f"CSV generation successful. Output file: '{filename}'.")
        return filename
    except Exception as e:
        logger.error(f"An error occurred during CSV generation: {e}")
        raise

def generate_csv_from_theme_internet(theme, filename="/tmp/synthetic_data_high_internet.csv", rows=20):
    """
    Generate a CSV file with synthetic data based on a specified theme using internet sources.
    
    Parameters:
        theme (str): The theme to base the data generation on.
        filename (str): The name of the output CSV file.
        rows (int): The number of rows to generate (default: 20).
    
    Returns:
        str: The filename of the generated CSV.
    """
    logger.info(f"Starting CSV generation for theme: '{theme}' with {rows} rows.")
    
    MIN_ROWS = 1
    MAX_ROWS = 50

    try:
        # Ensure the directory for the output file exists
        ensure_directory_exists(filename)

        # Validate input rows
        if rows < MIN_ROWS:
            raise ValueError(f"Number of rows must be greater than {MIN_ROWS}.")
        elif rows > MAX_ROWS:
            raise ValueError(f"Row limit exceeded. Maximum allowed rows: {MAX_ROWS}.")

        # Construct the prompt for the external API
        prompt = (
            f"Generate {rows} valid, newline-separated JSONL entries about: {theme}. "
            f"Each entry should have consistent fields and unique IDs."
        )
        logger.info("Requesting JSON format from external API.")

        # Request data from the external API
        try:
            response = chat_perplexity(prompt)
        except Exception as api_error:
            logger.error(f"Error while fetching data from the external API: {api_error}")
            raise

        # Format and process the response
        response = format_result(response)
        jsonl_entries = response.split("\n")
        logger.info(f"Generated {len(jsonl_entries)} JSONL entries.")

        # Convert the JSONL entries to a CSV file
        jsonlist_to_csv(jsonl_entries, filename)

        # Validate the row count in the generated CSV
        row_count = contar_lineas_csv(filename)
        if row_count < rows * 0.75:
            raise ValueError(
                f"Generated CSV does not meet the minimum row requirement. "
                f"Expected at least {rows * 0.75} rows, but got {row_count} rows."
            )

        logger.info(f"CSV generation successful. Output file: '{filename}'.")
        return filename

    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise
        
#generate_csv_from_theme_low_quality("Generate a dataset about AWS services with the fields: name, time, price.", rows=1000) # 23s
#generate_csv_from_theme_high_quality("Generate entries from a company with the fields: salary, deparment and hire_date. It is important that these are related between each other. Before hired employees better salary. And some departments will have a range of better salaries than others. Make sure to keep that relation. There are only 5 different departments. You can add extra fields if you want but thee are less relevant." , rows=200)
#generate_csv_from_theme_high_quality("Generate football data. Name, position, date of birth, height, team he plays for, scored goals, and some description about its game. Add some other fields you find relevant." , rows=5, pro = True, filename="ficheros/synthetic_data_high_pro.csv")
#generate_csv_from_theme_internet("Recent news that happend in the world. Title, brief description, and date. Be specific about each new in the title.", rows= 15)