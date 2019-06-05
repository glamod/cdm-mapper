#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IN:
# Registered data model name
# Data frame or pandas pandas.io.parsers.TextFileReader with data model to map
# atts with data model definition: atts = { x:attributes for x in elements }, where x is tuple (sections) or just name (no sections),
# including _datetime
#
# MAP for iModel:
# In mappings/lib/imodel
#
# Data frame column index, data_atts and mapping structure must match
#
# HOW:
# Goes through defined mappings for imodel and maps in a single data frame?
# Give as optional input what you want to map?
# Only define mappings for things that are mappable, don't create a mapping that is 90% empty!
# Can mappings be interdependent: obs table gets something in header table? Then we could not
# do independent mapping: create fully independent mappings!
# Ouput is, again, multiindexed at the columns: (table,element)

# print(sys.getsizeof(OBEJCT_NAME_HERE))

#import logging
import os
import pandas as pd
import numpy as np
from io import StringIO
import importlib
import glob
from cdm import properties
from cdm.common import pandas_TextParser_hdlr
from cdm.common import logging_hdlr
from cdm.lib.tables import tables_hdlr
from cdm.lib.mappings import mappings_hdlr

module_path = os.path.dirname(os.path.abspath(__file__))

def _map(data, data_atts, imodel, cdm_subset = None, log_level = 'INFO'):
    logger = logging_hdlr.init_logger(__name__,level = log_level)
    # Get mappings and functions and code_tables
    try:
        imodel_functions_mdl_tree = mappings_hdlr.get_functions_module_path(imodel)
        if len(imodel_functions_mdl_tree)>0:
            imodel_functions_mdl = importlib.import_module(imodel_functions_mdl_tree, package=None)
            imodel_functions = imodel_functions_mdl.mapping_functions(data_atts)
        else:
            logger.warning('No mapping functions found for model {}'.format(imodel))
        imodel_maps = mappings_hdlr.load_tables_maps(imodel, cdm_subset = cdm_subset)
        if len(imodel_maps) < 1:
                logger.error('No mappings found for model {}'.format(imodel))
                return
        imodel_code_tables = mappings_hdlr.load_code_tables_maps(imodel)
        if len(imodel_code_tables) < 1:
                logger.warning('No code table mappings found for model {}'.format(imodel))
    except Exception as e:
        logger.debug('Error loading {} cdm mappings'.format(imodel), exc_info=True)
        return
    if not imodel_maps:
        logger.error('Error loading {} cdm mappings'.format(imodel))
        return
    cdm_atts = tables_hdlr.load_tables()
    not_in_tool = [ x for x in imodel_maps.keys() if x not in cdm_atts.keys() ]
    if len(not_in_tool)>0:
        if any(not_in_tool):
            logger.error('One or more tables registered in the data model is not supported by the tool: {}'.format(",".join(not_in_tool)))
            logger.info('CDM tables registered in the tool in properties.py are: {}'.format(",".join(properties.cdm_tables)))
            return
    cdm_tables = { k:{'buffer':StringIO(),'atts':cdm_atts.get(k)} for k in imodel_maps.keys() }
    ### cdm elements dtypes
    # Mail sent may 7th to Dave. Are the types there real SQL types, or just approximations?
    # Numeric type in table definition not useful here to define floats with a specific precision
    # We should be able to use those definitions. Keep in mind that arrays are object type in pandas!
    # Remember any int and float (int, numeric) need to be tied for the parser!!!!
    # Also datetimes!
    # Until CDM table definition gets clarified:
    # We map from cdm table definition types to those in properties.pandas_dtypes.get('from_sql'), else: 'object'
    # We update to df column dtype if is of float type
    date_columns = { x:[] for x in imodel_maps.keys()}
    out_dtypes = { x:{} for x in imodel_maps.keys()}
    for table in out_dtypes:
        # get cdm element dtypes from table definition. Get method so that this does not
        # break if element defined in mapping is not in cdm table definition
        out_dtypes[table].update({ x:cdm_atts.get(table,{}).get(x,{}).get('data_type') for x in imodel_maps[table].keys()})
        # map those types (SQL) to pandas types
        date_columns[table].extend([ i for i,x in enumerate(list(out_dtypes[table].keys())) if 'timestamp' in out_dtypes[table].get(x) ])
        out_dtypes[table].update({ k:properties.pandas_dtypes.get('from_sql').get(v,'object') for k,v in out_dtypes[table].items()})
    for idata in data:
        cols = [x for x in idata]
        for table,mapping in imodel_maps.items():
            table_df_i = pd.DataFrame(index = idata.index, columns = mapping.keys())
            logger.debug('Table: {}'.format(table))
            for cdm_key,imapping in mapping.items():
                logger.debug('\tElement: {}'.format(cdm_key))
                [elements,transform,kwargs,code_table,default,fill_value, decimal_places] = [imapping.get('elements'),
                                                            imapping.get('transform'),imapping.get('kwargs'),
                                                            imapping.get('code_table'),imapping.get('default'),
                                                            imapping.get('fill_value'), imapping.get('decimal_places')]

                if elements:
                    # make sure they are clean and conform to their atts (tie dtypes)
                    # we'll only let map if row complete so mapping functions do not need to worry about handling NA
                    # Also make sure to_map object is:
                    #   - a pd.Series if 1 element from imodel to cdm
                    #   - a pd.DataFrame if >1 elements from imodel to cdm
                    # This is so that mapping functions can work knowing the input type!
                    logger.debug('\telements: {}'.format(" ".join([ str(x) for x in elements ])))
                    missing_els = [x for x in elements if x not in cols]
                    if len(missing_els)>0:
                        logger.warning('Following elements from data model missing from input data: {0} to map {1} '.format(",".join([str(x) for x in missing_els]),cdm_key))
                        continue
                    to_map_types = { element:properties.pandas_dtypes.get('from_atts').get(data_atts.get(element).get('column_type')) for element in elements }
                    notna_idx = np.where(idata[elements].notna().all(axis = 1))[0]
                    to_map = idata[elements].iloc[notna_idx].astype(to_map_types)
                    if len(elements) == 1:
                        to_map = to_map.iloc[:,0]
                if transform:
                    kwargs = {} if not kwargs else kwargs
                    logger.debug('\tkwargs: {}'.format(",".join(list(kwargs.keys()))))
                    trans = eval('imodel_functions.' + transform)
                    logger.debug('\ttransform: {}'.format(transform))
                    if elements:
                        a = trans(to_map,**kwargs)
                        logger.debug("Transform type: {}".format(type(a)))
                        table_df_i.loc[notna_idx,cdm_key] = a #trans(to_map,**kwargs)
                    else:
                        table_df_i[cdm_key] = trans(**kwargs)
                elif code_table:
#                    https://stackoverflow.com/questions/45161220/how-to-map-a-pandas-dataframe-column-to-a-nested-dictionary?rq=1
#                    Approach that does not work when it is not nested...so just try and assume not nested if fails
                    # Prepare code_table
                    table_map = imodel_code_tables.get(code_table)
                    try:
                        s = pd.DataFrame(table_map).unstack().rename_axis((elements)).rename('cdm')
                    except:
                        s = pd.DataFrame(table_map.values(),index = table_map.keys(),columns = ['cdm']).rename_axis((elements))  
                    # Make sure what we try to map is a df, not a series (method join is only on df...)
                    try:
                        to_map = to_map.to_frame()
                    except:
                        pass
                    table_df_i[cdm_key] = to_map.astype(str).join(s, on=elements)['cdm'] # here indexes well inherited as opposed to trans() above
                elif elements:
                    table_df_i[cdm_key] = to_map
                elif default is not None: #(vakue = 0 evals to False!!)
                    if isinstance(default,list):
                        table_df_i[cdm_key] = [default]*len(table_df_i.index)
                    else:
                        table_df_i[cdm_key] = default
                else:
                    if fill_value is None:
                        logger.warning('Nothing defined for cdm element {}'.format(cdm_key))

                if fill_value is not None:
                    table_df_i[cdm_key].fillna(value = fill_value,inplace = True)

                if decimal_places is not None:
                    if isinstance(decimal_places,int):
                        cdm_tables[table]['atts'][cdm_key].update({'decimal_places':decimal_places})
                    else:
                        cdm_tables[table]['atts'][cdm_key].update({'decimal_places':eval('imodel_functions.' + decimal_places)(elements)})
            # think that NaN also casts float to float64....!keep floats of lower precision to its original one
            out_dtypes[table].update({ i:table_df_i[i].dtype for i in table_df_i if table_df_i[i].dtype in properties.numpy_floats and out_dtypes[table].get(i) not in properties.numpy_floats})
            table_df_i.to_csv(cdm_tables[table]['buffer'], header = False, index = False, mode = 'a')

    for table in cdm_tables.keys():
        # Convert dtime to object to be parsed by the reader
        cdm_tables[table]['buffer'].seek(0)
        cdm_tables[table]['data'] = pd.read_csv(cdm_tables[table]['buffer'],names = out_dtypes[table].keys(), dtype = out_dtypes[table], parse_dates = date_columns[table])
        cdm_tables[table]['buffer'].close()
        cdm_tables[table].pop('buffer')

    return cdm_tables


def map_model( imodel, data, data_atts, chunksize = None, log_level = 'INFO', cdm_subset = None):
    logger = logging_hdlr.init_logger(__name__,level = log_level)
    # Check we have imodel registered, leave otherwise
    if imodel not in properties.supported_models:
        logger.error('Input data model ''{}'' not supported'.format(imodel))
        return

    # Check input data type and content (empty?)
    # ake sure data is an iterable
    if isinstance(data,pd.DataFrame):
        logger.debug('Input data is a pd.DataFrame')
        if len(data) == 0:
            logger.error('Input data is empty')
            return
        else:
            data = [data]
            elements = [ x for x in data[0] ]
    elif isinstance(data,pd.io.parsers.TextFileReader):
        logger.debug('Input is a pd.TextFileReader')
        not_empty,data = pandas_TextParser_hdlr.is_not_empty(data)
        if not not_empty:
            logger.error('Input data is empty')
            return
        else:
            elements = data.orig_options['names']
    else:
        logger.error('Input data type ''{}'' not supported'.format(type(data)))
        return

    # Check data_atts and data coherence: works but deactivated until we decide
    # what to do with the (_datetime) column from the reader....
#    if not all([ x if x in data_atts.keys() else None for x in elements ]):
#        logger.error('Input data and data attributes are not coherent\nData elements ({}) not in attributtes'.format(",".join([ str(x) for x in elements if x not in data_atts.keys()])))
#        return

    # Map thing:
    data_cdm = _map(data, data_atts, imodel, cdm_subset = cdm_subset, log_level = log_level)

    return data_cdm
