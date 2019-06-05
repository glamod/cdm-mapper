import os
import glob

mappings_lib = os.path.join(os.path.dirname(__file__),'lib','mappings')
supported_models = [ x.split("/")[-1] for x in glob.glob(mappings_lib + "/*")]

cdm_tables = ['header','observations_at','observations_sst',
              'observations_dpt','observations_wbt',
              'observations_wd','observations_ws',
              'observations_slp']

# Data types ------------------------------------------------------------------
numpy_integers = ['int8','int16','int32','int64','uint8','uint16','uint32','uint64']
numpy_floats = ['float16','float32','float64']
numeric_types = numpy_integers.copy()
numeric_types.extend(numpy_floats)

object_types = ['str','object','key','datetime']

data_types = object_types.copy()
data_types.extend(numpy_integers)
data_types.extend(numpy_floats)

pandas_dtypes = {}
pandas_dtypes['from_atts'] = {}
for dtype in object_types:
    pandas_dtypes['from_atts'][dtype] = 'object'
pandas_dtypes['from_atts'].update({ x:x for x in numeric_types })

pandas_dtypes['from_sql'] = {}
pandas_dtypes['from_sql']['timestamp with timezone'] = 'object'
pandas_dtypes['from_sql']['numeric'] = 'float16'
pandas_dtypes['from_sql']['int'] = 'int'

default_decimal_places = 5
