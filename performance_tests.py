#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 08:46:03 2019

@author: iregon
"""

import timeit
import pandas as pd
import numpy as np
import math


# Tests for string_wrap--------------------------------------------------------
#LEN =10000000 
#df = pd.DataFrame(data=['prueba']*LEN,columns=['str'])
#df.iloc[0,0] = None
#a = 'a'
#b = 'b'
#sep = "|"
#
#def string_wrap_i(a,b,c,sep):
#    if b:
#        return sep.join([a,b,c])
#    else:
#        return
#    
#def pd_apply(df):
#    def _pd_apply():
#        print(df.iloc[:,0].apply(lambda x: sep.join([a,x,b]) if x else None ))
#    return _pd_apply
#def vectorize(df):
#    def _vectorize():
#        print(np.vectorize(string_wrap_i)(a,df,b,sep))
#    return _vectorize
#
#def vectorize_np(df):        
#    def _vectorize_np():
#        print(np.vectorize(string_wrap_i)(a,df.values,b,sep))
#    return _vectorize_np
#
#t = timeit.Timer(pd_apply(df))
#t_apply = t.timeit(1)
#t = timeit.Timer(vectorize(df))
#t_vectorize = t.timeit(1)
#t = timeit.Timer(vectorize_np(df))
#t_vectorize_np = t.timeit(1)
#
#print("apply:",t_apply)
#print("df-vectorized:",t_vectorize)
#print("df.values-vectorized:",t_vectorize_np)


# Tests for string_wrap--------------------------------------------------------
LEN =100000000 
df = pd.DataFrame()
df['lon'] = np.random.randint(-180,180,LEN)
df.iloc[0,0] = None

def longitude_360to180_i(lon):
    if lon > 180:
        return -180 + math.fmod(lon, 180)
    else:
        return lon

def pd_apply(df):
    def _pd_apply():
        lon = df.iloc[:,0].apply(lambda x: -180 + math.fmod(x, 180) if x >= 180 else x )
        print(lon)
    return _pd_apply
   
def vectorize(df):
    def _vectorize():
        lon = np.vectorize(longitude_360to180_i)(df)
        print(lon)
    return _vectorize

t = timeit.Timer(pd_apply(df))
t_apply = t.timeit(1)
t = timeit.Timer(vectorize(df))
t_vectorize = t.timeit(1)
print("apply:",t_apply)
print("df-vectorized:",t_vectorize)
