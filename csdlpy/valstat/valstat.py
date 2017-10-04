# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 13:07:49 2017

@author: Sergey.Vinogradov
"""
import numpy as np

#============================================================================== 
def nearest(items, pivot):
    """
    Finds an item in 'items' list that is nearest in value to 'pivot'
    """
    nearestVal = min(items, key=lambda x: abs(x - pivot))
    try:
        items = items.tolist()
    except:
        pass
    indx = items.index(nearestVal)
    return nearestVal, indx

#==============================================================================
def rms(V):
    """
    Returns Root Mean Squared of the time series V (np.array)
    """    
    ind  = np.logical_not(np.isnan(V))
    V    = V[ind]
    summ = np.sum(V**2)
    N    = 1.0*len(V)
    return np.sqrt( summ/N )

#==============================================================================
def metrics (data, model, dates):
    """    
    data and model (np.arrays) projected on the 
    same time scale 'dates' (datetime)
    Computes: 
        rmsd, peak, plag (in minutes)    
    """
    rmsd = rms(data-model)
    peak = np.nanmax(data) - np.nanmax(model)
    plag = 60.*(dates[np.argmax(data)] - dates[np.argmax(model)]).total_seconds 
    
    return {'rmsd': rmsd, 
            'peak': peak,
            'plag': plag}
#            'vexp': vexp,
#            'bias': bias,
#            'rval': rval,
#            'skil': skil,
#            'npts': npts}
