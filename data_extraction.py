#!/usr/bin/env python3

"""Uploads the Health Canada Drug Product Database to a MySQL DB

    Last Update: 2017-Feb-20

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

"""
    STYLE RULES FOR THIS PROGRAM
    Style follows the Python Style Guide (PEP 8) where possible. The 
    following are common standards for reference
    
    COMMENT LINES to max of 72 characters
    PROGRAM LINES to a max of 79 characters
    
    INDENTATION 4 spaces
    STRINGS use quotation marks

    VARIABLES use camelCase
    GLOBAL VARIABLES use lowercase with underscores
    CLASSES use CapWords
    CONSTANTS use UPPERCASE
    FUNCTIONS use lowercase with underscores
    MODULES use lowercase with underscores
    
    ALIGNMENT
        If possible, align with open delminter
        If not possible, indent
        If one indent would align arguments with code in block, use 
            two indents to provide visual differentiation
        Operators should occur at start of line in broken up lines, 
        not at the end of the preceding line

    OPERATORS & SPACING
    Use spacing in equations
        e.g. 1 + 1 = 2
    Do not use spacing in assigning arguments in functions 
        e.g. def foo(bar=1):
"""

import codecs
from urllib import robotparser, request
import zipfile
from unipath import Path
import os
import sys
import datetime
import math
import pymysql
import configparser

from parse import parse_extract_entry
import upload

class FileDetails(object):
    title = ""
    suffix = ""
    locs = []

    def __init__(self, title, suffix, locs):
        # Generate file name based on suffix
        if suffix == "":
            name = "%s.txt" % title
        else:
            name = "%s_%s.txt" % (title, suffix)

        # Generate paths of extracted and parsed files
        ePath = locs["eLoc"].child(name)
        pPath = locs["pLoc"].child(name)

        self.title = title
        self.name = name
        self.ePath = ePath
        self.pPath = pPath


def file_len(fname):
	"""Calculates the number of lines in a file."""
	with open(fname) as f:
		for i, l in enumerate(f):
			pass
	return i + 1

def progress_bar(title, curPos, start, stop):
	"""Generates progress bar in console."""

	# Normalize start, stop, curPos
	curPos = (curPos - start) + 1
	stop = (stop - start) + 1 
	start = 1

	# Determine current progress
	prog = 100.00 * (curPos / stop)
	
	if prog != 100:
		progComp = "#" * math.floor(prog / 2)
		progRem = " " * (50 - math.floor(prog / 2))
		prog = "%.2f%%" % prog
		print(("%s [%s%s] %s  \r" % (title, progComp, progRem, prog)), end='')
		sys.stdout.flush()
	else:
		progComp = "#" * 50
		print("%s [%s] Complete!" % (title, progComp))


def create_extract_folders():
    """Creates the folders for holding the extracted files"""
    # Sets script directory to allow absolute path naming (for Cron job)
    # root = Path("/", "home", "joshua", "scripts", "dpd_data_extraction")
    root = Path("E:\\", "My Documents", "GitHub", "dpd_data_extraction")
    
    # Get the date
    today = datetime.date.today()
    year = today.year
    month = "%02d" % today.month
    day = "%02d" % today.day
    date = "%s-%s-%s" % (year, month, day)

    # Saves data extract location and creates folder if needed
    print ("Creating dpd_data_extracts folder... ", end="")
    extractLoc = root.child("dpd_data_extracts", date)

    if not extractLoc.exists():
        os.mkdir(extractLoc.absolute())
    
    print ("Complete!")

    # Saves parsed extract location and creates folder if needed
    print ("Creating parsed_data_extracts folder... ", end="")
    parseLoc = root.child("parsed_data_extracts", date)

    if not parseLoc.exists():
        os.mkdir(parseLoc.absolute())

    print ("Complete!\n")

    return {"eLoc": extractLoc, "pLoc": parseLoc}

def get_file_names(locs):
    """"Returns a list of all the file and folder details for the app"""
    print ("Generating file details... ", end="")

    names = [
        {
            "name": "allfiles.zip",
            "files": [
                FileDetails("comp", "", locs),
                FileDetails("drug", "", locs),
                FileDetails("form", "", locs),
                FileDetails("ingred", "", locs),
                FileDetails("package", "", locs),
                FileDetails("pharm", "", locs),
                FileDetails("route", "", locs),
                FileDetails("schedule", "", locs),
                FileDetails("status", "", locs),
                FileDetails("ther", "", locs),
                FileDetails("vet", "", locs)
            ]
         },
         {
            "name": "allfiles_ap.zip",
            "files": [
                FileDetails("comp", "ap", locs),
                FileDetails("drug", "ap", locs),
                FileDetails("form", "ap", locs),
                FileDetails("ingred", "ap", locs),
                FileDetails("package", "ap", locs),
                FileDetails("pharm", "ap", locs),
                FileDetails("route", "ap", locs),
                FileDetails("schedule", "ap", locs),
                FileDetails("status", "ap", locs),
                FileDetails("ther", "ap", locs),
                FileDetails("vet", "ap", locs)
            ]
         },
         {
            "name": "allfiles_ia.zip",
            "files": [
               FileDetails("comp", "ia", locs),
               FileDetails("drug", "ia", locs),
                FileDetails("form", "ia", locs),
                FileDetails("ingred", "ia", locs),
                FileDetails("package", "ia", locs),
                FileDetails("pharm", "ia", locs),
                FileDetails("route", "ia", locs),
                FileDetails("schedule", "ia", locs),
                FileDetails("status", "ia", locs),
                FileDetails("ther", "ia", locs),
                FileDetails("vet", "ia", locs)
            ]
         }
    ]

    print ("Complete!\n\n")

    return names

def get_permission(robotFile):
    """Checks the specified robot.txt file for access permission."""
    robot = robotparser.RobotFileParser()
    robot.set_url(robotFile)
    robot.read()
    
    can_crawl = robot.can_fetch(
		"Study Buffalo Data Extraction (http://www.studybuffalo.com/dataextraction/)",
		"https://idbl.ab.bluecross.ca/idbl/load.do")
    
    return can_crawl

def download_zips(locs, zipFiles):
    # Root URL to access all the zip files
    rootUrl = "http://www.hc-sc.gc.ca/dhp-mps/alt_formats/zip/prodpharma/databasdon/"

    # User Agent details for the program
    userAgent = ("Study Buffalo Data Extraction "
                 "(http://www.studybuffalo.com/dataextraction/)")
    email = "studybuffalo@studybuffalo.com"
    scriptHeader = {'User-Agent': userAgent, 'From': email}

    # Zips are saved to the extract location
    zipLoc = locs["eLoc"]

    for zip in zipFiles:
        zipName = zip["name"]

        # Access and download the zip file
        print (("Downloading %s... " % zipName), end="")

        # Creates zip path and name
        hdFile = zipLoc.child(zipName)

        # Create the zip url
        url = rootUrl + zipName
        
        # Request to download file
        req = request.Request(url, data=None, headers=scriptHeader)

        # Request the file and open a file to write the contents
        with request.urlopen(req) as response, open(hdFile, 'wb') as file:
            # Read the requested file from the website
            webFile = response.read()

            # Save the file
            file.write(webFile)
        
        print ("Complete!")
    
    print ("\n")

def unzip_zips(locs, names):
    # Set location to extract files to
    eLoc = locs["eLoc"]

    # Open each zip file and extract the files
    for zip in names:
        zipName = zip["name"]
        zipLoc = eLoc.child(zipName).absolute()
    
        # Unzip the zips
        print (("Unzipping %s... " % zipName), end="")
        archive = zipfile.ZipFile(zipLoc, 'r')
        
        # Cycles through all the files and extracts the data
        for file in zip["files"]:
            # Extracts the text file from the archive
            archive.extract(file.name, path=eLoc.absolute())
        
        archive.close()
        print ("Completed!")

    print ("\n")

def parse_files(names):
    # Cycles through each suffix
    for zip in names:
        for file in zip["files"]:
            # File details
            title = file.title
            name = file.name
            ePath = file.ePath
            pPath = file.pPath

            # Details for progress bar
            length = file_len(ePath)
            i = 1
            temp = [];
            
            # Name for progress bar (26 chars to all progress bars)
            pbTitle = "Extracting %s" % name
            pbTitle = pbTitle.ljust(26)

            # Open extracted file and create parsed file
            with open(ePath, "r") as ext, open(pPath, "w") as par:
                # Read each line of extracted file
                for line in ext:
                    # Parse line and write to parse file
                    pText = "%s\n" % parse_extract_entry(name, line)

                    par.write(pText)

                    # Display progress bar and increment counter
                    progress_bar(pbTitle, i, 1, length)
                    i = i + 1
        
        print ("")
    print ("")

    return ""

def upload_data(loc, data):
    """Uploads parsed files to the database."""
    # Obtain database credentials
    cLoc = loc["root"].parent.child("config", "python_config.cfg").absolute()
    
    # Connect to config file and collect MYSQL login information
    config = configparser.ConfigParser()
    config.read(cLoc)
    db = config.get("mysql_db_dpd", "db")
    host = config.get("mysql_db_dpd", "host")
    user = config.get("mysql_user_dpd_ent", "user")
    pw = config.get("mysql_user_dpd_ent", "password")

    #List of database tables
    tableList = [
        "comp", "comp_ap", "comp_ia", "drug", "drug_ap", "drug_ia", "form", 
        "form_ap", "form_ia", "ingred", "ingred_ap", "ingred_ia", "package", 
        "package_ap", "package_ia", "pharm", "pharm_ap", "pharm_ia", "route", 
        "route_ap", "route_ia", "schedule", "schedule_ap", "schedule_ia", 
        "status", "status_ap", "status_ia", "ther", "ther_ap", "ther_ia", 
        "vet", "vet_ap", "vet_ia"
    ]
    
    print("Establishing database connection")
    conn = None
    cursor = conn.cursor()
    
    #Cycles through and uploads each entry to the database
    for tableName in tableList:
        print(("Uploading to '%s' table..." % tableName), end="")
        
        #Truncates table to prepare for new entries
        try:
            cursor.execute("TRUNCATE %s" % tableName)
            conn.commit()
        except MySQLdb.Error as e:
            print ("Error Truncating Table: %s" % e)
            pass
        
        #Assembling path to parsed text file
        fileName = os.path.join(scriptDir, "Parsed_Data", date, tableName + ".txt")
        fileName = os.path.normpath(fileName)
        
        tempList = []
        length = file_len(fileName)
        i = 1
        n = 1
        
        # Opens file with 'latin-1' encoding
        with codecs.open(fileName, encoding='latin-1') as file:
            for line in file:
                # Generates MySQL statement and loads into database
                tempList.append(upload.generate_upload(tableName, line))
            
            statement = upload.generate_statement(tableName)
            
            try:
                cursor.executemany(statement, tempList)
                conn.commit()
                print ("Complete!")
            except MySQLdb.Error as e:
                print ("Error trying insert entry %s into database: %s" % (i, e))
                pass

        # PROGRESS BAR SOMEWHERE IN HERE?

        print("Closing connection to database\n")
        conn.close()
    


print ("\nHEALTH CANADA DRUG PRODUCT DATABASE DATA EXTRACTION TOOL")
print ("--------------------------------------------------------")
print ("Created by Joshua Torrance, 2017-Feb-20\n\n")

print ("CREATE APPLICATION FOLDERS AND FILE DETAILS")
print ("----------------------------------------------")
# Create the extract folders and save the paths
locs = create_extract_folders()

# Create a list of all file names, locations, and other details
names = get_file_names(locs)

# Downloads zip files
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

parsedData = parse_files(names)

#Upload the parsed files to the database
print ("UPLOADING PARSED DATA")
print ("---------------------")

upload_data(parsedData)


print ("Health Canada Drug Product Database Extraction Tool Finished!\n")
