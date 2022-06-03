"""Manages extraction of DPD data from extract files."""
# from datetime import datetime
# import logging
# from unipath import Path
# import zipfile

# import csv
# import math

# # Setup logging
# log = logging.getLogger(__name__)

# def get_extensions(config):
#     """Returns a list of extensions"""
#     # Get the extension list
#     extensions = config.get("zips", "extensions").split(",")

#     # Trim any white space (incase the comma was followed by a space)
#     return [e.strip() for e in extensions]

# def get_root_path(config):
#     """Constructs a path to the directory containg the data extracts"""
#     date = datetime.utcnow().strftime("%Y-%m-%d")
#     root_path = Path(config.get("zips", "save_loc")).child(date)

#     return root_path

# def get_data_files(config, ext):
#     """Returns a list of file names for the provided extension"""
#     data_files = config.get("files_{}".format(ext), "files").split(",")

#     # Trim any white space (incase the comma was followed by a space)
#     return [f.strip() for f in data_files]

# def get_django_model(config, ext, file):
#     """Returns the django model data for the provided file"""
#     django_model = config.get("files_{}".format(ext), file)
#     django_origin = config.get("files_{}".format(ext), "origin_file")

#     return {"model": django_model, "origin": django_origin}


# def unzip_files(config):
#     """Unzips the download files"""
#     extensions = get_extensions(config)

#     # Sets up location to the zip files
#     root_path = get_root_path(config)

#     # Cycle through all the extensions and save the files for the zip
#     for ext in extensions:
#         zip_name = config.get("zips", "save_{}".format(ext))

#         # Unzip the zip file
#         log.debug("Unzipping {}".format(zip_name))

#         zip_path = root_path.child(zip_name)
#         zip_file = zipfile.ZipFile(zip_path, "r")

#         # Get the names of the data files in the zip
#         data_files = get_data_files(config, ext)

#         # Cycle through each file name and save the file
#         for file in data_files:
#             file_name = "{}.txt".format(file)

#             # Extract the text file from the archive
#             log.debug("Extracting {}".format(file_name))

#             zip_file.extract(file_name, path=root_path)

#         # Close the archive
#         zip_file.close()

# def extract_dpd_data(config):
#     """Extracts the data from the data extract files"""
#     # Sets up location to the extracted files
#     root_path = get_root_path(config)

#     # Get the extensions of the downloaded files
#     extensions = get_extensions(config)

#     # Set up the dictionary to hold the extracted data
#     dpd_data = {}

#     # Cycle through all the extensions to locate the .txt files
#     for ext in extensions:
#         # Add the extension to the dictionary
#         dpd_data[ext] = {}

#         # Get the names of the data files in the zip
#         data_files = get_data_files(config, ext)

#         for data_file in data_files:
#             # Set the path to the data file
#             file_name = "{}.txt".format(data_file)
#             file_path = root_path.child(file_name)

#             # Get the Django model associated with this file
#             django_model_data = get_django_model(config, ext, data_file)

#             # Add the file name to the extension dictionary
#             dpd_data[ext][data_file] = {
#                 "model": django_model_data["model"],
#                 "origin": django_model_data["origin"],
#                 "data": []
#             }

#             # Open extracted file and parse it
#             with open(file_path, "r", encoding="utf8") as file:
#                 log.debug("Extracting data from {}".format(file_name))

#                 # Opens the file as a .csv
#                 csv_file = csv.reader(
#                     file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
#                 )

#                 # Read each line and append it to the list
#                 for line in csv_file:
#                     dpd_data[ext][data_file]["data"].append(line)

#     # Return the completed dictionary
#     return dpd_data

# def remove_files(config):
#     """Removes all the text files in the data extract directory"""
#     log.debug("Removing data extract .txt files")

#     # Sets up location to the extracted files
#     root_path = get_root_path(config)

#     # Collects the text files in the directory
#     text_files = root_path.listdir("*.txt")

#     # Removes all the text files
#     for file in text_files:
#         file.remove()
