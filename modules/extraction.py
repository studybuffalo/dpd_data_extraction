import zipfile
import datetime
import csv
import math

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

        self.title = title
        self.name = name
        self.ePath = ePath

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

