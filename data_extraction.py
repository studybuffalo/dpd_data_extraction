"""Uploads the Health Canada Drug Product Database to a Django database

    Last Update: 2022-Jun-02

    Copyright (c) Notices
        2022	Joshua R. Torrance	<joshua@torrance.io>

    This program is free software: you can redistribute it and/or
    modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not,
    see <http://www.gnu.org/licenses/>.

    SHOULD YOU REQUIRE ANY EXCEPTIONS TO THIS LICENSE, PLEASE CONTACT
    THE COPYRIGHT HOLDERS.
"""

# import configparser
# # Switch logging to Sentry
# import logging
# import logging.config
# import os
# import sys
# # Switch to pathlib
# from unipath import Path


# # APPLICATION SETUP
# # Setup root path
# root = Path(sys.argv[1])

# # Collect the config file
# config = configparser.ConfigParser()
# config.read(Path(root.parent, 'config', 'dpd_data_extraction.cfg'))

# # Setup Logging
# log_config = Path(root.parent, 'config', 'dpd_data_extraction_logging.cfg')
# logging.config.fileConfig(log_config, disable_existing_loggers=False)
# log = logging.getLogger(__name__)

# # Require critical logging for Django and Requests logging
# logging.getLogger('requests').setLevel(logging.CRITICAL)
# logging.getLogger('environ').setLevel(logging.CRITICAL)

#  # Setup the Django database connection
# os.environ.setdefault(
#     'DJANGO_SETTINGS_MODULE', config.get('django', 'settings')
# )
# sys.path.append(config.get('django', 'location'))
# application = get_wsgi_application()

# # Import program modules once Django is loaded
# from modules import (
#     dpd_connections, extraction, normalize, upload, substitution_functions
# )


# # DATA EXTRACTION PROCESS
# log.info('HEALTH CANADA DRUG PRODUCT DATABASE DATA EXTRACTION TOOL STARTED')

# # Download the data extracts
# dpd_connections.download_extracts(config)

# # Unzip the files
# extraction.unzip_files(config)

# # Extracts the data from the .txt files
# dpd_data = extraction.extract_dpd_data(config)
# substitution_functions.Substitutions()

# # Normalize the dpd_data for saving and upload
# normalized_data = normalize.normalize_data(dpd_data)

# # Remove all the previous entries from the database
# upload.remove_old_data()

# # Upload the data to the Django database
# upload.upload_data(config, normalized_data)

# # Remove all the unzipped text files
# extraction.remove_files(config)
