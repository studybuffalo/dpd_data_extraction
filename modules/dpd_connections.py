from datetime import datetime
import logging
import requests
from unipath import Path

# Setup logging
log = logging.getLogger(__name__)

def download_zips(session, config):
    extensions = config.get("zips", "extensions").split(",")
    
    # Create the save directory
    date = datetime.utcnow().strftime("%Y-%m-%d")
    root_path = Path(config.get("zips", "save_loc")).child(date)
    root_path.mkdir()
        
    for ext in extensions:
        # Set download and save locations
        url = config.get("zips", "download_{}".format(ext))
        file_name = config.get("zips", "save_{}".format(ext))
        save = root_path.child(file_name)

        # Get the zip file
        log.debug("Requesting {}".format(file_name))
        response = session.get(url)

        # Save the zip file
        with open(save, 'wb') as file:
            log.debug("Saving {}".format(file_name))
            file.write(response.content)
        
def download_extracts(config):
    """Handles download of the data extract files"""
    if config.getboolean("debug", "download"):
        # Setup the session
        session = requests.Session()
        session.headers.update({
            "User-Agent": config.get("robot", "user_agent"),
            "From": config.get("robot", "from")
        })

        # Download the zip files
        download_zips(session, config)
    else:
        log.debug("Debug mode - skip downloading zip files")