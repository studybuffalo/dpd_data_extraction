"""Manages data upload to the API."""


def upload_data(config, log):
    """Coordinate upload of extracted text data to API."""
    # Read through each group of files
    # Group data together by source across all status types
    # Calculate checksums for data
    # Compare calculated checksum against DB
    # When mismatch occurs, upload new data
