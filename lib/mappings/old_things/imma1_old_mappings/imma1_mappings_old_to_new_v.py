#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 10:21:12 2019

@author: iregon
"""

import os
import json

imma_paths = ['/Users/iregon/C3S/dessaps/glamod/icoads2cdm/py_tools/cdm/mappings/imma1/observations_at.json',
              '/Users/iregon/C3S/dessaps/glamod/icoads2cdm/py_tools/cdm/mappings/imma1/observations_dpt.json',
              '/Users/iregon/C3S/dessaps/glamod/icoads2cdm/py_tools/cdm/mappings/imma1/observations_slp.json',
              '/Users/iregon/C3S/dessaps/glamod/icoads2cdm/py_tools/cdm/mappings/imma1/observations_sst.json',
              '/Users/iregon/C3S/dessaps/glamod/icoads2cdm/py_tools/cdm/mappings/imma1/observations_wbt.json',
              '/Users/iregon/C3S/dessaps/glamod/icoads2cdm/py_tools/cdm/mappings/imma1/observations_ws.json',
              '/Users/iregon/C3S/dessaps/glamod/icoads2cdm/py_tools/cdm/mappings/imma1/observations_wd.json',
              '/Users/iregon/C3S/dessaps/glamod/icoads2cdm/py_tools/cdm/mappings/imma1/common.json']

cdm_lib = '/Users/iregon/dessaps/cdm/mapper/lib/imma1/old_mappings'

for imma in imma_paths:
    table_name = os.path.basename(imma)
    cdm_path = os.path.join(cdm_lib,table_name)

    with open(imma,'r') as fileObj:
        mapping = json.load(fileObj)

    mapping_dict = { x.get('cdm_key'):x for x in mapping }

    for key in mapping_dict.keys():
        mapping_dict.get(key).update({'sections':mapping_dict.get(key).get('data_key'),'elements':mapping_dict.get(key).get('data_key')})
        mapping_dict.get(key).pop('cdm_key')
        mapping_dict.get(key).pop('data_key')
        mapping_dict.get(key).pop('missing')

    with open(cdm_path,'w') as fileObj:
        json.dump(mapping_dict,fileObj,indent=4)
