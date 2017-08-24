# -*- coding: utf-8 -*-
"""
Created on Thu Mar 20 09:57:00 2017

@author: Sergey.Vinogradov
"""

import numpy as np
import matplotlib
matplotlib.use('Agg',warn=False)
import matplotlib.pyplot as plt
import matplotlib.tri    as tri

from csdlpy import interp, valstat, transfer

#==============================================================================
def save (fileName): 
    plt.savefig ( fileName)

#==============================================================================
def getCoastline (res = 'low'): 
    """
    Downloads NOAA coastline from OCS ftp    
    """
    coastlineFile = "./coastline.txt"
    request = 'ftp://ocsftp.ncd.noaa.gov/estofs/data/'
    if res is 'low':
        request = request + 'noaa_coastline_world.dat'
    else:
        request = request + 'noaa_coastline_usa.dat'

    transfer.download (request, coastlineFile)
#    if not os.path.exists(coastlineFile):    
#        print '[info]: retrieving coastline from ', request
#        urllib.urlretrieve (request, coastlineFile)

    f = open(coastlineFile,'r')
    xc = []
    yc = []
    for line in f:
        xc.append(float(line.split()[0]))
        yc.append(float(line.split()[1]))
    f.close()        

    return {'lon' : xc, 
            'lat' : yc}

#==============================================================================
def plotCoastline (coast, col='0.5'): 
    plt.plot(coast['lon'], coast['lat'],',',color=col,zorder=1)

#==============================================================================
def plotMap (x, y, fig_w=8.0, lonlim=None, latlim=None): 
    """
    Plots the "map" without using Basemap backend:
    parallels, meridians, coastline 
    """
    
    minx = np.floor(np.nanmin(x))
    maxx = np.ceil(np.nanmax(x))
    miny = np.floor(np.nanmin(y))
    maxy = np.ceil(np.nanmax(y))
    
    fig_h = np.round(fig_w*(maxy-miny)/(maxx-minx),2)
    print '[info]: Creating a figure ', str(fig_w),'x',str(fig_h), 'inches.'
    
    fig = plt.figure(figsize=[fig_w, fig_h])
    if lonlim is None:
        plt.xlim([minx, maxx])
    else:
        plt.xlim(lonlim)
    if latlim is None:
        plt.ylim([miny, maxy])
    else:
        plt.ylim(latlim)
    fig.tight_layout()

    # Draw parallels
    dx = maxx - minx
    dy = maxy - miny
    if dx < 10.:
        dx = 1.
    elif dx < 100.:
        dx = 10.
    else:
        dx = 20.
    if dy < 10.:
        dy = 1.
    elif dy < 100.:
        dy = 10.
    else:
        dy = 20.
    meridians = np.arange(np.floor(minx/10.)*10.,np.ceil(maxx/10.)*10.,dx)
    parallels = np.arange(np.floor(miny/10.)*10.,np.ceil(maxy/10.)*10.,dy)
    
    for m in meridians:
        plt.plot([m,m],[miny,maxy],':',color='gray',linewidth=1,zorder=0)
    for p in parallels:
        plt.plot([minx,maxx],[p,p],':',color='gray',linewidth=1,zorder=0)
    plt.tick_params(labelsize=7)    
    
    # Draw coastline
    coast = getCoastline (res = 'low')
    plotCoastline(coast,col='0.75') 
    return fig

#==============================================================================
def addPoints (data, ssize = 20, clim=[-0.5, 0.5], cmap=None):
    """
    Plots sparse data as circles
    """
    print '[info]: Plotting the points.'
    x = data[0]
    y = data[1]
    v = data[2]    
    
    if cmap is None:
        cmap = plt.cm.jet        
    plt.scatter (x, y, c=v, marker='o', s=ssize, edgecolors='k', cmap = cmap, zorder=10)
    plt.clim(vmin=clim[0], vmax=clim[1])

#==============================================================================
def addTriangles (data, threshold=0.0, clim=[-0.5, 0.5], cmap=None):
    """
    Plots sparse data as triangles, uward- or downward-looking depending
    if the value exceeds a threshold or not.
    """
    print '[info]: Plotting the triangles.'
    x = data[0]
    y = data[1]
    v = data[2]    
    
    # Block below can be somehow optimized, right?
    ind_up = [i for i, e in enumerate (v) if e >= threshold]
    ind_dn = [i for i, e in enumerate (v) if e <  threshold]   
    xup  = [x[i] for i in ind_up]
    yup  = [y[i] for i in ind_up]
    vup  = [v[i] for i in ind_up]   
    xdn  = [x[i] for i in ind_dn]
    ydn  = [y[i] for i in ind_dn]
    vdn  = [v[i] for i in ind_dn]

    if cmap is None:
        cmap = plt.cm.jet        
    plt.scatter (xup, yup, c=vup, marker='^', edgecolor='none', lw='0',
                 cmap = cmap, vmin=clim[0], vmax=clim[1], alpha=1,zorder=10)
    plt.scatter (xdn, ydn, c=vdn, marker='v', edgecolor='none', lw='0',
                 cmap = cmap, vmin=clim[0], vmax=clim[1], alpha=1,zorder=10)        
    
    
    plt.colorbar()    
    
#==============================================================================
def addSurface (grid, surface, 
                 clim=[0.0, 3.0]):
    """
    Plots a field specified on an unstructured grid
    Args:
        grid    (dict)   : grid     as read by adcirc.readGrid ()
        surface (array or masked_array) : 
                   field as read by adcirc.readSurfaceField ()
    Optional:
        clim ([float, float])  : color limits, ([0.0, 3.0] = default)
    Returns:
        fig (matplotlib figure handle) 
    Uses:
        grid = adcirc.readGrid ('fort.14')    
        plotSurface (grid, grid['depth'],clim=[-100, 4000])
    """
    
    print '[info]: Plotting the surface.'
    lon       = grid['lon']
    lat       = grid['lat']
    triangles = grid['Elements']
    z         = surface
    Tri       = tri.Triangulation(lon, lat, triangles=triangles-1)
        
    if hasattr(z,'mask'): 
        zmask = z.mask
    else:
        zmask = np.ones(len(z), dtype=bool)
    # Set mask 
    # TODO : Optimize this following loop
    #
    mask = np.ones(len(Tri.triangles), dtype=bool)
    count = 0
    for t in Tri.triangles:
        count+=1
        ind = t
        if np.any(zmask[ind-1]):
            mask[count-1] = False    
    Tri.set_mask = mask

    myCmap = plt.cm.jet
    plt.tripcolor(Tri, z, shading='gouraud',\
                         edgecolors='none', \
                         cmap=myCmap, vmin=clim[0], vmax=clim[1])
    
    cbar = plt.colorbar()
    cbar.ax.tick_params(labelsize=8) 

#====================================================================
def plot_estofs_timeseries (obs_dates,      obs_values, 
                            mod_dates,      mod_values, 
                            figFile=None,   stationName=None, 
                            htp_dates=None, htp_vals=None, 
                            daterange=None, ylim=[-2.0, 2.0]):
    """
    Project obs and model onto the same timeline;
    Compute RMSD
    """
    #Sort by date
    obs_dates  =  np.array(obs_dates)
    obs_values =  np.array(obs_values)
    ind = np.argsort(obs_dates)
    obs_dates  = obs_dates[ind]
    obs_values = obs_values[ind]
    # Remove nans
    ind = np.logical_not(np.isnan(obs_values))
    obs_dates   = obs_dates[ind]
    obs_values  = obs_values[ind]
    
    #Sort by date
    mod_dates  =  np.array(mod_dates)
    mod_values =  np.array(mod_values)
    ind = np.argsort(mod_dates)
    mod_dates  = mod_dates[ind]
    mod_values = mod_values[ind]
    
    #Rid of mask
    if hasattr(mod_values,'mask'):
        ind = ~mod_values.mask
        mod_dates   = mod_dates[ind]
        mod_values  = mod_values[ind]
    # Remove nans
    ind = np.logical_not(np.isnan(mod_values))
    mod_dates   = mod_dates[ind]
    mod_values  = mod_values[ind]

    refStepMinutes=6
    refDates, obsValProj, modValProj = \
             interp.projectTimeSeries(obs_dates, obs_values, 
                                      mod_dates, mod_values, 
                                      refStepMinutes)

    rmsd = valstat.rms (obsValProj-modValProj) 
    N    = len (obsValProj)

    if figFile:
        print '[info]: creating a plot ', figFile
        plt.figure(figsize=(20,4.5))
        if htp_dates is not None:
            plt.plot(htp_dates, htp_vals, color='c',label='TIDE')
        plt.plot(obs_dates, obs_values, '.', color='g',label='OBS')
        plt.plot(mod_dates, mod_values, '.', color='b',label='MOD')
        plt.ylim( ylim )
        if daterange is not None:
            plt.xlim ([daterange[0], mod_dates[-1]])
        if rmsd > 0:
            plt.title(stationName+', RMSD=' +str(rmsd)+' meters')
        else:
            plt.title(stationName)
        plt.legend(bbox_to_anchor=(0.9, 0.35))
        plt.grid()
        plt.xlabel('DATE UTC')
        plt.ylabel('WL, meters LMSL')
        plt.savefig( figFile )
        plt.close()
    return {'rmsd' : rmsd,
            'N'    : N}    
