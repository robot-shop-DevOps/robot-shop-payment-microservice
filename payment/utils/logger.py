import logging
import sys

class Logger:
    def __init__(self, name="payment_service", level=logging.INFO):
        self.name = name
        self.level = level
        self.logger = None

    def create_logger(self):
        if self.logger:
            return self.logger  # reuse if already created

        logger = logging.getLogger(self.name)
        logger.setLevel(self.level)

        # Prevent duplicate handlers if called multiple times
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(self._get_formatter())
            logger.addHandler(handler)

        self.logger = logger
        return logger

    def _get_formatter(self):
        return logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
