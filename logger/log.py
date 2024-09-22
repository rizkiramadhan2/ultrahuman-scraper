import logging


class Logger:
    logger = None

    @classmethod
    def initialize(cls):
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,  # Set the logging level to INFO
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        # Create a logger
        cls.logger = logging.getLogger(__name__)

    @classmethod
    def info(cls, message):
        cls.logger.info(message)

    @classmethod
    def error(cls, message):
        cls.logger.error(message)

    @classmethod
    def warning(cls, message):
        cls.logger.warning(message)
