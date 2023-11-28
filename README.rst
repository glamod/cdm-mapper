=========================================
Common Data Model mapper: ``cdm`` toolbox
=========================================

+----------------------------+-----------------------------------------------------+
| Versions                   | |pypi|                                              |
+----------------------------+-----------------------------------------------------+
| Documentation and Support  | |docs| |versions|                                   |
+----------------------------+-----------------------------------------------------+
| Open Source                | |license|                                           |
+----------------------------+-----------------------------------------------------+
| Coding Standards           | |black| |pre-commit|                                |
+----------------------------+-----------------------------------------------------+
| Development Status         | |status| |build| |coveralls|                        |
+----------------------------+-----------------------------------------------------+

The `cdm-mapper` or (`cdm`) is a python_ tool designed to map observed variables and its associated metadata from a `data
model`_or models combination to the `C3S CDS Common Data Model`_ (CDM) format. 

**Input data**:

- _imodel_: Data elements in a unique pandas.DataFrame_ objects with its attributes, available in a python dictionary and stored in a `.json` file. 

**Output data**:

- A series of files in ascii format that contains each field from the CDM tables for which a mapping element has been defined. For example:
   - Header table. 
   - Observations table for Sea level Pressure. 
   
For more information on the tables that compose the CDM format read the following guide_.

Installation
------------

You can install the package directly with pip:

.. code-block:: console

     pip install  cdm_mapper

If you want to contribute, I recommend cloning the repository and installing the package in development mode, e.g.

.. code-block:: console

    git clone https://github.com/glamod/cdm_mapper
    cd mdf_reader
    pip install -e .

This will install the package but you can still edit it and you don't need the package in your :code:`PYTHONPATH`
   
Run a test
----------

import os
import cdm
import json
import mdf_reader
import warnings
warnings.filterwarnings('ignore')
```
4. Read imma data with the `mdf_reader.read()` and copy the data attributes 
```
schema = 'imma1_d704'
data_file_path = '125-704_1879-01_subset.imma'

data_raw = mdf_reader.read(data_file_path, data_model = schema)
attributes = data_raw.atts.copy()
```

5. Map this data to a CDM build for the same deck (in this case deck 704: US Marine Metereological Journal collection of data)
```
name_of_model = 'icoads_r3000_d704'

cdm_dict = cdm.map_model(name_of_model, data_raw.data, attributes, 
                         cdm_subset = None, log_level = 'DEBUG')

```

For more details on how to use the `cdm-mapper` tool see the following `jupyter notebook`_.

6. For a detailed guide on how to build a cdm and write the output of the `cdm.map_model()` function in ascii see the `user guide`_.

.. _python: https://www.python.org

.. _data model: https://cds.climate.copernicus.eu/toolbox/doc/how-to/15_how_to_understand_the_common_data_model/15_how_to_understand_the_common_data_model.html

.. _C3S CDS Common Data Model: https://git.noc.ac.uk/brecinosrivas/cdm-mapper/-/blob/master/docs/cdm_latest.pdf

.. _pandas.DataFrame: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html

.. _guide: https://git.noc.ac.uk/brecinosrivas/cdm-mapper/-/blob/master/docs/cdm_latest.pdf

.. _jupyter notebook: https://git.noc.ac.uk/brecinosrivas/cdm-mapper/-/blob/master/docs/notebooks/CDM_mapper_example_deck704.ipynb

.. _user guide: https://git.noc.ac.uk/brecinosrivas/cdm-mapper/-/tree/master/docs

.. |pypi| image:: https://img.shields.io/pypi/v/mdf_reader.svg
        :target: https://pypi.python.org/pypi/mdf_reader
        :alt: Python Package Index Build

.. |docs| image:: https://readthedocs.org/projects/mdf_reader/badge/?version=latest
        :target: https://mdf-reader.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status

.. |versions| image:: https://img.shields.io/pypi/pyversions/mdf_reader.svg
        :target: https://pypi.python.org/pypi/mdf_reader
        :alt: Supported Python Versions

.. |license| image:: https://img.shields.io/github/license/glamod/mdf_reader.svg
        :target: https://github.com/glamod/mdf_reader/blob/master/LICENSE
        :alt: License

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
        :target: https://github.com/psf/black
        :alt: Python Black

.. |pre-commit| image:: https://results.pre-commit.ci/badge/github/glamod/mdf_reader/master.svg
   :target: https://results.pre-commit.ci/latest/github/glamod/mdf_reader/master
   :alt: pre-commit.ci status

.. |status| image:: https://www.repostatus.org/badges/latest/active.svg
        :target: https://www.repostatus.org/#active
        :alt: Project Status: Active – The project has reached a stable, usable state and is being actively developed.

.. |build| image:: https://github.com/glamod/mdf_reader/actions/workflows/ci.yml/badge.svg
        :target: https://github.com/glamod/mdf_reader/actions/workflows/ci.yml
        :alt: Build Status

.. |coveralls| image:: https://codecov.io/gh/glamod/mdf_reader/branch/master/graph/badge.svg
	:target: https://codecov.io/gh/glamod/mdf_reader
	:alt: Coveralls

.. |zenodo| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.7762679.svg
        :target: https://doi.org/10.5281/zenodo.7762679
 	:alt:   DOI