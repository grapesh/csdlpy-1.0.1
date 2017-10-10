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
def var_explained(m, d):
    """
    Returns amount of variance in d that is explained by variance in m
    """    
    stdd =    np.nanstd(d)
    eps  =    100.*(stdd - np.nanstd(d-m))/stdd
    if eps <  0:
        eps = 0.
    if eps >  100.:
        eps = 100
    return eps

#==============================================================================
def skill(m, d):
    """
    Returns the skill
    """    
    skill = 1-np.nansum((m-d)**2)/ np.nansum( (np.abs(m-np.nanmean(d)) + np.abs(d-np.nanmean(d)))**2 )
    return skill

#==============================================================================
def rvalue(m, d):
    """
    Returns R-value (Pearson correlation coefficient)
    """    
    rval = np.nansum( (d-np.nanmean(d))*(m-np.nanmean(d)) ) / \
                    (np.sqrt(np.nansum( (d-np.nanmean(d))**2 ))* \
                     np.sqrt(np.nansum( (m-np.nanmean(m))**2 )) )
    return rval

#==============================================================================
def metrics (data, model, dates):
    """    
    data and model (np.arrays) projected on the 
    same time scale 'dates' (datetime)
    Computes: 
        rmsd - root mean square difference, in data units 
        peak - difference in max values in data and model, in data units
        plag - difference in occurrence time of the maxima, in minutes
        bias - linear bias, in data units 
        vexp - variance explained, in %
        skil - skill, unitless
        rval - R-value, unitless
    """
    rmsd = np.nan
    peak = np.nan
    plag = np.nan
    bias = np.nan
    vexp = np.nan
    skil = np.nan
    rval = np.nan
    
    npts = np.count_nonzero(~np.isnan(model-data)) 
    if npts:
        rmsd = rms(model-data)
        peak = np.nanmax(model) - np.nanmax(data)
        plag = (dates[np.argmax(model)] - dates[np.argmax(data)]).total_seconds() 
        plag = plag/60. #in minutes
        bias = np.nanmean(model) - np.nanmean(data)
        vexp = var_explained (model, data)
        skil = skill (model, data)
        rval = rvalue(model, data)
    
    return {'rmsd': rmsd, 
            'peak': peak,
            'plag': plag,
            'bias': bias,
            'vexp': vexp,
            'skil': skil,
            'rval': rval,
            'npts': npts}
