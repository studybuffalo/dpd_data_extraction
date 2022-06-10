"""Manages details around script configuration."""
import configparser
from decimal import Decimal
from pathlib import Path
from typing import NamedTuple


class Config:  # pylint: disable=too-few-public-methods
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
        self.logging = None
        self.download = None
        self.upload = None

        self._assemble_app_configuration_details()

    class LoggingDetails(NamedTuple):
        """Describes Logging configuration details."""
        enable_sentry: bool
        dsn: str
        environment: str
        sample_rate: Decimal
        sentry_debug: bool
        enable_stdout: bool
        stdout_level: int

    class DownloadDetails(NamedTuple):
        """Describes HC DPD extract download configuration details."""
        download_debug: bool
        extract_debug: bool
        removal_debug: bool
        save_location: str
        files: list
        robots_txt: str
        robots_crawl_location: str
        robots_user_agent: str
        robots_from: str
        robots_crawl_delay: float

    class UploadDetails(NamedTuple):
        """Describes HC DPD upload configuration details."""
        debug: bool
        api_token: str
        api_upload_url: str
        api_checksum_url: str
        checksum_step: int

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

        # Call methods to assign various details
        self._assign_logging_details(config)
        self._assign_download_details(config)
        self._assign_upload_details(config)

    def _assign_logging_details(self, config):
        """Assigns details for tracking & logging.

            Args:
                config (obj): a ConfigParser object containing
                    configuration details for script.
        """
        self.logging = self.LoggingDetails(
            config.getboolean('logging', 'enable_sentry', fallback=False),
            config.get('logging', 'dsn', fallback='https://A@sentry.io/1'),
            config.get('logging', 'environment', fallback='production'),
            config.getdecimal('logging', 'sample_rate', fallback='1.0'),
            config.getboolean('logging', 'sentry_debug', fallback=False),
            config.getboolean('logging', 'enable_stdout', fallback=True),
            config.getint('logging', 'stdout_level', fallback=10),
        )

    def _assign_download_details(self, config):
        """Assigns details for download & extraction of DPD data.

            Args:
                config (obj): a ConfigParser object containing
                    configuration details for script.
        """
        # Mapping of config sections & keys
        config_sections = {
            'download_active_ingredient': {
                'file_types': ['marketed', 'approved', 'inactive', 'dormant'],
                'extract_name': 'active_ingredient',
            },
            'download_biosimilar': {
                'file_types': ['marketed', 'approved', 'inactive', 'dormant'],
                'extract_name': 'biosimilar',
            },
            'download_company': {
                'file_types': ['marketed', 'approved', 'inactive', 'dormant'],
                'extract_name': 'company',
            },
            'download_drug_product': {
                'file_types': ['marketed', 'approved', 'inactive', 'dormant'],
                'extract_name': 'drug_product',
            },
            'download_form': {
                'file_types': ['marketed', 'approved', 'inactive', 'dormant'],
                'extract_name': 'form',
            },
            'download_inactive_product': {
                'file_types': ['inactive'],
                'extract_name': 'inactive_product',
            },
            'download_packaging': {
                'file_types': ['marketed', 'approved', 'inactive', 'dormant'],
                'extract_name': 'packaging',
            },
            'download_pharmaceutical_standard': {
                'file_types': ['marketed', 'approved', 'inactive', 'dormant'],
                'extract_name': 'pharmaceutical_standard',
            },
            'download_route': {
                'file_types': ['marketed', 'approved', 'inactive', 'dormant'],
                'extract_name': 'route',
            },
            'download_schedule': {
                'file_types': ['marketed', 'approved', 'inactive', 'dormant'],
                'extract_name': 'schedule',
            },
            'download_status': {
                'file_types': ['marketed', 'approved', 'inactive', 'dormant'],
                'extract_name': 'status',
            },
            'download_therapeutic_class': {
                'file_types': ['marketed', 'approved', 'inactive', 'dormant'],
                'extract_name': 'therapeutic_class',
            },
            'download_veterinary_species': {
                'file_types': ['marketed', 'approved', 'inactive', 'dormant'],
                'extract_name': 'veterinary_species',
            },
        }

        download_url = config.get('download', 'base_download_url')
        zip_save_location = config.get('download', 'save_location')
        file_details = []

        for section, items in config_sections.items():
            for type in items['file_types']:
                zip_name = config.get(section, f'{type}_zip_name')
                file_details.append({
                    'url': f'{download_url}{zip_name}',
                    'zip_save_path': Path(zip_save_location, zip_name),
                    'file_name': config.get(section, f'{type}_file_name'),
                    'save_name': config.get(section, f'{type}_save_name'),
                    'extract_name': items['extract_name'],
                })

        # Make the save location a Path object
        self.download = self.DownloadDetails(
            config.getboolean('download', 'download_debug', fallback=True),
            config.getboolean('download', 'extract_debug', fallback=True),
            config.getboolean('download', 'removal_debug', fallback=True),
            config.get('download', 'save_location'),
            file_details,
            config.get('download', 'robots_txt'),
            download_url,
            config.get('download', 'robots_user_agent'),
            config.get('download', 'robots_from'),
            config.getfloat('download', 'robots_crawl_delay', fallback=5),
        )

    def _assign_upload_details(self, config):
        """Assigns details for API upload.

            Args:
                config (obj): a ConfigParser object containing
                    configuration details for script.
        """
        self.upload = self.UploadDetails(
            config.getboolean('upload', 'debug', fallback=False),
            config.get('upload', 'api_token', fallback=''),
            config.get('upload', 'api_upload_url', fallback=''),
            config.get('upload', 'api_checksum_url', fallback=''),
            config.getint('upload', 'checksum_step', fallback=100000),
        )
