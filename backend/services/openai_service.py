import logging
import json

# If you are using the official openai library, it would be:
# import openai
# And you'd call openai.ChatCompletion.create(...)

# Here we assume you have a custom client `from openai import OpenAI` as in your original code:
from openai import OpenAI

class OpenAIService:
    """
    Service to encapsulate interactions with OpenAI chat models.
    """

    def __init__(self, logger: logging.Logger, model_name: str = "gpt-4o-mini"):
        self.logger = logger
        self.model_name = model_name
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """
        Initialize the custom OpenAI client. 
        This may differ if you use the official openai library.
        """
        try:
            self.client = OpenAI()  # automatically sets up the API key
            self.logger.debug("OpenAI client successfully initialized.")
        except Exception as e:
            self.logger.error(f"Error initializing OpenAI client: {e}")
            self.client = None

    def chat_openai(self, message: str) -> str:
        """
        Send a message to the OpenAI model and return the response text.
        """
        self.logger.info(f"chat_openai called with message: '{message}' and model: '{self.model_name}'")

        if not self.client:
            error_message = "OpenAI client is not initialized."
            self.logger.error(error_message)
            return error_message

        try:
            # Build the messages array
            if self.model_name in ["gpt-4o-mini"]:
                messages_openai = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": message},
                ]
            else:
                # Example for other models
                messages_openai = [
                    {"role": "user", "content": message},
                ]

            # Send request to OpenAI API
            self.logger.info("Sending request to OpenAI API...")
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages_openai
            )

            # Extract the response text
            response = completion.choices[0].message.content
            self.logger.info(f"Response received: {response}")
            return response

        except Exception as e:
            error_message = "Error: Unable to get a response from the OpenAI model."
            self.logger.error(f"{error_message} Exception: {e}")
            return error_message
