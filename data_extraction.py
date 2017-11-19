"""Uploads the Health Canada Drug Product Database to a Django database

    Last Update: 2017-Nov-18

    Copyright (c) Notices
	    2017	Joshua R. Torrance	<studybuffalo@studybuffalo.com>
	
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

import configparser
from django.core.wsgi import get_wsgi_application
import logging
import logging.config
from modules import dpd_connections, extraction, normalize, upload
import os
import sys
from unipath import Path


# APPLICATION SETUP
# Setup root path
root = Path(sys.argv[1])

# Collect the config file
config = configparser.ConfigParser()
config.read(Path(root.parent, "config", "dpd_data_extraction.cfg"))

# Setup Logging
log_config = Path(root.parent, "config", "dpd_data_extraction_logging.cfg")
logging.config.fileConfig(log_config, disable_existing_loggers=False)
log = logging.getLogger(__name__)

# DATA EXTRACTION PROCESS
log.info("HEALTH CANADA DRUG PRODUCT DATABASE DATA EXTRACTION TOOL STARTED")

# Download the data extracts
dpd_connections.download_extracts(config)

# Unzip the files
extraction.unzip_files(config)

# Extracts the data from the .txt files
dpd_data = extraction.extract_dpd_data(config)

# Normalize the dpd_data for saving and upload
normalized_data = normalize.normalize_data(dpd_data)

# Upload the data to the Django database
upload.upload_data(normalized_data)

# Remove all the unzipped text files
extraction.remove_files(config)

"""
if permission:
    print ("CREATE APPLICATION FOLDERS AND FILE DETAILS")
    print ("----------------------------------------------")

    # Create the extract folders and save the paths
    locs = create_extract_folders()

    # Create a list of all file names, locations, and other details
    names = get_file_names(locs)


    # Download the zip files from the website
    print ("DOWNLOADING DATA EXTRACTIONS ZIP FILES")
    print ("--------------------------------------")

    download_zips(locs, names)


    # Extract the data extracts from the zip files
    print ("UNZIPPING FILES")
    print ("-------------------------------")

    unzip_zips(locs, names)


    # Parse the data extracts and return the data
    print ("PARSING FILES")
    print ("-------------")

    parsedData = parse_files(locs, names)


    # Upload the parsed files to the database
    print ("UPLOADING PARSED DATA")
    print ("---------------------")

    upload_data(locs, parsedData)


    print ("Health Canada Drug Product Database Extraction Tool Finished!\n")
"""