=======================================================
Health Canada Drug Product Database Data Extracton Tool
=======================================================
This program downloads the Health Canada Drug Product Database
(HC DPD) data and then submits it to an API for database upload.

--------------------
Technical Details
--------------------

- The data extracts are saved as text files, but follow a .csv format.
- The general formats of the files can be found on the Health Canada
  Drug Product Database website:
  https://www.canada.ca/en/health-canada/services/drugs-health-products/drug-products/drug-product-database/what-data-extract-drug-product-database.html
- The extracts have some deviations and exceptions from what is
  outlined on the HC DPD; these are documented within this application
  where applicable.

----------------
Running the Tool
----------------

If not already done, the virtual environment needs to be setup. This
is done with the following command:

  $ cd /path/to/the/tool
  $ pipenv install

The tool can be run using the following command::

  $ cd /path/to/the/tool
  $ pipenv run python -m extraction "/path/to/config/file.cfg"

-------------
Running Tests
-------------

To run tests::

  $ pipenv run pytest

To generate coverage report::

  # XML Report
  $ pipenv run pytest --cov test --cov-report xml

  # HTML Report
  $ pipenv run pytest --cov test --cov-report html

---------------
Running Linters
---------------

To run linting::

  # Run Pylint
  $ pipenv run pylint **/**.py

  # Run Pycodestyle
  $ pipenv run pycodestyle **/**.py

-------------------
Documentation Style
-------------------

Docstrings are documented using the reStructuredText format. Details of
this style can be found here:
https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html
