import logging

class LoggerUtils:
    """
    Clase estática para configurar y obtener loggers.
    """

    @staticmethod
    def setup_logger(logger_name: str = "my_logger", log_file: str = "app.log") -> logging.Logger:
        """
        Configura el sistema de logging (nivel, formato, archivo) 
        y devuelve un logger con el nombre especificado.
        """
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename=log_file,
            filemode='a'
        )
        return logging.getLogger(logger_name)
