#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 21 16:06:16 2019

We want a set of data descriptors on a monthly lat-lon box grid:
    - counts, max, min, mean
    
We want to have the stats for the qced and not qced thing
    
We want to save that to a nc file to open afterwards in notebooks 
and inspect further or to create static images (maps, plots, etc....) for reports

We are not doing it on the notebooks because we are running these interactively
 and these depend on the changing memo availability of the sci servers.
An alternative will be to run the notebook as a bsub job, but we would need
to know before hand, our memo requirements.

When we have experience with this, we can add the option to (re)compute the nc
 file in the notebook.


We use datashader to create the spatial aggregates because dask does not support
dataframe.cut, which is essential to do a flexible groupby coordinates. We could
groupby(int(coordinates)), but the we would be limited to 1degree boxes, which 
is not bad, but we don't wnat to be limited.  

@author: iregon
"""

import os
import datashader as ds
import xarray as xr
import pandas as pd
from cdm import properties
import datetime
import logging
import glob


# SOME COMMON PARAMS ----------------------------------------------------------
# For canvas
REGIONS = dict()
REGIONS['Global'] = ((-180.00, 180.00), (-90.00, 90.00))
DEGREE_FACTOR_RESOLUTION = dict()
DEGREE_FACTOR_RESOLUTION['lo_res'] = 1
DEGREE_FACTOR_RESOLUTION['me_res'] = 2
DEGREE_FACTOR_RESOLUTION['hi_res'] = 5
# To define aggregationa
DS_AGGREGATIONS = {'counts':ds.count,'max':ds.max,'min':ds.min, 'mean':ds.mean}
AGGREGATIONS = ['counts','max','min','mean']
DS_AGGREGATIONS_HDR = {'counts':ds.count}
AGGREGATIONS_HDR = ['counts']
# TO output nc
ENCODINGS = {'latitude': {'dtype': 'int16', 'scale_factor': 0.01, '_FillValue': -99999},
             'longitude': {'dtype': 'int16', 'scale_factor': 0.01, '_FillValue': -99999},
             'counts': {'dtype': 'int32','_FillValue': -99999},
             'max': {'dtype': 'int16', 'scale_factor': 0.01, '_FillValue': -99999},
             'min': {'dtype': 'int16', 'scale_factor': 0.01, '_FillValue': -99999},
             'mean': {'dtype': 'int16', 'scale_factor': 0.01, '_FillValue': -99999}}
ENCODINGS_HDR = {'latitude': {'dtype': 'int16', 'scale_factor': 0.01, '_FillValue': -99999},
             'longitude': {'dtype': 'int16', 'scale_factor': 0.01, '_FillValue': -99999},
             'counts': {'dtype': 'int32','_FillValue': -99999}}
# To read tables
CDM_DTYPES = {'latitude':'float32','longitude':'float32',
              'observation_value':'float32','date_time':'object',
              'quality_flag':'int8','crs':'int'}
READ_COLS = ['latitude','longitude','observation_value','date_time',
                 'quality_flag']
DTYPES = { x:CDM_DTYPES.get(x) for x in READ_COLS }

READ_COLS_HDR = ['latitude','longitude','crs','report_timestamp']
DTYPES_HDR = { x:CDM_DTYPES.get(x) for x in READ_COLS }

DELIMITER = '|'


# SOME FUNCTIONS THAT HELP ----------------------------------------------------
def bounds(x_range, y_range):
    return dict(x_range=x_range, y_range=y_range)

def create_canvas(bbox,degree_factor):
    plot_width = int(abs(bbox[0][0]-bbox[0][1])*degree_factor)
    plot_height = int(abs(bbox[1][0]-bbox[1][1])*degree_factor)    
    return ds.Canvas(plot_width=plot_width, plot_height=plot_height, **bounds(*bbox))
 

# FUNCTIONS TO DO WHAT WE WANT ------------------------------------------------
def from_cdm_monthly(dir_data, cdm_id = None, region = 'Global', 
                      resolution = 'lo_res', nc_dir = None, qc=False):
    
    logging.basicConfig(format='%(levelname)s\t[%(asctime)s](%(filename)s)\t%(message)s',
                    level=logging.INFO,datefmt='%Y%m%d %H:%M:%S',filename=None)
    
    canvas = create_canvas(REGIONS.get(region),DEGREE_FACTOR_RESOLUTION.get(resolution)) 
    
    table = 'header'
    logging.info('Processing table {}'.format(table))
    table_file = os.path.join(dir_data,'-'.join([table,cdm_id]) + '.psv')
    if not os.path.isfile(table_file):
        logging.error('Table file not found {}'.format(table_file))
        return
    df = pd.read_csv(table_file,delimiter=DELIMITER,usecols = READ_COLS_HDR,
                     parse_dates=['report_timestamp'],dtype=DTYPES_HDR)
    try:
        date_time = datetime.datetime(df['report_timestamp'][0].year,df['report_timestamp'][0].month,1)
    except Exception:
        fields = cdm_id.split('-')
        date_time = datetime.datetime(int(fields[0]),int(fields[1]),1)
    # Aggregate on to and aggregate to a dict
    xarr_dict = { x:'' for x in AGGREGATIONS_HDR }
    for agg in AGGREGATIONS_HDR:
        xarr_dict[agg] = canvas.points(df, 'longitude','latitude',
                         DS_AGGREGATIONS_HDR.get(agg)('crs'))
    # Merge aggs in a single xarr
    xarr = xr.merge([ v.rename(k) for k,v in xarr_dict.items()])
    xarr.expand_dims(**{'time':[date_time]})
    xarr.encoding = ENCODINGS_HDR 
    # Save to nc
    nc_dir = dir_data if not nc_dir else nc_dir 
    nc_name = '-'.join([table,cdm_id]) + '.nc' 
    xarr.to_netcdf(os.path.join(nc_dir,nc_name),encoding = ENCODINGS_HDR,mode='w')
        
    obs_tables = [ x for x in properties.cdm_tables if x != 'header' ]
    for table in obs_tables:
        logging.info('Processing table {}'.format(table))
        table_file = os.path.join(dir_data,'-'.join([table,cdm_id]) + '.psv')
        if not os.path.isfile(table_file):
            logging.warning('Table file not found {}'.format(table_file))
            continue
        # Read the data
        df = pd.read_csv(table_file,delimiter=DELIMITER,usecols = READ_COLS,
                         parse_dates=['date_time'],dtype=DTYPES)
        if qc:
            df = df.loc[df['quality_flag'] == 0]
        try:
            date_time = datetime.datetime(df['date_time'][0].year,df['date_time'][0].month,1)
        except Exception:
            fields = cdm_id.split('-')
            date_time = datetime.datetime(int(fields[0]),int(fields[1]),1)
        # Aggregate on to and aggregate to a dict
        xarr_dict = { x:'' for x in AGGREGATIONS }
        for agg in AGGREGATIONS:
            xarr_dict[agg] = canvas.points(df, 'longitude','latitude',
                             DS_AGGREGATIONS.get(agg)('observation_value'))
        # Merge aggs in a single xarr
        xarr = xr.merge([ v.rename(k) for k,v in xarr_dict.items()])
        xarr.expand_dims(**{'time':[date_time]})
        xarr.encoding = ENCODINGS 
        # Save to nc
        nc_dir = dir_data if not nc_dir else nc_dir 
        nc_name = '-'.join([table,cdm_id]) + '.nc' 
        xarr.to_netcdf(os.path.join(nc_dir,nc_name),encoding = ENCODINGS,mode='w')
    
    return

def merge_from_monthly_nc(dir_data, cdm_id = None, nc_dir = None):
    
    logging.basicConfig(format='%(levelname)s\t[%(asctime)s](%(filename)s)\t%(message)s',
                    level=logging.INFO,datefmt='%Y%m%d %H:%M:%S',filename=None)
    table = 'header'
    logging.info('Processing table {}'.format(table))
    pattern = '-'.join([table,'*',cdm_id]) + '.nc'      
    all_files = glob.glob(os.path.join(dir_data,pattern))
    if len(all_files) == 0:
         logging.error('No nc files found {}'.format(pattern)) 
         return
    all_files.sort()
    # Read all files to a single dataset
    dataset = xr.open_mfdataset(all_files,concat_dim='time')
    # Aggregate each aggregation correspondingly....
    merged = {}
    merged['counts'] = dataset['counts'].sum(dim='time',skipna=True)
    # Merge aggregations to a single xarr
    xarr = xr.merge([ v.rename(k) for k,v in merged.items()])
    xarr.encoding = ENCODINGS_HDR 
    # Save to nc
    nc_dir = dir_data if not nc_dir else nc_dir 
    nc_name = '-'.join([table,cdm_id]) + '.nc' 
    xarr.to_netcdf(os.path.join(nc_dir,nc_name),encoding = ENCODINGS_HDR)
    
    obs_tables = [ x for x in properties.cdm_tables if x != 'header' ]
    for table in obs_tables:
        logging.info('Processing table {}'.format(table))
        pattern = '-'.join([table,'*',cdm_id]) + '.nc'      
        all_files = glob.glob(os.path.join(dir_data,pattern))
        if len(all_files) == 0:
             logging.warning('No nc files found {}'.format(pattern)) 
             continue
        all_files.sort()
        # Read all files to a single dataset
        dataset = xr.open_mfdataset(all_files,concat_dim='time')
        # Aggregate each aggregation correspondingly....
        merged = {}
        merged['max'] = dataset['max'].max(dim='time',skipna=True)
        merged['min'] = dataset['min'].min(dim='time',skipna=True)
        merged['mean'] = dataset['mean'].mean(dim='time',skipna=True)
        merged['counts'] = dataset['counts'].sum(dim='time',skipna=True)
        # Merge aggregations to a single xarr
        xarr = xr.merge([ v.rename(k) for k,v in merged.items()])
        xarr.encoding = ENCODINGS 
        # Save to nc
        nc_dir = dir_data if not nc_dir else nc_dir 
        nc_name = '-'.join([table,cdm_id]) + '.nc' 
        xarr.to_netcdf(os.path.join(nc_dir,nc_name),encoding = ENCODINGS)
    return

def global_from_cdm_monthly():
    print('hi, not there yet')
    return

def global_from_monthly_nc():
    print('hi, not there yet')
    return


##if __name__=='__main__':
##    kwargs = dict(arg.split('=') for arg in sys.argv[2:])
##    if 'sections' in kwargs.keys():
##        kwargs.update({ 'sections': [ x.strip() for x in kwargs.get('sections').split(",")] })
##    read(sys.argv[1], 
##         **kwargs) # kwargs
