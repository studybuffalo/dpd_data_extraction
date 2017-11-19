from datetime import datetime
import logging
from unipath import Path
import zipfile

import csv
import math

# Setup logging
log = logging.getLogger(__name__)

def unzip_files(config):
    """Unzips the download files"""
    extensions = config.get("zips", "extensions").split(",")

    # Sets up location to the zip files
    date = datetime.utcnow().strftime("%Y-%m-%d")
    root_path = Path(config.get("zips", "save_loc")).child(date)
    
    # Cycle through all the extensions and save the files for the zip
    for ext in extensions:
        zip_name = config.get("zips", "save_{}".format(ext))

        # Unzip the zip file
        log.debug("Unzipping {}".format(zip_name))
        
        zip_path = root_path.child(zip_name)
        zip_file = zipfile.ZipFile(zip_path, "r")

        # Get the names of the data files in the zip
        data_files = config.get("files_{}".format(ext), "files").split(",")

        # Cycle through each file name and save the file
        for file in data_files:
            file_name = "{}.txt".format(file)

            # Extract the text file from the archive
            log.debug("Extracting {}".format(file_name))

            zip_file.extract(file_name, path=root_path)

        # Close the archive
        zip_file.close()
        
def remove_files(config):
    log.debug("Removing data extract .txt files")

    # Sets up location to the extracted files
    date = datetime.utcnow().strftime("%Y-%m-%d")
    root_path = Path(config.get("zips", "save_loc")).child(date)

    # Collects the text files in the directory
    text_files = root_path.listdir("*.txt")

    # Removes all the text files
    for file in text_files:
        file.remove()
    
def create_extract_folders():
    """Creates the folders for holding the extracted files"""
    # Sets script directory to allow absolute path naming (for Cron job)
    # Ubuntu Path
    # root = Path("/", "home", "joshua", "scripts", "dpd_data_extraction")
    # Windows Path
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

    return {"root": root, "eLoc": extractLoc, "pLoc": parseLoc}

def parse_files(locs, names):
    # Array that will collect all parsed extracts
    parseArray = {
        "comp": [],
        "drug": [],
        "form": [],
        "ingred": [],
        "package": [],
        "pharm": [],
        "route": [],
        "schedule": [],
        "status": [],
        "ther": [],
        "vet": []
    }

    # Cycles through each suffix
    for zip in names:
        for file in zip["files"]:
            # File details
            title = file.title
            name = file.name
            ePath = file.ePath

            # Open extracted file and parse it
            with open(ePath, "r", encoding="latin-1") as ext:
                # Treats text file as csv and converts lines to list
                csvFile = csv.reader(ext, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)

                # Read each line of file & output array of parsed text
                for line in csvFile:
                    # Parse list
                    parseArray[title].append(parse_extract_entry(name, line))

        
        print ("")
    
    # Save parsed text to file
    for key in parseArray:
        pPath = locs["pLoc"].child("%s.txt" % key)

        with open(pPath, 'w', newline="") as pFile:
            # Create writer to convert list to text
            csvWriter = csv.writer(pFile, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)

            # Writer all lines to file
            print ("Saving parsed %s entries to file... " % key, end="")
            
            # TO FIX - NOT WRITING TO FILE, BUT IS COLLECTING DATA
            csvWriter.writerows(parseArray[key])
                
            print ("Complete!")
    
    print ("")

    # Delete the extracted text files
    for zip in names:
        for file in zip["files"]:
            # File details
            name = file.name
            ePath = file.ePath

            # Delete the specified file
            print (("Deleting %s... " % name), end="")

            os.remove(ePath)

            print ("Complete!")

    print ("\n")

    return parseArray

