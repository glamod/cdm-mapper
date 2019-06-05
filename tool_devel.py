#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 13:45:38 2019

Look into validation results

@author: iregon
"""

import os
import sys
sys.path.append('/Users/iregon/dessaps')
import mdf_reader
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import cdm


# Input -----------------------------------------------------------------------
data_file = 'meds_2010-07.imma'
main_model = 'imma1'
sections = ['core','c1','c98','c99']
supp_model = 'cisdm_dbo_imma1'
supp_section = 'c99'
mapping = 'imma1_cisdm_dbo'


# Settings --------------------------------------------------------------------
reader_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'mdf_reader')
data_path = os.path.join(reader_path,'tests','data')
data_file_path = os.path.join(data_path,data_file)
main_schema = mdf_reader.schemas.read_schema(schema_name = main_model)

if supp_model:
    supp_schema = mdf_reader.schemas.read_schema(schema_name = supp_model)

# Read ------------------------------------------------------------------------
imodel = mdf_reader.read(data_file_path, sections = sections, data_model = main_model, supp_section = supp_section ,supp_model = supp_model )

imodel['data'].loc[0,('c1','PT')]=np.nan
imodel['data'].loc[4,('c1','PT')]=np.nan
imodel['data'].loc[4,('core','YR')]=np.nan
imodel['data'].loc[19999,('c99','Identifier')]=np.nan
cdm_tables = cdm.map_model(mapping, imodel['data'], imodel['atts'], log_level = 'INFO')
ascii_tables = cdm.cdm_to_ascii(cdm_tables,log_level ='DEBUG',out_dir = '/Users/iregon/', suffix = None, prefix = None)
