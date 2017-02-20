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
import pymysql
import configparser

from parse import parse
import upload


def file_len(fname):
	"""Calculates the number of lines in a file."""
	with open(fname) as f:
		for i, l in enumerate(f):
			pass
	return i + 1

def get_date():
	"""Returns the current date in a YYYY-MM-DD format."""
	today = datetime.date.today()
	year = today.year
	month = "%02d" % today.month
	day = "%02d" % today.day
	date = "%s-%s-%s" % (year, month, day)

	return date

def get_permission(robotFile):
	"""Checks the specified robot.txt file for access permission."""
	robot = robotparser.RobotFileParser()
	robot.set_url(robotFile)
	robot.read()

	can_crawl = robot.can_fetch(
		"Study Buffalo Data Extraction (http://www.studybuffalo.com/dataextraction/)",
		"https://idbl.ab.bluecross.ca/idbl/load.do")

	return can_crawl

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

def download_zips(suffixList, date):
    # Root URL to access all the zip files
    rootUrl = "http://www.hc-sc.gc.ca/dhp-mps/alt_formats/zip/prodpharma/databasdon/"

    # User Agent details for the program
    userAgent = ("Study Buffalo Data Extraction "
                 "(http://www.studybuffalo.com/dataextraction/)")
    email = "studybuffalo@studybuffalo.com"
    scriptHeader = {'User-Agent': userAgent, 'From': email}

    # Create the folder to hold the data extracts
    zipsLocation = root.child("dpd_data_extracts", date)

    if not zipsLocation.exists():
        os.mkdir(zipsLocation.absolute())
    
    for suffix in suffixList:
        # Set the file name for the downloads
        if suffix == "":
            zipName = "allfiles.zip"
        else:
            zipName = "allfiles_" + suffix + ".zip"
        
        # Access and download the 
        print (("Downloading %s... " % zipName), end="")

        # Creates zip path and name
        dlName = zipsLocation.child(zipName)

        # Create the zip url
        url = rootUrl + zipName
        
        # Request to download file
        req = request.Request(url, data=None, headers=scriptHeader)

        # Request the file and open a file to write the contents
        with request.urlopen(req) as response, open(dlName, 'wb') as file:
            # Read the requested file from the website
            zipFile = response.read()

            # Save the file
            file.write(zipFile)
        
        print ("Complete!")
    
    print ("\n")


# SET UP PROCESSES TO RUN PROGRAM
# Sets script directory to allow absolute path naming (for Cron job)
# root = Path("/", "home", "joshua", "scripts", "dpd_data_extraction")
root = Path("E:\\", "My Documents", "GitHub", "dpd_data_extraction")

# Get the date
today = get_date()

# The various .txt files accessed from the HC DPD zip files
fileList = [
    "comp", "drug", "form", "ingred", "package", "pharm", "route", 
    "schedule", "status", "ther", "vet"
]

# The three types of .zip and .txt files found on the HC DPD
suffixList = ["", "ia", "ap"]

print ("\nHEALTH CANADA DRUG PRODUCT DATABASE DATA EXTRACTION TOOL")
print ("--------------------------------------------------------")
print ("Created by Joshua Torrance, 2017-Feb-20\n\n")

# Downloads zip files
print ("DOWNLOADING DATA EXTRACTIONS ZIP FILES")
print ("--------------------------------------")
download_zips(suffixList, today)


"""
#Extract and parse zip files
for suffix in suffixList:
	zipName = 'allfiles.zip' if suffix == "" else 'allfiles_' + suffix + ".zip"
	
	zipPath  = os.path.join(scriptDir, "DPD_Data_Extract", date, zipName)
	
	# Access the zip file
	print("Opening %s\n" % zipName)
	archive = zipfile.ZipFile(zipPath, 'r')
	
	# Cycles through all the files and extracts the data
	for fileName in fileList:
		# Generates the file name
		fileName = fileName + ".txt" if suffix == "" else fileName + "_" + suffix + ".txt"
		
		# Extracts the DPD text file
		print("Accessing %s from %s" % (fileName, zipName))
		archive.extract(fileName)
		
		# Creates folder for parsed text files if necessary
		extractLocation = os.path.join(scriptDir, "Parsed_Data", date)
		extractLocation = os.path.normpath(extractLocation)
		
		if not os.path.exists(extractLocation):
			os.mkdir(extractLocation)
		
		# Creates a new text file or deletes previous data within file
		extractName = os.path.join(extractLocation, fileName)
		extractName = os.path.normpath(extractName)
		
		extractFile = codecs.open(extractName, encoding='latin-1', mode='w')
		extractFile.truncate()
		
		# Determining number of lines in text file for progress bar
		length = file_len(fileName)
		i = 1
		n = 1
		percent = 0
		
		# Opens file with 'latin-1' encoding
		with codecs.open(fileName, encoding='latin-1') as file:
			for line in file:
				# Reviews and formats each line as required
				parsedText = parse(fileName, line)
				
				# Writes each line to a temporary file (will ultimately upload to database)
				try:
					extractFile.write("%s\n" % parsedText)
				except:
					extractFile.write("ERROR PARSING ENTRY\n")
				
				# Progress bar
				percent = 100.00 * i / length
				
				if percent != 100:
					print("Parsing [%s%s] %.2f%%\r" % 
						  ((n - 1) * "#", (51 - n) * " ", percent)),
					sys.stdout.flush()
					
					n = n + 1 if percent > n * 2 else n
				else:
					print("Parsing [%s] Complete!" % ("#" * 50))
				
				i += 1
		
		# Closes the extract file
		try:
			print("Closing %s\n" % fileName)
			os.remove(fileName)
		except OSError, e:
			print("Error: %s - %s." % (e.fileName, e.strerror))
	
	# Closes the zip archive
	print("Closing %s\n\n" % zipName)
	archive.close()


#Connect to database
#List of database tables
tableList = ["comp", "comp_ap", "comp_ia",
			 "drug", "drug_ap", "drug_ia",
			 "form", "form_ap", "form_ia",
			 "ingred", "ingred_ap", "ingred_ia",
			 "package", "package_ap", "package_ia",
			 "pharm", "pharm_ap", "pharm_ia",
			 "route", "route_ap", "route_ia",
			 "schedule", "schedule_ap", "schedule_ia",
			 "status", "status_ap", "status_ia",
			 "ther", "ther_ap", "ther_ia",
			 "vet", "vet_ap", "vet_ia"]
			 
print("Establishing database connection")
conn = MySQLdb.connect(user='USERNAME', 
					   passwd='PASSWORD', 
					   db='DATABASE', 
					   host='HOST',
					   charset='latin1',
					   use_unicode=True)
cursor = conn.cursor()

#Cycles through and uploads each entry to the database
for tableName in tableList:
	print("Uploading to '%s' table..." % tableName),
	
	#Truncates table to prepare for new entries
	try:
		cursor.execute("TRUNCATE %s" % tableName)
		conn.commit()
	except MySQLdb.Error, e:
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
		except MySQLdb.Error, e:
			print ("Error trying insert entry %s into database: %s" % (i, e))
			pass
		
		
		'''
		# Progress bar
		percent = 100.00 * i / length
		
		if percent != 100:
			print("Uploading [%s%s] %.2f%%\r" % 
				  ((n - 1) * "#", (51 - n) * " ", percent)),
			sys.stdout.flush()
			
			n = n + 1 if percent > n * 2 else n
		else:
			print("Uploading [%s] Complete!\n" % ("#" * 50))
		
		i += 1
		'''
print("Closing connection to database\n")
conn.close()
"""

print ("Health Canada Drug Product Database Extraction Tool Finished!\n")
