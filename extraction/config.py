"""Manages details around script configuration."""
import configparser
from decimal import Decimal
from pathlib import Path
from typing import NamedTuple


class Config:
    """Class to hold configuration details."""
    def __init__(self, config_path):
        """Initialization details for Config class.

            Args:
                config_path (str):

            Attributes:
                config_path: a Path object to the script's config file.
                sentry: A named tuple containing Sentry config details.
                api: A named tuple containing API config details.
        """
        self.config_path = Path(config_path)
        self.api = None
        self.sentry = None

        self._assemble_app_configuration_details()

    class SentryDetails(NamedTuple):
        """Describes Sentry configuration details."""
        enable_sentry: bool
        enable_stdout: bool
        dsn: str
        environment: str
        sample_rate: Decimal

    class APIDetails(NamedTuple):
        """Describes HC DPD Upload API configuration details."""
        debug: bool
        url: str
        token: str

    def _assemble_app_configuration_details(self):
        """Collects and assigns all the relevant configuration details.

            Loads the config file with the provided Path. Once loaded,
            retrieves all config details and parses into correct
            formats and types.

            Updates object attributes with these details.
        """
        # Read the config file from the provided root
        config = configparser.ConfigParser(
            converters={'decimal': Decimal}
        )
        config.read(self.config_path)

        # Raise alert if no config file found
        if not config.sections():
            raise FileNotFoundError('Config file not found or is empty.')

        # Assign Sentry details
        self.sentry = self.SentryDetails(
            config.getboolean('sentry', 'enable_sentry', fallback=False),
            config.getboolean('sentry', 'enable_stdout', fallback=True),
            config.get('sentry', 'dsn', fallback='https://A@sentry.io/1'),
            config.get('sentry', 'environment', fallback='production'),
            config.getdecimal('sentry', 'sample_rate', fallback='1.0'),
        )

        # Assign API details
        self.api = self.APIDetails(
            config.getboolean('api', 'debug', fallback=False),
            config.get('api', 'url', fallback=''),
            config.get('api', 'token', fallback=''),
        )
