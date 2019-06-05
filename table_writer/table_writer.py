#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
import numpy as np
from io import StringIO
import importlib
import glob
from cdm import properties
from cdm.common import pandas_TextParser_hdlr
from cdm.common import logging_hdlr
#from ..lib.tables import tables_hdlr

module_path = os.path.dirname(os.path.abspath(__file__))

def print_integer(data,null_label):
    data.iloc[np.where(data.notna())] = data.iloc[np.where(data.notna())].astype(int).astype(str)
    data.iloc[np.where(data.isna())] = null_label
    return data

def print_float(data,null_label, decimal_places = None):
    decimal_places = properties.default_decimal_places if not decimal_places else decimal_places
    format_float='{:.' + str(decimal_places) + 'f}'
    data.iloc[np.where(data.notna())] = data.iloc[np.where(data.notna())].apply(format_float.format)
    data.iloc[np.where(data.isna())] = null_label
    return data

def print_datetime_tz(data,null_label):
    return 'datetime_tz'

def print_varchar(data,null_label):
    data.iloc[np.where(data.notna())] = data.iloc[np.where(data.notna())].astype(str)
    data.iloc[np.where(data.isna())] = null_label
    return data

def print_integer_array(data,null_label):
    return data.apply(print_integer_array_i,null_label=null_label)

def print_float_array(data,null_label, decimal_places = None):
     return 'float array not defined in printers'

def print_datetime_tz_array(data,null_label):
    return 'datetime tz array not defined in printers'

def print_varchar_array(data,null_label):
    return data.apply(print_varchar_array_i,null_label=null_label)

printers = {'int': print_integer, 'numeric': print_float, 'varchar':print_varchar,
            'timestamp with timezone': print_datetime_tz,
            'int[]': print_integer_array, 'numeric[]': print_float_array,
            'varchar[]':print_varchar_array,
            'timestamp with timezone[]': print_datetime_tz_array}

iprinters_kwargs = {'numeric':['decimal_places'],
                   'numeric[]':['decimal_places']}


def print_integer_array_i(row,null_label = None):
    if row==row:
        row = eval(row)
        row = row if isinstance(row,list) else [row]
        string = ','.join(filter(bool,[ str(int(x)) for x in row if np.isfinite(x)]))
        if len(string) > 0:
            return '{' + string + '}'
        else:
            return null_label
    else:
        return null_label

def print_varchar_array_i(row,null_label = None):
    if row==row:
        row = eval(row)
        row = row if isinstance(row,list) else [row]
        string = ','.join(filter(bool,x))
        if len(string) > 0:
            return '{' + string + '}'
        else:
            return null_label
    else:
        return null_label

def table_to_ascii(table, table_atts, log_level = 'INFO', delimiter = '|', null_label = 'null', extension = 'psv', full_table = True):
    logger = logging_hdlr.init_logger(__name__,level = log_level)
#   Check input:
#   table either df or parser
#   table columns in table_atts
    # All this change if iterating over chunks!!!! :()
    table = [table]
    for itable in table:
        # drop records with no 'observation_value'
        empty_table = False
        if 'observation_value' in itable:
            itable.dropna(subset=['observation_value'],inplace=True)
            empty_table = True if len(itable) == 0 else False
        elif 'observation_value' in table_atts.keys():
            empty_table = True  
        if empty_table:
            logger.warning('No observation values in table')
            ascii_table = pd.DataFrame(columns = table_atts.keys(), dtype = 'object')
            break    
        ascii_table = pd.DataFrame(index = itable.index, columns = table_atts.keys(), dtype = 'object')
        for iele in table_atts.keys():
            if iele in itable:
                itype = table_atts.get(iele).get('data_type')
                if printers.get(itype):
                    iprinter_kwargs = iprinters_kwargs.get(itype)
                    if iprinter_kwargs:
                        kwargs = { x:table_atts.get(iele).get(x) for x in iprinter_kwargs}
                    else:
                        kwargs = {}
                    ascii_table[iele] = printers.get(itype)(itable[iele], null_label, **kwargs)
                else:
                    logger.error('No printer defined for element {}'.format(iele))
            else:
                ascii_table[iele] = null_label

    # Now clean final ascii_table from empty columns if full_table = False (TBI)
    
#                logger.error('No printer defined for cdm element \'{0}\' data type \'{1}\''.format(iele,itype))

    return ascii_table

def cdm_to_ascii( cdm, log_level = 'INFO', delimiter = '|', null_label = 'null', extension = 'psv',out_dir = None, suffix = None, prefix = None ):
    logger = logging_hdlr.init_logger(__name__,level = log_level)
    # Check input:
#    cdm must be a dictionary
#    keys must be in properties.cdm_tables
#    'atts' and 'data' in cdm[table]
    # Write thing:
    extension = '.' + extension
    for table in cdm.keys():
        logger.info('Printing table {}'.format(table))
        filename = os.path.join(out_dir,'-'.join(filter(bool,[prefix,table,suffix])) + extension )
        ascii_table = table_to_ascii(cdm[table]['data'], cdm[table]['atts'], delimiter = delimiter, null_label= null_label, extension = extension, log_level = log_level)
        ascii_table.to_csv(filename, index = False, sep = delimiter)
    return ascii_table
