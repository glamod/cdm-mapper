#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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


def coord_dmh_to_180i(deg, min, hemis):
    """
    Converts longitudes from degrees, minutes and hemisphere
    to decimal degrees between -180 to 180.
    Parameters
    ----------
    deg: longitude or latitude in degrees
    min: logitude or latitude in minutes
    hemis: Hemisphere W or E

    Returns
    var: longitude in decimal degrees
    -------
    """
    hemisphere = 1
    min_df = min / 60
    if hemis.any() == 'W':
        hemisphere = -1
    var = np.round((deg + min_df), 2) * hemisphere
    return var


def coord_dmh_to_90i(deg, min, hemis):
    """
    Converts latitudes from degrees, minutes and hemisphere
    to decimal degrees between -90 to 90.
    Parameters
    ----------
    deg: longitude or latitude in degrees
    min: logitude or latitude in minutes
    hemis: Hemisphere N or S

    Returns
    var: latitude in decimal degrees
    -------
    """
    hemisphere = 1
    min_df = min / 60
    if hemis.any() == 'S':
        hemisphere = -1
    var = np.round((deg + min_df), 2) * hemisphere
    return var


def location_accuracy_i(li, lat):
    #    math.sqrt(111**2)=111.0
    #    math.sqrt(2*111**2)=156.97770542341354
    #   Previous implementation:
    #    degrees = {0: .1,1: 1,2: fmiss,3: fmiss,4: 1/60,5: 1/3600,imiss: fmiss}
    degrees = {0: .1, 1: 1, 4: 1 / 60, 5: 1 / 3600}
    deg_km = 111
    accuracy = degrees.get(int(li), np.nan) * math.sqrt((deg_km ** 2) * (1 + math.cos(math.radians(lat)) ** 2))
    return np.nan if np.isnan(accuracy) else max(1, int(round(accuracy)))


def string_add_i(a, b, c, sep):
    if b:
        return sep.join(filter(None, [a, b, c]))
    else:
        return


def convert_air_temp_according_to_unitsi(ind, temp):
    """same function can be apply for wet bulb temp"""
    list_celsius = ['2', '3', '6']
    if ind in list_celsius:
        return np.round(temp + 273.5, decimals=2)
    else:
        return np.round(273.5 + ((temp - 32.0) * (5.0 / 9.0)), decimals=2)


def convert_sst_according_to_unitsi(ind, temp):
    list_celsius = ['2', '3', '5']
    if ind in list_celsius:
        return np.round(temp + 273.5, decimals=2)
    else:
        return np.round(273.5 + ((temp - 32.0) * (5.0 / 9.0)), decimals=2)


def convert_slp_according_to_unitsi(ind, slp):
    list_units = ['1', '2', '3', '4', '5']
    list_barotype = ['1', '2']
    return slp


def give_back_units_ati(ind):
    list_celcius = ['2', '3', '6']
    if ind in list_celcius:
        return 'C'
    else:
        return 'F'


def give_back_units_ssti(ind):
    list_celcius = ['2', '3', '6']
    if ind in list_celcius:
        return 'C'
    else:
        return 'F'


def get_wind_speed_from_tablei(beau_force, scale):
    """
    Converts wind force from beaufort scale to
    average wind speed m/s
    Parameters
    ----------
    beau_force: the beaufort scale
    scale: the key to return either the original loggin scale or
    the conversion to m/s
    Returns
    -------
    value: value or description depending of the scale indicated
    """
    # Convert beau_force to integer
    beau_forcei = int(beau_force)

    wind_speed = {'beaufort': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                  'meterpersec': np.array([0, 1, 3, 5, 7, 10, 12, 15, 19, 23, 27, 31, 41]),
                  'original': ["Calm", "Light air",
                               "Light breeze", "Gentle breeze",
                               "Moderate breeze", "Fresh breeze",
                               "Strong breeze", "High wind,moderate gale,near gale",
                               "Gale,fresh gale", "Strong, severe gale",
                               "Storm,whole gale", "Violent storm",
                               "Hurricane force"]}
    dws = pd.DataFrame.from_dict(wind_speed)

    value = dws[(dws['beaufort'] == beau_forcei)]
    return value[scale].values[0]


class mapping_functions():
    def __init__(self, atts):
        self.atts = atts

    def datetime_decimalhour_to_HM(self, ds):
        hours = int(math.floor(ds))
        minutes = int(math.floor(60.0 * math.fmod(ds, 1)))
        return hours, minutes

    def datetime_imma1(self, df):  # TZ awareness?
        date_format = "%Y-%m-%d-%H-%M"
        hours, minutes = np.vectorize(mapping_functions(self.atts).datetime_decimalhour_to_HM)(df.iloc[:, -1].values)
        # the mapping_functions(self.atts) does not look right, but otherwise it won't recognize things, seems it need to be
        # newly instantiated to be vectorized, ohhhhhhh, me lo estoy inventando, pero suena bien, jajajajaja
        df.drop(df.columns[len(df.columns) - 1], axis=1, inplace=True)
        df['H'] = hours
        df['M'] = minutes
        # VALUES!!!!
        data = pd.to_datetime(df.astype(str).apply("-".join, axis=1).values, format=date_format, errors='coerce')
        return data

    def datetime_utcnow(self):
        return datetime.datetime.utcnow()

    def decimal_places(self, element):
        return self.atts.get(element[0]).get('decimal_places')

    def decimal_places_temperature_kelvin(self, element):
        origin_decimals = self.atts.get(element[0]).get('decimal_places')
        if origin_decimals <= 2:
            return 2
        else:
            return origin_decimals

    def decimal_places_pressure_pascal(self, element):
        origin_decimals = self.atts.get(element[0]).get('decimal_places')
        if origin_decimals > 2:
            return origin_decimals - 2
        else:
            return 0

    def df_col_join(self, df, sep):
        joint = df.iloc[:, 0].astype(str)
        for i in range(1, len(df.columns)):
            joint = joint + sep + df.iloc[:, i].astype(str)
        return joint

    def float_scale(self, ds, factor=1):
        return ds * factor

    def integer_to_float(self, ds, float_type='float32'):
        return ds.astype(float_type)

    def lineage(self, ds):
        return datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S') + ". Initial conversion from ICOADS R3.0.0T"

    def coord_dmh_to_180(self, df):
        """
        Passing attributes and converting longitude to decimal degrees
        Parameters
        ----------
        df: with longitude degree, min, hemisphere
        Returns
        lon: longitude in decimal degrees
        -------
        """
        lon = coord_dmh_to_180i(df.iloc[:, 0], df.iloc[:, 1], df.iloc[:, 2])
        return lon

    def coord_dmh_to_90(self, df):
        """
        Passing attributes and converting latitude to decimal degrees
        Parameters
        ----------
        df: with latitude degree, min, hemisphere
        Returns
        lat: latitude in decimal degrees
        -------
        """
        lat = coord_dmh_to_90i(df.iloc[:, 0], df.iloc[:, 1], df.iloc[:, 2])
        return lat

    def location_accuracy(self, df):
        # (li_core,lat_core) math.radians(lat_core)
        lat = coord_dmh_to_90i(df.iloc[:, 1], df.iloc[:, 2], df.iloc[:, 3])
        la = np.vectorize(location_accuracy_i, otypes='f')(df.iloc[:, 0],
                                                           lat)  # last minute tweak so that is does no fail on nans!
        return la

    def speed_converter(self, ds):
        """
        Picks a ship speed where there is one and converts it
        to m/s.

        Parameters
        ----------
        ds: dataframe with two columns one containing only nans
            and another one with the ship speed
            (Function to be used only for deck 704 and with the field
            "nan_filter": "any" in the header.json file)
        Returns
        -------
        ship_speed: the ship speed that is not nan in m/s
        """
        col_na = ds.columns[ds.isna().any()].tolist()
        speed = ds.drop(columns=col_na[0])
        return np.round(speed.iloc[:, 0] * 0.514444, 2)

    def observing_programme(self, ds):
        op = {str(i): [5, 7, 56] for i in range(0, 6)}
        op.update({'7': [5, 7, 9]})
        return ds.map(op, na_action='ignore')
        # Previous version:
        # observing_programmes = { range(1, 5): '{7, 56}',7: '{5,7,9}'} see how to do a beautifull range dict in the future. Does not seem to be straighforward....
        # if no PT, assume ship
        # !!!! set only for drifting buoys. Rest assumed ships!
        # return df[df.columns[0]].swifter.apply( lambda x: '{5,7,9}' if x == 7 else '{7,56}')

    def string_add(self, ds, prepend=None, append=None, separator=None, zfill_col=None, zfill=None):
        prepend = '' if not prepend else prepend
        append = '' if not append else append
        separator = '' if not separator else separator
        if zfill_col and zfill:
            for col, width in zip(zfill_col, zfill):
                df.iloc[:, col] = df.iloc[:, col].astype(str).str.zfill(width)
        ds['string_add'] = np.vectorize(string_add_i)(prepend, ds, append, separator)
        return ds['string_add']

    def string_join_add(self, df, prepend=None, append=None, separator=None, zfill_col=None, zfill=None):
        separator = '' if not separator else separator
        # This duplication is to prevent error in Int to object casting of types
        # when nrows ==1, shown after introduction of nullable integers in objects.
        duplicated = False
        if len(df) == 1:
            df = pd.concat([df, df])
            duplicated = True
        if zfill_col and zfill:
            for col, width in zip(zfill_col, zfill):
                df.iloc[:, col] = df.iloc[:, col].astype(str).str.zfill(width)
        joint = mapping_functions(self.atts).df_col_join(df, separator)
        df['string_add'] = np.vectorize(string_add_i)(prepend, joint, append, separator)
        if duplicated:
            df = df[:-1]
        return df['string_add']

    def air_temperature_to_kelvin(self, df):
        """
        Parameters
        ----------
        df: data frame with temperature ind and temperature value
        same function can be apply for wet bulb temp
        Returns
        -------
        temp: temperature converted to kelvin according to temp ind values
        for more information on temp ind see mdf.reader() code tables
        """
        df = df.dropna(axis=1, how='all')

        # We get the names of the remaining column
        atts_main = df.iloc[:, 0].name[0]
        atts_ind = df.iloc[:, 0].name[1]
        atts_temp = df.iloc[:, 1].name[1]

        temp = df.apply(lambda x: convert_air_temp_according_to_unitsi(x[atts_main][atts_ind],
                                                                   x[atts_main][atts_temp]), axis=1)
        return temp

    def sst_to_kelvin(self, df):
        """
        Parameters
        ----------
        df: data frame with temperature ind and temperature value
        Returns
        -------
        temp: temperature converted to kelvin according to temp ind values
        for more information on temp ind see mdf.reader() code tables
        """
        df = df.dropna(axis=1, how='all')

        # We get the names of the remaining column
        atts_main = df.iloc[:, 0].name[0]
        atts_ind = df.iloc[:, 0].name[1]
        atts_temp = df.iloc[:, 1].name[1]

        temp = df.apply(lambda x: convert_sst_according_to_unitsi(x[atts_main][atts_ind],
                                                                       x[atts_main][atts_temp]), axis=1)
        return temp

    def get_air_temp_units(self, df):
        """
        Parameters
        ----------
        df: data frame with temperature ind, same function can be apply for wet bulb temp
        Returns
        -------
        temp_units: original temperature units
        """
        df = df.dropna(axis=1, how='all')

        # We get the names of the remaining column
        atts_main = df.iloc[:, 0].name[0]
        atts_ind = df.iloc[:, 0].name[1]

        units = df.apply(lambda x: give_back_units_ati(x[atts_main][atts_ind]), axis=1)
        return units

    def get_sst_units(self, df):
        """
        Parameters
        ----------
        df: data frame with temperature ind
        Returns
        -------
        temp_units: original temperature units
        """
        df = df.dropna(axis=1, how='all')

        # We get the names of the remaining column
        atts_main = df.iloc[:, 0].name[0]
        atts_ind = df.iloc[:, 0].name[1]

        units = df.apply(lambda x: give_back_units_ssti(x[atts_main][atts_ind]), axis=1)
        return units

    def get_orginal_value(self, df):
        """
        Parameters
        ----------
        df: data frame with temperature values
        Returns
        -------
        temp: original temperature that is not a nan
        """
        value = df.dropna(axis=1, how='all')
        return value.iloc[:, 0]

    def temperature_celsius_to_kelvin(self, ds):
        return ds + 273.15

    def time_accuracy(self, ds):  # ti_core
        # Shouldn't we use the code_table mapping for this? see CDM!
        secs = {'0': 3600, '1': int(round(3600 / 10)), '2': int(round(3600 / 60)), '3': int(round(3600 / 100))}
        return ds.map(secs, na_action='ignore')

    def datetime_to_cdm_time(self, df):
        """
        Converts year, month, day and time indicator to
        a datetime obj with a 24hrs format '%Y-%m-%d-%H-%M'
        Parameters
        ----------
        dates: list of elements from a date array
        Returns
        -------
        date: datetime obj
        """

        # Drop NaN from dates list
        dates = df.dropna(axis=1, how='all')

        # Arranging the hour
        dates.iloc[:, 3] = dates.iloc[:, 3].apply("{0:0=2d}".format) + ':00' + ':00'
        dates.iloc[:, -1] = dates.iloc[:, -1].apply(lambda x: 'AM' if x == '1' else 'PM')
        time_string = [x + ' ' + y for x, y in zip(dates.iloc[:, 3], dates.iloc[:, -1])]

        hours = []
        minutes = []
        for item in time_string:
            time_string = pd.to_datetime(item).strftime('%H:%M:%S')
            time_obj = datetime.datetime.strptime(time_string, '%H:%M:%S')
            hours = np.array(np.append(hours, time_obj.hour), np.int16)
            minutes = np.append(minutes, time_obj.minute)

        dates.iloc[:, 3] = hours
        dates.iloc[:, -1] = minutes

        date_format = "%Y-%m-%d-%H"
        data = pd.to_datetime(dates.iloc[:, 0:4].astype(str).apply("-".join, axis=1).values,
                              format=date_format)

        return data

    def get_wind_speed_from_table(self, df, scale=1):
        """
        Parameters
        ----------
        df: data frame with speed term in Beaufort scale
        table: key to pick original scale or converted to m/s
        Returns
        -------
        wind_speed: in m/s
        """
        if scale == 1:
            scale = 'original'
        else:
            scale = 'meterpersec'

        df = df.dropna(axis=1, how='all')
        ds = df.dropna(axis=0, how='all')

        atts_main = ds.iloc[:, 0].name[0]
        atts_ind = ds.iloc[:, 0].name[1]

        wind_speed = ds.apply(lambda x: get_wind_speed_from_tablei(x[atts_main][atts_ind], scale),
                              axis=1)

        return wind_speed