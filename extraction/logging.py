"""Module for logging and error tracking."""
import __main__
import logging
from sys import stdout

import sentry_sdk


class Log:
    """A generic logging method that handles console & Sentry logging."""
    def __init__(self, config):
        self.sentry = config.sentry.enable_sentry
        self.stdout = config.sentry.enable_stdout
        self.logger = None

        if self.stdout:
            self.logger = logging.getLogger(__name__)

    def debug(self, message):
        """Capture a message with a level of 'debug'.

            Does not call Sentry method, as we only capture Sentry
            messages with a level of 'warning' or gerater
        """
        self._logger_message(message, logging.DEBUG)

    def info(self, message):
        """Capture a message with a level of 'INFO'.

            Does not call Sentry method, as we only capture Sentry
            messages with a level of 'warning' or gerater
        """
        self._logger_message(message, logging.INFO)

    def warning(self, message):
        """Capture a message with a level of 'warning'."""
        self._sentry_message(message, 'warning')
        self._logger_message(message, logging.WARNING)

    def error(self, message):
        """Capture a message with a level of 'error'."""
        self._sentry_message(message, 'error')
        self._logger_message(message, logging.ERROR)

    def critical(self, message):
        """Capture a message with a level of 'critical'."""
        self._sentry_message(message, 'critical')
        self._logger_message(message, logging.CRITICAL)

    def _sentry_message(self, message, level):
        """Logs a Sentry message (if enabled)."""
        if self.sentry:
            sentry_sdk.capture_message(message, level)

    def _logger_message(self, message, level):
        """Logs a message via the logger (if enabled)."""
        if self.stdout:
            self.logger.log(level, message)


def initiate_logging(config):
    """Initiates logging functions for script.

        Sentry is used as the logger (if enabled in the config file).
        Otherwise, all details will be logged to stdout.
    """
    # Set up Sentry (if enabled)
    if config.sentry.enable_sentry:
        sentry_sdk.init(
            config.sentry.dsn,
            traces_sample_rate=config.sentry.sample_rate,
            environment=config.sentry.environment,
            debug=config.debug,
        )

    # Return a generic logging object
    return Log(config)
