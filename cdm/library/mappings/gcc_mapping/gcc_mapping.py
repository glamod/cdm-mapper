"""
Created on Wed Apr  3 10:31:18 2019

imodel: imma1

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
import math
import numpy as np
import pandas as pd
import datetime
import uuid

def longitude_360to180_i(lon):
    if lon > 180:
        return -180 + math.fmod(lon, 180)
    else:
        return lon

def string_add_i(a,b,c,sep):
    if b:
        return sep.join(filter(None,[a,b,c]))
    else:
        return

class mapping_functions():
    def __init__(self, atts):
        self.atts = atts

    def datetime_decimalhour_to_HM(self,ds):
        hours = int(math.floor(ds))
        minutes = int(math.floor(60.0*math.fmod(ds, 1)))
        return hours,minutes

    def datetime_imma1(self,df): # TZ awareness?
        date_format = "%Y-%m-%d-%H-%M"
        hours, minutes = np.vectorize(
            mapping_functions(self.atts).datetime_decimalhour_to_HM)(
                df.iloc[:,-1].values)
        df.drop(df.columns[len(df.columns)-1], axis=1, inplace=True)
        df['H'] = hours
        df['M'] = minutes
        # VALUES!!!!
        data = pd.to_datetime(df.astype(str).apply("-".join, axis=1).values,
                              format=date_format, errors='coerce')
        return data

    def datetime_utcnow(self):
        return datetime.datetime.utcnow()

    def decimal_places(self,element):
        return self.atts.get(element[0]).get('decimal_places')

    def decimal_places_temperature_kelvin(self,element):
        origin_decimals = self.atts.get(element[1]).get('decimal_places')
        if origin_decimals <= 2:
            return 2
        else:
            return origin_decimals

    def decimal_places_pressure_pascal(self,element):
        origin_decimals = self.atts.get(element[0]).get('decimal_places')
        if origin_decimals > 2:
            return origin_decimals - 2
        else:
            return 0

    def df_col_join(self,df,sep):
        joint = df.iloc[:,0].astype(str)
        for i in range(1,len(df.columns)):
            joint = joint + sep + df.iloc[:,i].astype(str)
        return joint

    def float_scale(self,ds,factor = 1):
        return ds*factor

    def integer_to_float(self,ds,float_type = 'float32'):
        return ds.astype(float_type)

    def lineage(self,ds):
        return datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    def longitude_360to180(self,ds):
        lon = np.vectorize(longitude_360to180_i)(ds)
        return lon

    def observing_programme(self,ds):
        op = { str(i):[5,7,56] for i in range(0,6) }
        op.update({'7':[5,7,9]})
        return ds.map( op, na_action = 'ignore' )


    def string_add(self, ds, prepend=None, append=None, separator=None,
                   zfill_col=None, zfill=None):
        prepend = '' if not prepend else prepend
        append = '' if not append else append
        separator = '' if not separator else separator
        if zfill_col and zfill:
            for col,width in zip(zfill_col,zfill):
                df.iloc[:,col] = df.iloc[:,col].astype(str).str.zfill(width)
        ds['string_add'] = np.vectorize(string_add_i)(prepend,ds,append,separator)
        return ds['string_add']

    def string_join_add(self,df, prepend=None, append=None, separator=None,
                        zfill_col=None, zfill=None):
        separator = '' if not separator else separator
        # This duplication is to prevent error in Int to object casting of types
        # when nrows ==1, shown after introduction of nullable integers in objects.
        duplicated = False
        if len(df) == 1:
            df = pd.concat([df,df])
            duplicated = True
        if zfill_col and zfill:
            for col,width in zip(zfill_col,zfill):
                df.iloc[:,col] = df.iloc[:,col].astype(str).str.zfill(width)
        joint = mapping_functions(self.atts).df_col_join(df,separator)
        df['string_add'] = np.vectorize(string_add_i)(prepend,joint,append,separator)
        if duplicated:
            df = df[:-1]
        return df['string_add']

    def apply_sign(self, ds):
        ds.iloc[0] = np.where((ds.iloc[0] == 0) | (ds.iloc[0] == 5), 1, -1)
        return ds

    def temperature_celsius_to_kelvin(self, ds):
        ds.iloc[:, 0] = np.where(
            (ds.iloc[:, 0] == 0) | (ds.iloc[:, 0] == 5), 1, -1)
        # print(ds.iloc[:, 0]*ds.iloc[:, 1])
        return ds.iloc[:, 0]*ds.iloc[:, 1]+273.15

    def time_accuracy(self,ds): #ti_core
        # Shouldn't we use the code_table mapping for this? see CDM!
        secs = {'0': 3600,'1': int(round(3600/10)),'2': int(round(3600/60)),
                '3': int(round(3600/100))}
        return ds.map( secs, na_action = 'ignore' )

    def guid(self,df,prepend='',append=''):
        df["YR"] = df["YR"].apply(lambda x: f"{x:04d}")
        df["MO"] = df["MO"].apply(lambda x: f"{x:02d}")
        df["DY"] = df["DY"].apply(lambda x: f"{x:02d}")
        df["GG"] = df["GG"].astype('int64').apply(lambda x: f"{x:02d}")
        name = df.apply(lambda x: ''.join(x), axis=1)
        uid = np.empty(np.shape(df["YR"]),dtype="U126")
        for (i,n) in enumerate(name):
            uid[i] = str(prepend)+uuid.uuid5(uuid.NAMESPACE_OID,str(n)).hex + \
                str(append)
        df["UUID"] = uid
        return df["UUID"]

