"""Manages data upload to the API."""
import csv
from operator import itemgetter
from pathlib import Path
from zlib import crc32

from .utils import setup_session


class UploadManager:
    """Manages API calls & helper functions for HC DPD data uplaoad."""
    def __init__(self, config, log):
        self.upload_details = {
            'active_ingredient': {
                'field_order': [
                    'drug_code',
                    'active_ingredient_code',
                    'ingredient',
                    'ingredient_supplied_ind',
                    'strength',
                    'strength_unit',
                    'strength_type',
                    'dosage_value',
                    'base',
                    'dosage_unit',
                    'notes',
                    'ingredient_f',
                    'strength_unit_f',
                    'strength_type_f',
                    'dosage_unit_f',
                ],
                'files': [],
            },
            'biosimilar': {
                'field_order': [
                    'drug_code',
                    'biosimilar_code',
                    'biosimilar_type',
                    'biosimilar_type_f',
                ],
                'files': [],
            },
            'company': {
                'field_order': [
                    'drug_code',
                    'mfr_code',
                    'company_code',
                    'company_name',
                    'company_type',
                    'address_mailing_flag',
                    'address_billing_flag',
                    'address_notification_flag',
                    'address_other',
                    'suite_number',
                    'street_name',
                    'city_name',
                    'province',
                    'country',
                    'postal_code',
                    'post_office_box',
                    'province_f',
                    'country_f',
                ],
                'files': [],
            },
            'drug_product': {
                'field_order': [
                    'drug_code',
                    'product_categorization',
                    'class_e',
                    'drug_identification_number',
                    'brand_name',
                    'descriptor',
                    'pediatric_flag',
                    'accession_number',
                    'number_of_ais',
                    'last_update_date',
                    'ai_group_no',
                    'class_f',
                    'brand_name_f',
                    'descriptor_f',
                ],
                'files': [],
            },
            'form': {
                'field_order': [
                    'drug_code',
                    'pharm_form_code',
                    'pharmaceutical_form',
                    'pharmaceutical_form_f',
                ],
                'files': [],
            },
            'inactive_product': {
                'field_order': [
                    'drug_code',
                    'drug_identification_number',
                    'brand_name',
                    'history_date',
                ],
                'files': [],
            },
            'packaging': {
                'field_order': [
                    'drug_code',
                    'upc',
                    'package_size_unit',
                    'package_type',
                    'package_size',
                    'product_information',
                    'package_size_unit_f',
                    'package_type_f',
                ],
                'files': [],
            },
            'pharmaceutical_standard': {
                'field_order': [
                    'drug_code',
                    'pharmaceutical_std',
                ],
                'files': [],
            },
            'route': {
                'field_order': [
                    'drug_code',
                    'route_of_administration_code',
                    'route_of_administration',
                    'route_of_administration_f',
                ],
                'files': [],
            },
            'schedule': {
                'field_order': [
                    'drug_code',
                    'schedule',
                    'schedule_f',
                ],
                'files': [],
            },
            'status': {
                'field_order': [
                    'drug_code',
                    'current_status_flag',
                    'status',
                    'history_date',
                    'status_f',
                    'lot_number',
                    'expiration_date',
                ],
                'files': [],
            },
            'therapeutic_class': {
                'field_order': [
                    'drug_code',
                    'tc_atc_number',
                    'tc_atc',
                    'tc_atc_f',
                ],
                'files': [],
            },
            'veterinary_species': {
                'field_order': [
                    'drug_code',
                    'vet_species',
                    'vet_sub_species',
                    'vet_species_f',
                ],
                'files': [],
            }
        }
        self.config = config
        self.log = log
        self.save_location = Path(config.download.save_location)
        self.session = self._setup_api_session()

        self._group_extract_files()

    def upload_data(self):
        """Coordinates evaluation and upload of data."""
        # Cycle through each extract type and load the the file data
        self.log.debug('Looping through all extract file groups.')

        for extract_type, details in self.upload_details.items():
            # Open up each file and extract data with a CSV Reader
            data = self.extract_file_data(details['files'], extract_type)

            # Calculate individual row checksums
            row_checksums = self.calculate_row_checksum(data)

            # Calculate the collective checksum for batches of data
            required_uploads = self.identify_required_uploads(row_checksums, extract_type)

    def extract_file_data(self, files, extract_type):
        """Extract data from all the provided files.

            Args:
                files (list): a list of Path objects to the DPD data files.
                extract_type (str): the type of extract files provided.

            Return:
                dict: dictionary of all data from the provides files.
                    Dictionary Key is the drug_code.
                    Value is a list with all data for that drug_code.
        """
        self.log.debug(f'Opening up files for type: "{extract_type}".')

        # Loop through each file to collect data in one dictionary
        data = {}

        for file in files:
            # Open files as CSV to convert data into Python data
            with open(file, newline='', encoding='utf-8') as csv_file:
                self.log.debug(f'Opening file: "{file}".')

                csv_reader = csv.DictReader(
                    csv_file, self.upload_data[extract_type]['field_type'], delimiter=',', quotechar='"'
                )

                for row in csv_reader:
                    data.setdefault(row['drug_code'], []).append(row)

        return data

    def calculate_row_checksums(self, data):
        """Calculates a checksum for each row.

            Args:
                data (list): the DPD file data, with each item being
                    a single row of data

            Returns
                list: list of dicts containing the drug_coode (int)
                    and checksum (str) of each DPD row
        """
        self.log.debug('Calculating checksum for each row')

        # Loop through each row of DPD data to calculate checksum
        checksums = []

        for row in data:
            checksums.append({
                'drug_code': int(row[0]),
                'checksum': calculate_checksum(''.join(row)),
            })

        # Sort checksums by the drug_code and then by checksum value
        self.log.debug('Sorting checksums by drug_code and checksum value.')
        checksums.sort(key=itemgetter('drug_code', 'checksum'))

        return checksums

    def identify_required_uploads(self, file_checksums, extract_type):
            """Identifies which drug codes need to be uploaded.

                Args:
                    file_checksums (dict): the dictionary of row checksum values.
                    extract_type (str): extract type for provided checksums.

                Returns:
                    list: drug_codes that will need to be uploaded.
            """
            self.log.debug ('Comparing extracted checksum data with API data.')

            # Initial setup for checksum calculations
            checksum_step = self.config.upload.checksum_step
            checksum_start = 0
            checksum_stop = checksum_start + checksum_step
            checksum_list = []
            drug_code_list = []

            api_checksums = self._retrieve_comparison_checksums(checksum_step, extract_type)

            for file_checksum in file_checksums:
                drug_code = file_checksum['drug_code']

                if drug_code >= checksum_start and drug_code < checksum_stop:
                    # Drug code is still in range, so add to running list
                    checksum_list.append(file_checksum['checksum'])
                else:
                    # This drug code is out of the current range
                    # Can now run the checksum calculation
                    # Will need to include this current item in the start of the new list
                    # Update the Start & Stop accordingly
                    checksum_string = ''.join(checksum_list)
                    list_checksum = self.calculate_checksum(checksum_string)

                    # Run checksum comparison
                    if checksum_start in comparison_checksums and list_checksum == comparison_checksums[checksum_start]:
                        log.debug(f'No upload required for {extract_type} drug codes {checksum_start} to {checksum_stop - 1}')
                    else:
                        # Need to sort out the upload details here
                        # Perhaps just identify the drug_codes that need to be
                        # uploaded and then go back and upload them?
                        pass

                    # Reset start, stop, and list to prepare for next batch
                    checksum_start = checksum_start + checksum_step
                    checksum_stop = checksum_start + checksum_step
                    checksum_list = [data['checksum']]

            # Loop has finished because there is no more data
            # Can run final checksum calculation & upload
            checksum_string = ''.join(checksum_list)
            list_checksum = self.calculate_checksum(checksum_string)

            return drug_code_list

    @classmethod
    def calculate_checksum(cls, data_string):
        """Calculates a checksum for the provided data.

            Args:
                step (int): the step for each batch of checksums.
                extract_type (str): the extract file type.
                session (obj): a Requests session object.
                config (ojb): a Config object.
                log (obj): a Log object.

            Returns:
                str: the calculated checksum
        """

        # Convert string to bytes
        b_string = data_string.encode('utf-8')

        # Return the checksum
        return str(crc32(b_string))

    def _group_extract_files(self):
        """Groups similar extract files within upload_details."""
        self.log.debug('Grouping similar file types.')

        for download_details in self.config.download.files:
            self.upload_details[download_details['extract_name']]['files'].append(
                self.save_location / download_details['save_name']
            )

    def _setup_api_session(self):
        """Sets up a Requests session for API calls."""
        extra_headers = {
            'Authorization': f'Token {self.config.upload.api_token}'
        }
        return setup_session(self.config, self.log, extra_headers)

    def _make_api_call(self, url, method='get', params={}):
        """Makes call to API and returns response.

            Args:
                session (obj): a Requests session object.
                url (str): the URL to make the API call to.
                method (str): the HTTP method to use
                params (dict): any additional URL params to include.

            Returns
                dict: the JSON response dictionary.
        """
        # Make API call
        if method == 'post':
            response = self.session.post(url, params=params)
        else:
            response = self.session.get(url, params=params)

        # Raise any HTTP errors (if they occurred)
        response.raise_for_status()

        # Return JSON response details
        return response.json()

    def _retrieve_comparison_checksums(self, step, extract_type):
        """Retrieves the list of comparison checksums from API"""
        # Make initial API Call
        self.log.debug(f'Retrieving checksums for "{extract_type}" (step = {step})')

        get_params = {'step': step, 'source': extract_type}
        response = self._make_api_call(
            self.config.upload.api_checksum_url, 'get', get_params
        )
        data_exists = True

        # Compile response details and then make next API call
        checksum_details = {}

        # Continue API calls until all results retrieved (i.e. no next URL)
        while data_exists:
            # Compile response into a dict with drug_code_start as key
            for checksum in response['results']:
                checksum_details[checksum['drug_code_start']] = checksum

            # Check if there are more results to retrieve
            data_exists = bool(response['next'])

            if data_exists:
                response = self._make_api_call(response['next'], 'get')

        return checksum_details

    def _upload_data(self):
        """SOMETHING"""

def upload_data(config, log):
    """Coordinate upload of extracted text data to API."""
    # Setup manager to coordinate data upload
    manager = UploadManager(config, log)

    manager.upload_data()
