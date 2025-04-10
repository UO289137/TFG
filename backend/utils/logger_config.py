import logging

def setup_logger(logger_name: str = "my_logger", log_file: str = "app.log") -> logging.Logger:
    """
    Configure and return a logger with the specified name.
    """
    # You can customize the logging level, format, file, etc.
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename=log_file,
        filemode='a'
    )

    logger = logging.getLogger(logger_name)
    return logger
