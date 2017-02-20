#!/usr/bin/env python3
# -*- coding: latin-1 -*-

'''Uploads the Health Canada Drug Product Database to a MySQL DB

  Last Update: 2017-Feb-20

  Copyright (c) Notices
	2017	Joshua R. Torrance	<studybuffalo@studybuffalo.com>
	
  This software may be used in any medium or format and adapated to
  any purpose under the following terms:
    - You must give appropriate credit, provide a link to the
      license, and indicate if changes were made. You may do so in
      any reasonable manner, but not in any way that suggests the
      licensor endorses you or your use.
    - You may not use the material for commercial purposes.
    - If you remix, transform, or build upon the material, you must 
      distribute your contributions under the same license as the 
      original.
	
  Alternative uses may be discussed on an individual, case-by-case 
  basis by contacting one of the noted copyright holders.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
  OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
  WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
  OTHER DEALINGS IN THE SOFTWARE.
'''
 
import codecs
import urllib2
import zipfile
import os
import sys
import datetime
import MySQLdb
from MySQLdb import escape_string
import hashlib
from parse import parse
import upload


def file_len(fname):
	'''Calculates the number of lines in a file.'''
	with open(fname) as f:
		for i, l in enumerate(f):
			pass
	return i + 1


# Current file directory
scriptDir = os.path.dirname(os.path.abspath(__file__))

# Generates today's date for saving and extracting files
today = datetime.date.today()
year = today.year
month = "%02d" % today.month
day = "%02d" % today.day
date = "%s-%s-%s" % (year, month, day)

# The various .txt files accessed from the HC DPD zip files
fileList = ["comp", "drug", "form", "ingred", "package", "pharm", "route", "schedule", "status", "ther", "vet"]

# The three types of .zip and .txt files found on the HC DPD
suffixList = ["", "ia", "ap"]

print("\nHealth Canada Drug Product Directorate Data Extraction Tool")
print("Created by Joshua Torrance, 2015-11-19\n")

# Downloads zip files
for suffix in suffixList:
	zipName = 'allfiles.zip' if suffix == "" else 'allfiles_' + suffix + ".zip"
	
	print("Downloading %s" % zipName)
	
	url = "http://www.hc-sc.gc.ca/dhp-mps/alt_formats/zip/prodpharma/databasdon/" + zipName
	scriptHeader = {
		'User-Agent': 'Study Buffalo Data Extraction (http://www.studybuffalo.com/dataextraction/)',
		'From': 'studybuffalo@studybuffalo.com'
	}
	
	request = urllib2.Request(url, headers=scriptHeader)
	zipFile = urllib2.urlopen(request)
	downloadFile = zipFile.read()
	
	# Create file path (and folder if needed)
	downloadLocation = os.path.join(scriptDir, "DPD_Data_Extract", date)
	downloadLocation = os.path.normpath(downloadLocation)
	
	if not os.path.exists(downloadLocation):
		os.mkdir(downloadLocation)
	
	# Creates file name
	downloadName = os.path.join(downloadLocation, zipName)
	downloadName = os.path.normpath(downloadName)
	
	# Saves file
	with open(downloadName, "wb") as file:
		file.write(downloadFile)
		
print("\n")

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

print("Extraction and Upload Complete!\n")