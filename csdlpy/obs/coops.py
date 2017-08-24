# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 12:06:00 2017

@author: Sergey.Vinogradov
"""
from datetime import datetime
import numpy as np
from csdlpy import transfer

#==============================================================================
def getData (stationID,  dateRange, 
             product='waterlevelrawsixmin', datum='MSL', units='meters'):
    
    """ 
    Allows for downloading the observations from NOAA's 
    Center for Operational Oceanographic Products and Services (COOPS)
    via OpenDAP server    http://opendap.co-ops.nos.noaa.gov .
    
    Args:
        stationID (str):              7 character-long CO-OPS station ID.
        dateRange (datetime, datetime): start and end dates of retrieval.
    
    Optional Args:        
        'product' (str):             
            WATER LEVEL: 
            'waterlevelrawsixmin' (=default), 'waterlevelrawonemin',
            'waterlevelverifiedsixmin',  'waterlevelverifiedhourly',
            'waterlevelverifiedhighlow', 'waterlevelverifieddaily', 
            'waterlevelverifiedmonthly',
            'highlowtidepredictions', 'predictions', 
            'harmonicconstituents',    'datums',             
            METEOROLOGY: 
            'barometricpressure', 'wind'. 
            
        'datum' (str): 'MSL' (=default), 'NAVD', 'IGLD', 'MTL',
            'station datum', 'MHW','MHHW','MLLW', 'MLW'.
        
        'units' (str): 'meters','feet', 'm/sec', 'knots','miles/hour'
        
        'tideFreq' (str): '6' (=default), '60'
        
    Returns:
        ('dates' (datetime), 'values' (float)): 
            retrieved time series record of observations.
            Note: for the 'wind' product, 'values' consist of 
            wind speed, wind direction and wind gust.
            
    Examples:
        now   = datetime.now()
        dates = (now-dt(days=3), now)
        tides = getdata('8518750', dates, product='predictions')        
        retrieves tidal water levels at The Battery, NY over the last 3 days.
        
    """
    # TODO:
    # Check dateRange
    # 'waterlevel*'       : months=12
    # 'waterlevelverifiedhighlow' : months=5*12
    # 'waterlevel*sixmin' : months=1
    # ''
    # If needed call sub-function to split dateRange into proper chunks
    # and call getdata recursively and concatenate the outputs
    
    ## Formulate, print and send the request
    serverSide  = 'https://opendap.co-ops.nos.noaa.gov/axis/webservices/'
    timeZoneID  = '0'

    unitID      = '1'  # feet, or knots
    if units   == 'meters' or units == 'm/sec':
        unitID  = '0'    
    elif units == 'miles/hour':
        unitID  = '2'

    tideFreq    = '6'  # use 60 for hourly tides
    tideFreqStr = ''
    if product == 'predictions':
        tideFreqStr = '&dataInterval=' + tideFreq
        
    request = ( serverSide + product + '/plain/response.jsp?stationId=' + 
               stationID + 
               '&beginDate=' + dateRange[0].strftime("%Y%m%d") +
               '&endDate='   + dateRange[1].strftime("%Y%m%d") +
               '&datum=' + datum + '&unit=' + unitID + 
               '&timeZone=' + timeZoneID + tideFreqStr + 
               '&Submit=Submit')
    #print '[info]: Downloading ', request    
           
    lines = transfer.readlines_ssl (request)
    
    ## Parse the response
    dates  = []
    values = []   
    for line in lines:
        if ('waterlevel' in product):
            try:
                dates.append  (datetime.strptime(line[13:29],'%Y-%m-%d %H:%M'))
                values.append (float(line[31:38]))
            except:
                pass
        elif product == 'predictions':
            try:
                dates.append  (datetime.strptime(line[ 9:25],'%m/%d/%Y %H:%M'))
                values.append (float(line[26:]))
            except: 
                pass
        elif product == 'barometricpressure':
            try:
                dates.append  (datetime.strptime(line[13:29],'%Y-%m-%d %H:%M'))
                values.append (float(line[30:37]))
            except: 
                pass
        elif product == 'wind':
            try:
                dates.append  (datetime.strptime(line[13:29],'%Y-%m-%d %H:%M'))
                values.append ([float(line[30:37]),
                                float(line[38:45]),
                                float(line[46:53])])
            except: 
                pass
        else:
            print '[error]: product [' + product + '] is not yet implemented!'
            break
        
    return {'dates' : dates, 'values' : values}       


#==============================================================================
def getStationInfo (stationID):
    
    """
    Downloads geographical information for a CO-OPS station
    from http://tidesandcurrents.noaa.gov
    
    Args:
        stationID (str):              7 character-long CO-OPS station ID
    
    Returns:
        'info' (dict): ['name']['state']['lon']['lat']

    Examples:
        & getStationInfo('8518750')['name']
        & 'The Battery'
    """
    request = ( 'https://tidesandcurrents.noaa.gov/stationhome.html?id=' +
               stationID )

    lines = transfer.readlines (request)    
    
    try:
        for line in lines:
            if 'var station_name'  in line:
                stationName  = line.split('"')[1]
            if 'var station_state' in line:
                stationState = line.split('"')[1]
            if 'var lat'           in line:
                lat          = float(line.split('"')[1])
            if 'var lon'           in line:
                lon          = float(line.split('"')[1])           
        
        return {'name'  : stationName, 
                'state' : stationState,
                'lon'   : lon, 
                'lat'   : lat }
    except:
        print '[error]: cannot get info for  ' + stationID
        return None

#==============================================================================
def getActiveStations ():
    """
    Downloads and parses the list of CO-OPS active tide gauges.
    """
    request = 'https://access.co-ops.nos.noaa.gov/nwsproducts.html?type=current'
    lines = transfer.readlines (request)    

    nos_id = []
    nws_id   = []
    for line in lines:        
        if line[0:4] == '<br>':
            stid = line[5:12]
            try:
                stid = int(stid)                
                nos_id.append(stid)    
                nws_id.append(line[13:18])    
            except:
                pass                    
    return {'nos' : nos_id,
            'nws' : nws_id}

#==============================================================================
def bias_table (csvFile, dates):
    """
    Alternative to SHEF bulletin.
    Reads all active CO-OPS stations via openDAP, computes bias\
    and writes into a file in comma-delimited format
    """
    rightNow = datetime.utcnow()    

    f = open(csvFile,'w')
    header = 'NOS-ID, NWS-ID, lon, lat, Bias MSL (meters), Length of record (days),' + \
              datetime.strftime(dates[0],'%Y%m%d') +'--' + \
              datetime.strftime(dates[1],'%Y%m%d') + '\n'
    f.write(header)

    active = getActiveStations()

    for count in range(len(active['nos'])):
        
        nos_id = str(active['nos'][count])
        nws_id   = str(active['nws'][count])        
        
        try:
            info = getStationInfo (nos_id)
            wlv  = getData(nos_id, dates, product='waterlevelrawsixmin')
            bias = np.mean(wlv['values'])
            if not np.isnan(bias):
                N    = len(wlv['values'])
                line = nos_id + ',' + nws_id + ','
                line = line + str(info['lon']) + ','
                line = line + str(info['lat']) + ','
                line = line + str(bias) + ','
                line = line + str(N/240.) + '\n'
                f.write(line)                    
        except:
            print '[warn]: failed to read ' + str(nos_id)
            
    f.close()
    print '[info]: elapsed time:', (datetime.utcnow()-rightNow).seconds, ' sec'
   

#==============================================================================
def read_bias_table (csvFile, column=4):
    """
    Reads lon, lat and bias from the bias table.
    column=4 is MSL meters
    """
    f = open(csvFile,'r')
    lines = f.readlines()
    xo = []
    yo = []
    zo = []
    dates = lines[0].split(',')[-1]
    for line in lines[1:]:
        sline = line.split(',')
        xo.append(float(sline[2]))
        yo.append(float(sline[3]))
        zo.append(float(sline[column]))
    f.close()
    return xo, yo, zo, dates

