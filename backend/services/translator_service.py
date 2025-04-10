import logging
from deep_translator import GoogleTranslator

class TranslatorService:
    """
    Service to handle text translation using deep-translator.
    """

    def __init__(self, logger: logging.Logger, source_lang: str = 'auto'):
        self.logger = logger
        self.source_lang = source_lang

    def translate_text(self, text: str, target_language: str = "en") -> str:
        """
        Translate the given text to the target language using deep-translator.
        """
        self.logger.info(f"translate_text called with input: '{text}' -> '{target_language}'")
        try:
            translator = GoogleTranslator(source=self.source_lang, target=target_language)
            translated_text = translator.translate(text)
            self.logger.info(f"Translation successful: '{translated_text}'")
            return translated_text
        except Exception as e:
            error_message = f"Translation failed: {str(e)}"
            self.logger.error(error_message)
            return error_message
