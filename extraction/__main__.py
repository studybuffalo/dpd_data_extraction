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
import pathlib
import sys

from . import Config, Log, download_extracts, remove_extracts


def main():
    """Organizes and runs the extraction script."""
    # APPLICATION SETUP
    # Retrieve path to config file
    config_path = pathlib.Path(sys.argv[1])

    # Setup config deatils
    config = Config(config_path)

    # Setup Logging
    log = Log(config)

    # DATA EXTRACTION PROCESS
    log.info('HEALTH CANADA DRUG PRODUCT DATABASE DATA EXTRACTION TOOL STARTED')

    # Download the data extracts
    download_extracts(config, log)

    # Read file content, run checksums, and submit to API (as needed)

    # Remove the downloaded files
    remove_extracts(config, log)

    # Return 0 to confirm successful completion
    return 0


if __name__ == '__main__':
    sys.exit(main())
