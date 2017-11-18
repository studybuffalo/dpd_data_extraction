# Health Canada Drup Product Database Data Extracton Tool
This program downloads the Health Canada Drug Product Database data extracts, normalizes the data, and uploads the data to a Django database.

## Technical Details
* The data extracts are saved as text files, but follow a .csv format.
* There are several typos, spelling mistakes, and other formatting issues that make the data hard to work with. This program tries to correct and standardize the information for better usability.

## Current Status
* Project is being updated and refactored to work with a Django database to provide more functionality for the Study Buffalo website and other projects.
