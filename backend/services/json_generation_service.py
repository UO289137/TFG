import json
import logging
from utils.json_utils import JSONUtils
from utils.validation_utils import ValidationUtils

class JSONGenerationService:
    """
    Generates a valid JSON config for data generation from an OpenAI chat response.
    """

    def __init__(self, openai_service, logger: logging.Logger):
        self.openai_service = openai_service
        self.logger = logger

    def create_response_final(self, theme: str, json_example: dict) -> dict:
        """
        Request a JSON structure from the OpenAI model based on a given example,
        then validate and return it as a Python dictionary.
        """
        self.logger.info(f"Asking OpenAI for a valid JSON structure for theme: '{theme}'.")
        prompt = (
            f"Please provide a valid JSON structure similar to the example below. "
            f"You must use the same fields and data types. The generated fields "
            f"should be thematically related to '{theme}', but remain synthetic.\n\n{json_example}\n"
        )
        raw_response = self.openai_service.chat_openai(prompt)

        # Extract the JSON part from the response
        json_str = JSONUtils.extract_low_result_json(raw_response)
        config_dict = json.loads(json_str)

        # Validate format
        self.logger.info("Validating the format of the generated JSON.")
        if not ValidationUtils.validate_config_dict(config_dict):
            raise ValueError("Generated JSON config is invalid or incomplete.")

        return config_dict
