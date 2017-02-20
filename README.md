# Health Canada Drup Product Database Data Extracton Tool
This program downloads the Health Canada Drug Product Database data extracts and uploads them to a mysql database.

## Technical Details
* The data extracts are saved as text files, but follow a .csv format.
* There are several typos, spelling mistakes, and other formatting issues that make the data hard to work with. This program tries to correct and standardize the information for better usability
* The program does not keep a history of all the data in the database, but all data extracts are saved for audit/tracking purposes
* This program was built in Python 2.7 and is now being streamlined for 3.5.

## Background Information
* The goal of this program is make a database that can reliably be used to identify medications available in Canada.
* This database is hoped to serve as a standard reference of medications that other programs can be built off of or tied to.
* This was the second python project I created, so there are likely some significant inefficiencies, poor documentation, and non-standard practices. The goal at some point will be to refactor everything.
