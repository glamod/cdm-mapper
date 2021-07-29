# Common Data Model mapper: `cdm` toolbox

The `cdm-mapper` or (`cdm`) is a [python3](https://www.python.org/) tool designed to map observed variables and its associated metadata from a [data
model](https://cds.climate.copernicus.eu/toolbox/doc/how-to/15_how_to_understand_the_common_data_model/15_how_to_understand_the_common_data_model.html) or models combination to the [C3S CDS Common Data Model](https://glamod.github.io/cdm-obs-documentation/index.html) (CDM) format. 

**Input data**:

- _imodel_: Data elements in a unique [pandas.DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html) objects with its attributes, available in a python dictionary and stored in a `.json` file. 

**Output data**:

- A series of files in ascii format that contains each field from the CDM tables for which a mapping element has been defined. For example:
   - Header table. 
   - Observations table for Sea level Pressure. 
   
For more information on the tables that compose the CDM format read the following [guide](https://glamod.github.io/cdm-obs-documentation/conceptual.html).

**Quick guide**

1. Clone the repository:
   ```
   git clone git@github.com:glamod/cdm-mapper.git --branch master --single-branch cdm
   ```
   > Dont forget to do it as a `--single-branch cdm` otherwise you wont be able to use it as a python module.


2. To install requirements please follow the instructions in the [documentation website](https://glamod.github.io/cdm_mapper_documentation/tool-set-up.html).
    
3. Run a test:
```
import os
import sys
sys.path.append('/path_to_folder_directory_containing_the_cdm_and_mdf_reader_folder/')
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

For more details on how to use the `cdm-mapper` tool see the [documentation](https://glamod.github.io/cdm_mapper_documentation/getting-started.html#).
