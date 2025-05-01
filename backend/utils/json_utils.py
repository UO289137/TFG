import re
import json
import csv
import logging

class JSONUtils:
    """
    Utilidad estática para extraer JSON de texto crudo,
    formatear JSONL y convertir listas JSONL a CSV.
    """

    @staticmethod
    def format_result_for_jsonl(raw_result: str) -> str:
        """
        Limpia el texto crudo para extraer múltiples objetos JSON,
        devolviéndolos como JSONL (uno por línea).
        """
        matches = re.findall(r'\{.*?\}', raw_result, re.DOTALL)
        if not matches:
            raise ValueError("No valid JSON block found in the response.")

        # Une los bloques JSON con saltos de línea
        json_content = "\n".join(matches).replace("\n\n", "\n")

        # Corrige valores N/A no entre comillas
        corrected_json_content = re.sub(r'(?<!")\bN/A\b(?!")', '"N/A"', json_content)
        return corrected_json_content

    @staticmethod
    def extract_low_result_json(raw_result: str) -> str:
        """
        Extrae y devuelve sólo el bloque JSON válido del texto,
        eliminando comillas triples u otros textos alrededor.
        """
        cleaned = raw_result.replace("'''json", "").strip()
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if not match:
            raise ValueError("No valid JSON structure found.")
        return match.group(0)

    @staticmethod
    def jsonlist_to_csv(jsonl_list: list, output_file: str, logger: logging.Logger) -> None:
        """
        Convierte una lista de cadenas JSONL en un fichero CSV.
        Las columnas se infieren de las claves del primer objeto.
        """
        logger.info(f"Starting conversion of {len(jsonl_list)} JSONL strings to CSV: {output_file}")

        json_objects = []
        for idx, line in enumerate(jsonl_list):
            try:
                obj = json.loads(line.strip())
                json_objects.append(obj)
                logger.debug(f"Parsed JSONL at index {idx}: {obj}")
            except json.JSONDecodeError as je:
                logger.error(f"JSON decode error at index {idx}: {je}")
            except Exception as e:
                logger.error(f"Unexpected error at index {idx}: {e}")

        if not json_objects:
            logger.warning("No valid JSON objects to write. Aborting CSV creation.")
            return

        fieldnames = list(json_objects[0].keys())
        logger.info(f"Using fieldnames: {fieldnames}")

        try:
            with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for obj in json_objects:
                    writer.writerow(obj)
                    logger.debug(f"Wrote row: {obj}")
            logger.info(f"CSV created successfully: {output_file}")
        except Exception as e:
            logger.error(f"Error writing CSV: {e}")
