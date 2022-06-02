"""Module for logging and error tracking."""
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
        """Capture a message with a level of 'debug'."""
        self._capture_message(message, 'debug')

    def info(self, message):
        """Capture a message with a level of 'INFO'."""
        self._capture_message(message, 'info')

    def warning(self, message):
        """Capture a message with a level of 'warning'."""
        self._capture_message(message, 'warning')

    def error(self, message):
        """Capture a message with a level of 'error'."""
        self._capture_message(message, 'error')

    def critical(self, message):
        """Capture a message with a level of 'critical'."""
        self._capture_message(message, 'critical')

    def _capture_message(self, message, level):
        """Logs a message based on config details"""
        # Logs sentry messages if enabled & level is greater than "info"
        if self.sentry and level not in ('debug', 'info'):
            sentry_sdk.capture_message(message, level)

        # Logs to stdout if enabled (any level)
        if self.stdout:
            self.logger.log(message, level=level.upper())


def initiate_logging(config):
    """Initiates logging functions for script.

        Sentry is used as the logger (if enabled in the config file).
        Otherwise, all details will be logged to stdout.
    """
    # Set up Sentry (if enabled)
    if config.sentry.enable:
        sentry_sdk.init(
            config.sentry.dsn,
            traces_sample_rate=config.sentry.sample_rate,
            environment=config.sentry.environment,
            debug=config.debug,
        )

    # Return a generic logging object
    return Log(config)
