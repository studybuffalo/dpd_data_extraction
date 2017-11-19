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

