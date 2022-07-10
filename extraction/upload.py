"""Manages data upload to the API."""
import csv
from datetime import datetime
from operator import itemgetter
from pathlib import Path
from zlib import crc32

from requests.exceptions import HTTPError

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
                    'biosimilar_type',
                    'biosimilar_type_f',
                    'biosimilar_code',
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
                    'brand_name_f',
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
            row_checksums = self.calculate_row_checksums(data)

            # Identify which drug codes require upload
            required_uploads = self.identify_required_uploads(row_checksums, extract_type)

            # Upload the required drug_codes
            self.submit_upload_data(data, required_uploads, extract_type)

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
                    csv_file, self.upload_details[extract_type]['field_order'], delimiter=',', quotechar='"'
                )

                for row in csv_reader:
                    data.setdefault(int(row['drug_code']), []).append(row)

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
        file_checksums = []

        for drug_code, rows in data.items():
            for row in rows:
                file_checksums.append({
                    'drug_code': drug_code,
                    'checksum': self.calculate_checksum(
                        ''.join([value for _, value in row.items()])
                    ),
                })

        # Sort checksums by the drug_code and then by checksum value
        self.log.debug('Sorting checksums by drug_code and checksum value.')
        file_checksums.sort(key=itemgetter('drug_code', 'checksum'))

        # Group checksums into groups based on the specified step
        # Initial setup for checksum grouping
        checksum_step = self.config.upload.checksum_step
        checksum_start = 0
        checksum_stop = checksum_start + checksum_step
        checksum_groups = {}

        # Loop through all checksums & group into batches of the step
        for file_checksum in file_checksums:
            if file_checksum['drug_code'] >= checksum_stop:
                # Drug code out of range - reset variables for next group
                checksum_start = checksum_start + checksum_step
                checksum_stop = checksum_start + checksum_step

            checksum_groups.setdefault(checksum_start, []).append(file_checksum)

        return checksum_groups

    def identify_required_uploads(self, file_checksums, extract_type):
            """Identifies which drug codes need to be uploaded.

                Args:
                    file_checksums (dict): the dictionary of grouped checksum values.
                    extract_type (str): extract type for provided checksums.

                Returns:
                    list: drug_codes that will need to be uploaded.
            """
            # Retrieve API checksum values for comparison
            self.log.debug(f'Retrieve comparison checksums for "{extract_type}" file type.')

            checksum_step = self.config.upload.checksum_step
            api_checksums = self._retrieve_comparison_checksums(checksum_step, extract_type)

            # Loop through grouped file checksums to identify drug codes requiring upload
            drug_code_list = []
            temp_drug_code_list = []

            for drug_code_start, rows in file_checksums.items():
                temp_checksum_list = []
                temp_drug_code_list = []

                # Iterate through items in group to calculate checksum
                for row in rows:
                    temp_checksum_list.append(row['checksum'])
                    temp_drug_code_list.append(row['drug_code'])

                # Calculate checksum for group
                group_checksum = self.calculate_checksum(''.join(temp_checksum_list))

                # Run checksum comparison
                if drug_code_start in api_checksums and group_checksum == api_checksums[drug_code_start]:
                    # Match found with API checksums - no upload required
                    self.log.debug(
                        f'No upload required for drug code start = "{drug_code_start}" and step = "{checksum_step}")'
                    )
                else:
                    # No checksum match found - record drug codes for upload
                    drug_code_list.extend(temp_drug_code_list)

            return drug_code_list

    def submit_upload_data(self, data, required_drug_codes, extract_type):
        """Uploads the required drug codes.

            Args:
                data (dict): dict of drug codes (keys) and DPD data.
                required_drug_codes (list): all drug_codes for upload.
                extract_type (str): the extract type for this data.
        """
        # Iterate through required_drug_codes & collate data for upload
        self.log.debug(f'Uploading data for "{extract_type}" data.')

        # Setup to allow batching of uploads per the upload step
        upload_data = []
        drug_code_step = self.config.upload.upload_step
        drug_code_start = 0
        drug_code_stop = drug_code_start + drug_code_step

        for drug_code in required_drug_codes:
            print(drug_code)
            if drug_code >= drug_code_stop:
                print("upload")
                # Drug code out of range - submit upload
                self._make_api_call(
                    self.config.upload.api_upload_url,
                    'post',
                    data={extract_type: upload_data},
                )

                # Reset variables for next batch
                upload_data = []
                drug_code_start = drug_code_start + drug_code_step
                drug_code_stop = drug_code_start + drug_code_step

            upload_data.extend(data[drug_code])

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

    def _make_api_call(self, url, method='get', data={}):
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
            response = self.session.post(url, json=data)
        else:
            response = self.session.get(url, params=data)

        # Raise any HTTP errors (if they occurred)
        if response.status_code == 400:
            raise HTTPError(f'400 Error with request for url {url}: {response.json()}')

        if response.status_code == 500:
            raise HTTPError(f'500 Error with request for url {url}: {response.json()}')

        # Raise any other errors not explicitly caught
        response.raise_for_status()

        # Return JSON response details
        return response.json()

    def _retrieve_comparison_checksums(self, step, extract_type):
        """Retrieves the list of comparison checksums from API"""
        self.log.debug(f'Retrieving checksums for "{extract_type}" (step = {step})')

        # Setup initial details to initiate while loop
        api_url = f'{self.config.upload.api_checksum_url}?step={step}&source={extract_type}'
        checksum_details = {}

        # Continue API calls until all results retrieved (i.e. no next URL)
        while api_url:
            response = self._make_api_call(api_url, 'get')

            # Compile response into a dict with drug_code_start as key
            for checksum in response['results']:
                checksum_details[checksum['drug_code_start']] = checksum

            # Check if there are more results to retrieve
            api_url = response['next']

        return checksum_details


def upload_data(config, log):
    """Coordinate upload of extracted text data to API."""
    # Check if running in debug mode
    if config.upload.debug:
        log.debug('Upload Debug Mode: skipping API upload.')
    else:
        # Setup manager to coordinate data upload
        manager = UploadManager(config, log)

        manager.upload_data()
