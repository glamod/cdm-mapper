#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 21 16:06:16 2019

We want a set of data descriptors on a monthly lat-lon box grid:
    - counts, max, min, mean
    - quantiles: p1, p99, p25, p50, p75
    - source hitting min,max, p?
    - number of sources
    
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
from dask import dataframe as dd
import dask.diagnostics as diag
import datashader as ds
import xarray as xr
import shutil
import random

# SOME COMMON PARAMS ----------------------------------------------------------
CDM_OBSERVED_VARIABLES = ['sst','at','slp','dpt','wbt','wd','ws']
AGGREGATIONS = ['counts','max','min']
aggregates = AGGREGATIONS.copy()
for agg in AGGREGATIONS:
    aggregates.append('_'.join([agg,'qc']))

# FUNCTIONS AND PARAMETRIZATIONS TO DO THE AGGREGATIONS WITH DATASHADER -------
DS_AGGREGATIONS = {'counts':ds.count,'max':ds.max,'min':ds.min}
for agg in AGGREGATIONS:
    DS_AGGREGATIONS.update({'_'.join([agg,'qc']):DS_AGGREGATIONS.get(agg)})
    
REGIONS = dict()
REGIONS['Global'] = ((-180.00, 180.00), (-90.00, 90.00))
REGIONS['North_Atlantic']   = (( -90.00,  10.00), ( 0, 80))
DEGREE_FACTOR_RESOLUTION = dict()
DEGREE_FACTOR_RESOLUTION['lo_res'] = 1
DEGREE_FACTOR_RESOLUTION['me_res'] = 2
DEGREE_FACTOR_RESOLUTION['hi_res'] = 5

def bounds(x_range, y_range):
    return dict(x_range=x_range, y_range=y_range)

def create_canvas(bbox,degree_factor):
    plot_width = int(abs(bbox[0][0]-bbox[0][1])*degree_factor)
    plot_height = int(abs(bbox[1][0]-bbox[1][1])*degree_factor)    
    return ds.Canvas(plot_width=plot_width, plot_height=plot_height, **bounds(*bbox))
  
def monthly_aggs_by_index(df,i,agg,canvas,qc = False):
    if qc:
        month_par = df.get_partition(i)
        month_data = month_par.loc[month_par['quality_flag']==0].compute()
    else:
        month_data = df.get_partition(i).compute()
    return canvas.points(month_data, 'longitude','latitude',
                         DS_AGGREGATIONS.get(agg)('observation_value'))
    
# FUNCTIONS TO READ DATA ------------------------------------------------------
def read_cdm_to_dd(dir_data,obs_var,yyyy = None,mm = None,release_id = None):
    # THE DASK APPROACH DOES NOT REALLY MAKE SENSE WHEN READING A SINGLE,
    # (SMALL) FILE: THE OVERHEAD MAKES IT EVEN WORSE THAN WITH A SIMPLE PANDAS
    # READING.....
    CDM_DTYPES = {'latitude':'float32','longitude':'float32',
              'observation_value':'float32','date_time':'object',
              'quality_flag':'int8'}
    READ_COLS = ['latitude','longitude','observation_value','date_time',
                 'quality_flag']
    
    yyyy = '*' if not yyyy else str(yyyy)
    mm = '*' if not mm else str(mm).zfill(2)

    data_path = os.path.join(dir_data,'-'.join(filter(None,['observations',
                            obs_var,yyyy,mm,release_id])) + '.psv')
     
    if not os.path.isfile(data_path):
        return
    dtypes = { x:CDM_DTYPES.get(x) for x in READ_COLS }
    df = dd.read_csv(data_path,delimiter='|',usecols = READ_COLS,
                     parse_dates=['date_time'],dtype=dtypes)
    # Following is not working in JASMIN: had to install pyarrow insted of fastparquet
    #print('to parquet')
    #parq_path = os.path.join(dir_data,str(random.randint(1,30000))+ str(random.randint(1,3000)) + 'data.parq.tmp')
    #with diag.ProgressBar(), diag.Profiler() as prof, diag.ResourceProfiler(0.5) as rprof:
    #    df.to_parquet(parq_path)
    #del df
    #print('From parquet')
    #try:
    #    df = dd.read_parquet(parq_path)
    #except Exception as e:
    #    print(e)
    #print(df)
    # NOW REINDEX TO MONTHLY AND HAVE THE PARTITIONS TO MONTH TO EASE COMPUTATIONS
    # HERE CHECK THE PARTITION CONTENTS AGAINST THE DIVISIONS NAMES, ETC.....
    with diag.ProgressBar(), diag.Profiler() as prof, diag.ResourceProfiler(0.5) as rprof:
        df = df.set_index(df['date_time'], sorted=True) # Convert already here to monthly precision...
    if df.npartitions > 1:
        with diag.ProgressBar(), diag.Profiler() as prof, diag.ResourceProfiler(0.5) as rprof:
            df = df.repartition(freq='MS') # beware on how actual partitions are made....
    return df#,parq_path


# FUNCTIONS TO MANAGE THE GRIDDING FROM INPUT DATA ----------------------------
def df_to_xarray_monthly_aggs(df,obs_var,region,resolution):
    # Check canvas borders on different resolutions
    canvas = create_canvas(REGIONS.get(region),DEGREE_FACTOR_RESOLUTION.get(resolution))
    xarr_dict = { x:'' for x in aggregates }
    for agg in aggregates:
        if agg.endswith('qc'):
            with diag.ProgressBar(), diag.Profiler() as prof, diag.ResourceProfiler(0.5) as rprof:
                xarr_dict[agg] = xr.concat([ monthly_aggs_by_index(df,i,agg,canvas,qc=True).assign_coords(time=df.divisions[i]).rename(agg) for i in range(0,df.npartitions) ], dim = 'time')
        else:
            with diag.ProgressBar(), diag.Profiler() as prof, diag.ResourceProfiler(0.5) as rprof:
                xarr_dict[agg] = xr.concat([ monthly_aggs_by_index(df,i,agg,canvas).assign_coords(time=df.divisions[i]).rename(agg) for i in range(0,df.npartitions) ], dim = 'time')
        
    # Merge all stats in a single array; one var, the aggregation goes to the dimensions!
    xarr = xr.concat([ v.rename(obs_var) for k,v in xarr_dict.items()],dim='aggregation',coords='all')
    xarr = xarr.assign_coords(aggregation=list(xarr_dict.keys()))    
    xarr.loc['counts'] = xarr.loc['counts'].where(xarr.loc['counts'] >= 1)
    xarr.loc['counts_qc'] = xarr.loc['counts_qc'].where(xarr.loc['counts_qc'] >= 1)   
    return xarr


# FUNCTIONS/PARAMS TO OUTPUT TO NC --------------------------------------------
ENCODINGS = {'latitude': {'dtype': 'int16', 'scale_factor': 0.01, '_FillValue': -99999},
             'longitude': {'dtype': 'int16', 'scale_factor': 0.01, '_FillValue': -99999},
             'var': {'dtype': 'int16', 'scale_factor': 0.01, '_FillValue': -99999}}

    
encoded_coordinates = ['latitude','longitude']
#encoded_coordinates.extend(aggregates)

def xarray_to_nc(xarray,varis, nc_path):
    xarray.encoding={ x:ENCODINGS.get(x) for x in encoded_coordinates }
    xarray.encoding={ x:ENCODINGS.get('var') for x in varis }
    xarray.to_netcdf(nc_path,encoding = xarray.encoding)
    return

# FUNCTIONS TO DO WHAT WE WANT ------------------------------------------------
def monthly_from_cdm_monthly_files(dir_data, yyyy, mm, release_id = None, 
                                   region = 'Global', resolution = 'lo_res', 
                                   nc_dir = None, nc_name = None):
    xarray_vars = {}
    for obs_var in CDM_OBSERVED_VARIABLES:
        try:
            df = read_cdm_to_dd(dir_data,obs_var,yyyy = yyyy,mm = mm, 
                                release_id = release_id)
            #df,parquet_path = read_cdm_to_dd(dir_data,obs_var,yyyy = yyyy,mm = mm)
        except:
            print('No data for {}'.format(obs_var))
            continue
        xarray_vars[obs_var] = df_to_xarray_monthly_aggs(df, obs_var, region, resolution)
        #shutil.rmtree(parquet_path)
    xarray_all = xr.merge([ v for k,v in xarray_vars.items()] ) 
    nc_dir = dir_data if not nc_dir else nc_dir
    nc_name = '-'.join(filter(None,[str(yyyy),str(mm).zfill(2),release_id])) + '.nc' if not nc_name else nc_name
    xarray_to_nc(xarray_all,list(xarray_vars.keys()),os.path.join(nc_dir,nc_name))
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
