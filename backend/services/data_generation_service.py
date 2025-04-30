import logging
import json
import random
import pandas as pd
import os
from faker import Faker
from utils.data_utils import (
    is_name, 
    is_id, 
    is_country, 
    generate_ids, 
    generate_country,
    generate_random_date
)
from utils.validation_utils import validate_config_dict
from utils.json_utils import format_result_for_jsonl, jsonlist_to_csv

from sdv.metadata import Metadata
from sdv.single_table import CTGANSynthesizer
from sdv.single_table import GaussianCopulaSynthesizer


class DataGenerationService:
    """
    Provides methods for generating synthetic data in CSV format using 
    either a configuration dictionary or direct JSONL responses from OpenAI.
    """

    def __init__(self, translator_service, openai_service, logger: logging.Logger):
        self.translator_service = translator_service
        self.openai_service = openai_service
        self.logger = logger

    def generate_data_from_config(
        self, 
        config: dict, 
        vary_names: bool, 
        vary_countries: bool, 
        num_rows: int, 
        output_file: str
    ) -> None:
        """
        Generate a CSV file based on a configuration dictionary.
        """
        if not validate_config_dict(config):
            raise ValueError("The provided config dictionary is invalid.")

        data = {}
        columns = config.get('columns', {})

        for column_name, properties in columns.items():
            col_type = properties.get('type')

            if col_type == 'string':
                values = properties['values']
                # Basic checks to see if they're mostly names or mostly countries
                name_count = sum(1 for v in values if is_name(v))
                country_count = sum(1 for v in values if is_country(v, self.translator_service.translate_text))
                threshold = 0.5
                total_values = len(values)

                if vary_names and (name_count / total_values) >= threshold:
                    # Generate random names
                    data[column_name] = [self._faker_name() for _ in range(num_rows)]
                elif vary_countries and (country_count / total_values) >= threshold:
                    # Generate random countries
                    data[column_name] = [generate_country() for _ in range(num_rows)]
                elif is_id(column_name):
                    # Generate IDs
                    data[column_name] = generate_ids(values[0], num_rows)
                else:
                    # Pick random from existing values
                    data[column_name] = [random.choice(values) for _ in range(num_rows)]

            elif col_type == 'int':
                if is_id(column_name):
                    data[column_name] = generate_ids("0", num_rows)
                else:
                    # Generate random integers
                    min_val = properties['min']
                    max_val = properties['max']
                    data[column_name] = [random.randint(min_val, max_val) for _ in range(num_rows)]

            elif col_type == 'float':
                min_val = properties['min']
                max_val = properties['max']
                data[column_name] = [
                    round(random.uniform(min_val, max_val), 2) 
                    for _ in range(num_rows)
                ]

            elif col_type == 'boolean':
                data[column_name] = [random.choice([True, False]) for _ in range(num_rows)]

            elif col_type == 'date':
                start_str = properties['start']
                end_str = properties['end']
                data[column_name] = [
                    generate_random_date(start_str, end_str) 
                    for _ in range(num_rows)
                ]
            else:
                self.logger.error(f"Unknown type '{col_type}' for column '{column_name}'")
                continue

        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        self.logger.info(f"Data generation complete. Output file: {output_file}")

    def _faker_name(self):
        """
        Wrapper for generating a single fake name. 
        (Alternatively, you could just inline Faker().name(), but 
         it's useful to have a dedicated method in case you'd like to mock it in tests.)
        """
        
        fake = Faker()
        return fake.name()

    def generate_data_merlin(
        self, 
        theme: str, 
        json_generation_service, 
        rows: int = 1000, 
        vary_names: bool = True, 
        vary_countries: bool = True, 
        output_file: str = "generations/synthetic_data_merlin.csv"
    ):
        """
        Generates data using a "Merlin" approach: obtains a JSON config from OpenAI, 
        then uses that config to create a CSV.
        """
        self.logger.info(f"Starting MERLIN generation for theme '{theme}' with {rows} rows.")
        tries = 2
        config_dict = None

        while tries > 0:
            try:
                config_dict = json_generation_service.create_response_final(
                    theme, 
                    json_example={
                        "columns": {
                            "name": { "type": "string", "values": ["Alice", "Bob", "Charlie"] },
                            "age": { "type": "int", "min": 18, "max": 65 },
                            "salary": { "type": "float", "min": 30000, "max": 120000 },
                            "is_manager": { "type": "boolean" },
                            "hire_date": { "type": "date", "start": "2010-01-01", "end": "2023-12-31" }
                        }
                    }
                )
                if validate_config_dict(config_dict):
                    break
            except Exception as e:
                self.logger.error(f"Error creating config: {e}")
            tries -= 1

        if not config_dict or not validate_config_dict(config_dict):
            self.logger.error("Could not generate a valid configuration after multiple attempts.")
            return

        self.generate_data_from_config(
            config=config_dict,
            vary_names=vary_names,
            vary_countries=vary_countries,
            num_rows=rows,
            output_file=output_file
        )

    def generate_data_gold(
        self, 
        theme: str, 
        rows: int = 50, 
        output_file: str = "generations/synthetic_data_gold.csv"
    ):
        """
        Generate a CSV file with "high-quality" synthetic data based on a theme 
        by directly requesting JSONL from OpenAI and then converting it to CSV.
        """
        self.logger.info(f"Starting GOLD generation for theme '{theme}' with {rows} rows.")
        # Constants
        MAX_ROWS = 200
        MIN_ROWS = 1

        # Basic validation
        if rows < MIN_ROWS:
            error_message = "Number of rows cannot be < 1."
            self.logger.error(error_message)
            return
        if rows > MAX_ROWS:
            error_message = "Row limit exceeded (max 200 for GOLD)."
            self.logger.error(error_message)
            return

        # Build prompt
        prompt = (
            f"Generate {rows} valid, newline-separated JSONL entries about: {theme}. "
            f"All data must be synthetic, make sure if there are any names that you anonimize them for data compliance, make up a name."
            f"Ensure each entry has the exact same fields."
            f"including a unique 'id' field for each line. Each JSON entry should be on its own line."
            f"Containing only simple key-value pairs. Do not include any nested dictionaries or arrays that contain objects."
        )
        result = self.openai_service.chat_openai(prompt)
        # Extract multiple JSON objects from the raw text
        try:
            result = format_result_for_jsonl(result)
            self.logger.info("\nThis is the corrected JSON content:\n" + result)
        except Exception as e:
            error_message = f"Error processing the OpenAI response: {e}"
            self.logger.error(error_message)
            return

        # Split into lines
        jsonl_entries = result.strip().split("\n")
        self.logger.info(f"Received {len(jsonl_entries)} JSONL entries from the model.")

        # Convert to CSV
        jsonlist_to_csv(jsonl_entries, output_file, self.logger)

        # (Optional) You could add a row-count check here
        try:
            df = pd.read_csv(output_file)
            if len(df) < rows * 0.75:
                self.logger.error("CSV does not meet the minimum row requirement (75%).")
        except Exception as e:
            self.logger.error(f"Error reading generated CSV: {e}")

    def generate_data_ctgan(
        self, 
        input_file: str,
        rows: int = 20,
        output_file: str = "generations/synthetic_data_ctgan.csv"
    ):
        """
        Genera datos sintéticos usando CTGAN a partir de un CSV subido por el usuario.
        1) Carga el CSV a un DataFrame.
        2) Crea el metadata y lo ajusta.
        3) Entrena el sintetizador CTGAN.
        4) Genera N filas sintéticas.
        5) Combina el dataset sintético con el original y guarda el resultado.
        """
        try:
            self.logger.info(f"generate_data_ctgan: input_file={input_file}, rows={rows}")

            # 1) Leer el CSV original
            df_original = pd.read_csv(input_file)
            df_training = None
            if df_original.empty:
                raise ValueError("El CSV subido está vacío o no contiene columnas.")

            self.logger.info(f"Original CSV shape: {df_original.shape}")

            # Si el DataFrame tiene más de 10000 entradas, seleccionar 10000 aleatoriamente
            if df_original.shape[0] > 10000:
                df_training = df_original.sample(n=10000, random_state=42)
                self.logger.info("Se han seleccionado 10.000 entradas aleatorias para el entrenamiento.")
            else:
                df_training = df_original

            # 2) Crear Metadata y detectar automáticamente
            metadata = Metadata()
            metadata = metadata.detect_from_dataframe(df_training)

            # 3) Crear el sintetizador con la metadata (puedes personalizar parámetros)
            synthesizer = CTGANSynthesizer(metadata=metadata)
            self.logger.info("Entrenando CTGAN...")
            synthesizer.fit(df_training)
            self.logger.info("Entrenamiento finalizado.")

            # 4) Generar N filas sintéticas
            df_synthetic = synthesizer.sample(num_rows=rows)
            self.logger.info(f"Synthetic data shape: {df_synthetic.shape}")

            # 5) Combinar original + sintético (opcional, si quieres "aumentar")
            df_augmented = pd.concat([df_original, df_synthetic], ignore_index=True)

            # Crear la carpeta de salida si no existe
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # Guardar el CSV final
            df_augmented.to_csv(output_file, index=False)
            self.logger.info(f"Archivo aumentado guardado en: {output_file}")

        except Exception as e:
            self.logger.error(f"Error en generate_data_ctgan: {str(e)}")
            raise

    def generate_data_gaussian(
        self, 
        input_file: str,
        rows: int = 20,
        output_file: str = "generations/synthetic_data_gaussian.csv"
    ):
        """
        Genera datos sintéticos usando GaussianCopula a partir de un CSV subido por el usuario.
        1) Carga el CSV a un DataFrame.
        2) Crea el metadata y lo ajusta.
        3) Entrena el sintetizador GaussianCopula.
        4) Genera N filas sintéticas.
        5) Combina el dataset sintético con el original y guarda el resultado.
        """
        try:
            self.logger.info(f"generate_data_gaussian: input_file={input_file}, rows={rows}")

            # 1) Leer el CSV original
            df_original = pd.read_csv(input_file)
            df_training = None
            if df_original.empty:
                raise ValueError("El CSV subido está vacío o no contiene columnas.")

            self.logger.info(f"Original CSV shape: {df_original.shape}")

            # Si el DataFrame tiene más de 10000 entradas, seleccionar 10000 aleatoriamente
            if df_original.shape[0] > 10000:
                df_training = df_original.sample(n=10000, random_state=42)
                self.logger.info("Se han seleccionado 10.000 entradas aleatorias para el entrenamiento.")
            else :
                df_training = df_original

            # 2) Crear Metadata y detectar automáticamente
            metadata = Metadata()
            metadata = metadata.detect_from_dataframe(df_training)

            # 3) Crear el sintetizador con la metadata (puedes personalizar parámetros)
            synthesizer = GaussianCopulaSynthesizer(metadata=metadata)
            self.logger.info("Entrenando GaussianCopulaSynthesizer...")
            synthesizer.fit(df_training)
            self.logger.info("Entrenamiento finalizado.")


            # 4) Generar N filas sintéticas
            df_synthetic = synthesizer.sample(num_rows=rows)
            self.logger.info(f"Synthetic data shape: {df_synthetic.shape}")

            # 5) Combinar original + sintético (opcional, si quieres "aumentar")
            df_augmented = pd.concat([df_original, df_synthetic], ignore_index=True)

            # Crear la carpeta de salida si no existe
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # Guardar el CSV final
            df_augmented.to_csv(output_file, index=False)
            self.logger.info(f"Archivo aumentado guardado en: {output_file}")

        except Exception as e:
            self.logger.error(f"Error en generate_data_gaussian: {str(e)}")
            raise
