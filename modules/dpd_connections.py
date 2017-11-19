from urllib import robotparser
from urllib import request

def get_permission(robotFile):
    # Get permission to access the Health Canada website
    print ("CHECKING FOR PERMISSION TO RUN")
    print ("------------------------------")

    """Checks the specified robot.txt file for access permission."""
    robot = robotparser.RobotFileParser()
    robot.set_url(robotFile)
    robot.read()
    
    print ("Checking robots.txt... ", end="")

    can_crawl = robot.can_fetch(
		"Study Buffalo Data Extraction (http://www.studybuffalo.com/dataextraction/)",
		"https://idbl.ab.bluecross.ca/idbl/load.do")
    
    if can_crawl == True:
        print ("Permission Granted!\n\n")
    else:
        print ("Permission Rejected.")

    return can_crawl
