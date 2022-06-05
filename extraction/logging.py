"""Module for logging and error tracking."""
import logging

import sentry_sdk


class Log:
    """A generic logging method that handles console & Sentry logging.

        Args:
            config (obj): A Config instance.

        Attributes:
            sentry: boolean describing if Sentry logging is enabled.
            stdout: boolean describing if Python logging is enabled.
            logger: reference to the script's Python logger object.
    """
    def __init__(self, config):
        self.sentry = config.logging.enable_sentry
        self.stdout = config.logging.enable_stdout
        self.stdout_level = config.logging.stdout_level
        self.logger = self._setup_logger()

        self._setup_sentry(config)

    def _setup_logger(self):
        """Sets up the Python logging object (if enabled)."""
        # Checks if stdout logger is enabled
        if not self.stdout:
            return None

        # Create formatter for logger
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Create console handler for logger
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        # Create logger
        logger = logging.getLogger(__name__)
        logger.addHandler(handler)
        logger.setLevel(self.stdout_level)

        return logger

    def debug(self, message):
        """Capture a message with a level of 'debug'.

            Does not call Sentry method, as we only capture Sentry
            messages with a level of 'warning' or greater.

            Args:
                message (str): the message to log.
        """
        self._logger_message(message, logging.DEBUG)

    def info(self, message):
        """Capture a message with a level of 'INFO'.

            Does not call Sentry method, as we only capture Sentry
            messages with a level of 'warning' or greater.

            Args:
                message (str): the message to log.
        """
        self._logger_message(message, logging.INFO)

    def warning(self, message):
        """Capture a message with a level of 'warning'.

            Args:
                message (str): the message to log.
        """
        self._sentry_message(message, 'warning')
        self._logger_message(message, logging.WARNING)

    def error(self, message):
        """Capture a message with a level of 'error'.

            Args:
                message (str): the message to log.
        """
        self._sentry_message(message, 'error')
        self._logger_message(message, logging.ERROR)

    def critical(self, message):
        """Capture a message with a level of 'critical'.

            Args:
                message (str): the message to log.
        """
        self._sentry_message(message, 'critical')
        self._logger_message(message, logging.CRITICAL)

    def _sentry_message(self, message, level):
        """Logs a Sentry message (if enabled).

            Args:
                message (str): the message to log.
        """
        if self.sentry:
            sentry_sdk.capture_message(message, level)

    def _logger_message(self, message, level):
        """Logs a message via the logger (if enabled).

            Args:
                message (str): the message to log.
        """
        if self.stdout:
            self.logger.log(level, message)

    def _setup_sentry(self, config):
        """Sets up Sentry (if enabled).

                Args:
                    config (obj): A Config object instance.

                Returns:
                    obj: a Log object instance.
        """
        # Set up Sentry (if enabled)
        if config.logging.enable_sentry:
            sentry_sdk.init(
                config.sentry.dsn,
                traces_sample_rate=config.logging.sample_rate,
                environment=config.logging.environment,
                debug=config.logging.sentry_debug,
            )
