# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 12:59:49 2017

@author: Sergey.Vinogradov
"""
import os
from csdlpy import adcirc
from datetime import datetime 
from datetime import timedelta

#==============================================================================
def latestForecast (now = datetime.utcnow()):
    """
    Returns strings YYYYMMDD and tHHz, where HH=00,06,12,18 for the forecast
    that should already have been produced on WCOSS at the time 'now'
    Default value for 'now' is current UTC time.
    """

    #now = datetime.utcnow()
    print '[info]: UTC now:', now
    yyyy = str(now.year).zfill(4)
    mm   = str(now.month).zfill(2)
    dd   = str(now.day).zfill(2)

    #production schedule (Based on ESTOFS v2 which is ~15 min later than v1)
    t00z = datetime.strptime(yyyy+mm+dd+' 05:20','%Y%m%d %H:%M')
    t06z = datetime.strptime(yyyy+mm+dd+' 11:20','%Y%m%d %H:%M')
    t12z = datetime.strptime(yyyy+mm+dd+' 17:20','%Y%m%d %H:%M')
    t18z = datetime.strptime(yyyy+mm+dd+' 23:20','%Y%m%d %H:%M')

    fxDate = now
    if now < t00z:
        #take previous days t18z
        fxDate = now-timedelta(days=1)
        tHHz         = 't18z'
    elif t00z <= now and now < t06z:
        tHHz         = 't00z'
    elif t06z <= now and now < t12z:
        tHHz         = 't06z'
    elif t12z <= now and now < t18z:
        tHHz         = 't12z'
    elif t18z <= now:
        tHHz         = 't18z'

    yyyymmdd = str(fxDate.year).zfill(4)+ \
               str(fxDate.month).zfill(2)+ \
               str(fxDate.day).zfill(2)

    return {'yyyymmdd' : yyyymmdd,
            'tHHz'     : tHHz} 

#==============================================================================
def getPointsWaterlevel ( ncFile ):    
    """
    Reads water levels at stations 
    Args: 
        'ncFile' (str): full path to netCDF file        
    Returns:
        dict: 'lon', 'lat', 'time', 'base_date', 'zeta', 'stations'
    """
    print '[info]: Reading waterlevels from ' + ncFile               
    if not os.path.exists (ncFile):
        print '[error]: File ' + ncFile + ' does not exist.'
        return

    z = adcirc.readTimeSeries (ncFile, 'zeta')

    # checking ESTOFS version
    ncTitle = z['title']
    if ncTitle.find('PACIFIC') > 0:
        estofsVersion = 1
        xy_mltplr = 0.01745323168310549  #Magic ESTOFS1 Multiplier...
    else:
        estofsVersion = 2
        xy_mltplr = 1.00
    print '[info]: ESTOFS Version ' + str(estofsVersion)  +' detected.'
    
    z['lon']  = xy_mltplr*z['lon']
    z['lat']  = xy_mltplr*z['lat']

    return z

#==============================================================================
def getFieldsWaterlevel ( ncFile, ncVarName ):

    return adcirc.readSurfaceField ( ncFile, ncVarName )

