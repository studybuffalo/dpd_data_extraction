"""Manages downlaods from the DPD site."""
from pathlib import Path
import time
from urllib.robotparser import RobotFileParser
from zipfile import ZipFile

from .utils import setup_session


def _get_robot_rules(config, log):
    """Retrieves any request rules from the robot.txt file.

        Args:
            config (obj): a Config object.
            log (obj): a Log object

        Returns:
            float: the number of seconds to wait between requests.
    """
    # Setup parser and retrieve robots.txt details
    parser = RobotFileParser()
    parser.set_url(config.download.robots_txt)
    parser.read()

    # Confirm if robot is allowed to proceed
    log.info('Confirming robot is permitted to crawl')
    if parser.can_fetch(config.download.robots_user_agent, config.download.robots_crawl_location) is False:
        raise PermissionError(
            f'Robot does not have permission to crawl URL: "{config.download.robots_crawl_location}"'
        )

    # Determine the crawl delay (if any)
    txt_crawl_delay = parser.crawl_delay(config.download.robots_user_agent)

    # Determine request rate (if any)
    txt_request_rate = parser.request_rate(config.download.robots_user_agent)

    # Convert request rate to seconds per request
    if txt_request_rate:
        seconds_per_request = txt_request_rate.seconds / txt_request_rate.requests
    else:
        seconds_per_request = None

    # Use the longest time as the delay
    delays = [config.download.robots_crawl_delay]

    if txt_crawl_delay:
        delays.append(txt_crawl_delay)

    if seconds_per_request:
        delays.append(seconds_per_request)

    return max(delays)


def _download_zips(config, log):
    """Downloads the zip files containing DPD data.

        Args:
            config (ojb): a Config object.
            log (obj): a Log object.
    """
    if config.download.download_debug:
        log.debug('Download Debug Mode: skipping extract download.')

        return

    # Perform checks for robots.txt rules and get request delay
    delay = _get_robot_rules(config, log)

    # Create a Requests session
    session = setup_session(config, log)

    # Get or create a save directory
    log.info('Downloading extract files from Health Canada Drug Product Databse.')

    save_path = Path(config.download.save_location)
    save_path.mkdir(exist_ok=True)

    for details in config.download.files:
        # Get the file from the DPD website
        log.debug(f'Requesting file from "{details["url"]}"')
        response = session.get(details['url'])

        # Confirms zip file exists at URL
        if response.status_code == 404:
            raise FileNotFoundError(f'Requested zip file does not exist: "{details["url"]}"')

        # Save the downloaded file
        with open(details['zip_save_path'], 'wb') as file:
            log.debug(f'Saving "{details["zip_save_path"]}"')
            file.write(response.content)

        time.sleep(delay)


def _extract_csv_files(config, log):
    """Extracts the CSV files from the downloaded zip files.

        Args:
            config (ojb): a Config object.
            log (obj): a Log object.
        """
    if config.download.extract_debug:
        log.debug('Extract Debug Mode: skipping zip file extraction.')

        return

    log.info('Extracting data files from zip files.')

    # Cycle through every zip file
    for details in config.download.files:
        # Open Zip file
        log.debug(f'Opening zip file "{details["zip_save_path"]}"')

        with ZipFile(details['zip_save_path']) as zip_file:
            # Rename the file witin the zip file
            log.debug(f'Renaming "{details["file_name"]}" to "{details["save_name"]}"')

            zip_info = zip_file.getinfo(details['file_name'])
            zip_info.filename = details['save_name']

            # Extract the file to the save location
            log.debug(f'Extracting "{details["save_name"]}" from zip file')
            zip_file.extract(zip_info, config.download.save_location)


def download_extracts(config, log):
    """Handles download of the data extract files.
        Args:
            config (ojb): a Config object.
            log (obj): a Log object.
        """
    # Download the zip files
    _download_zips(config, log)

    # Extract the CSV files from the zip files
    _extract_csv_files(config, log)


def remove_extracts(config, log):
    """Handles removal of the data extract files.

        Args:
            config (ojb): a Config object.
            log (obj): a Log object.
    """
    if config.download.removal_debug:
        log.debug('Removal Debug Mode: skipping extract file removal.')

        return

    download_directory = Path(config.download.save_location)

    # Remove .zip files
    log.info('Removing extract zip files.')

    zip_files = download_directory.glob('*.zip')

    for file in zip_files:
        file.unlink()

    # Remove .txt files
    log.info('Removing extract .txt files.')

    txt_files = download_directory.glob('*.txt')

    for file in txt_files:
        file.unlink()
