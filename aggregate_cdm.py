#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 15:30:57 2023

@author: sbiri
"""

import pandas as pd
import glob
import os


def myrd_csv(fn, delimiter = '|'):
    # column names in header.psv
    hdr_cols = ["report_id", "region", "sub_region", "application_area",
            "observing_programme", "report_type", "station_name",
            "station_type", "platform_type", "platform_sub_type",
            "primary_station_id", "station_record_number",
            "primary_station_id_scheme", "longitude", "latitude",
            "location_accuracy","location_method", "location_quality",
            "crs", "station_speed", "station_course", "station_heading",
            "height_of_station_above_local_ground", 
            "height_of_station_above_sea_level",
            "height_of_station_above_sea_level_accuracy", 
            "sea_level_datum", "report_meaning_of_timestamp",
            "report_timestamp", "report_duration", "report_time_accuracy",
            "report_time_quality", "report_time_reference", "profile_id",
            "events_at_station", "report_quality", "duplicate_status",
            "duplicates", "record_timestamp", "history", 
            "processing_level", "processing_codes", "source_id",
            "source_record_id", "image_name", "image_directory",
            "image_url", "remarks"]
    # column names in observations files we want to keep
    obs_cols = ["observation_id", "data_policy_licence",
            "date_time", "date_time_meaning", "observation_duration", 
            "z_coordinate", "z_coordinate_type", 
            "observation_height_above_station_surface", 
            "observed_variable", "secondary_variable", "observation_value",
            "value_significance", "secondary_value", "units", 
            "code_table", "conversion_flag",  "location_precision",
            "z_coordinate_method", "bbox_min_longitude",
            "bbox_max_longitude", "bbox_min_latitude", "bbox_max_latitude",
            "spatial_representativeness", "quality_flag", 
            "numerical_precision", "sensor_id", "sensor_automation_status",
            "exposure_of_sensor", "original_precision", "original_units",
            "original_code_table", "original_value", "conversion_method",
            "adjustment_id", "traceability", "advanced_qc", 
            "advanced_uncertainty", "advanced_homogenisation"]
    
    if "header" in fn:
        df = pd.read_csv(fn, delimiter=delimiter, usecols=hdr_cols,
                         dtype="object")
    else:
        suf = fn.split("-")[1][:-4]
        df = pd.read_csv(fn, delimiter=delimiter, usecols=obs_cols, 
                          dtype="object")
        # add observation value suffix in column names
        df.columns = [str(col)+"_"+suf for col in df.columns]
    return df

def aggregate_cdm(path, filename):
    """
    

    Parameters
    ----------
    path : string
        path to input files
    filename : string
        path and name of the merged file

    Returns
    -------
    df : data frame
        aggregated psv file

    """
    # merge files
    files_all = os.path.join(path, "*.psv")
    # remove source_config, station_config if in files_all
    list_all = [item for item in glob.glob(files_all) if item not in {
        path+"source_config.psv", path+"station_config.psv"}]
    # if header is missing stop
    if not [ele for ele in list_all if("header" in ele)]:
        print("header.psv is missing")
        return
    # Merge files by joining all files
    mapper = map(lambda fn: myrd_csv(fn), list_all)
    df = pd.concat(list(mapper), axis=1, ignore_index=False)
    for i in df.iloc[0, :]:
        print(i)    
    df.to_csv(filename, index=False, sep="|", header=True, mode='w')
    return df
