#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 10:31:18 2019

imodel: cisdm_dbo_imma1

Functions to map imodel elements to CDM elements

Main functions are those invoqued in the mappings files (table_name.json)

Main functions need to be part of class mapping_functions()

Main functions get:
    - 1 positional argument (pd.Series or pd.DataFrame with imodel data or 
    imodel element name)
    - Optionally, keyword arguments

Main function return: pd.Series, np.array or scalars

Auxiliary functions can be used and defined in or outside class mapping_functions

@author: iregon
"""

    
class mapping_functions():
    def __init__(self, atts):
        self.atts = atts

    def decimal_places(self,element): 
        return self.atts.get(element[0]).get('decimal_places') 
    
    def decimal_places_pressure_pascal(self,element):
        origin_decimals = self.atts.get(element[0]).get('decimal_places')  
        if origin_decimals > 2:
            return origin_decimals - 2
        else:
            return 0
    
    def decimal_places_temperature_kelvin(self,element):
        origin_decimals = self.atts.get(element[0]).get('decimal_places')  
        if origin_decimals <= 2:
            return 2
        else:
            return origin_decimals
    
    def float_opposite(self,ds):
        return -ds
    
    def float_scale(self,ds,factor = 1):
        return ds*factor
    
    def temperature_celsius_to_kelvin(self,ds):
        return ds + 273.15