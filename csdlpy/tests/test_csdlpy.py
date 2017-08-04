# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 10:02:14 2017

@author: Sergey.Vinogradov
"""

import os
import getopt
import matplotlib
import numpy as np
matplotlib.use('Agg',warn=False)
import matplotlib.pyplot as plt
import sys
from datetime import datetime as dt
#==============================================================================
def run_test_csdlpy (argv):
    
    toolkitPath = ''
    
    try:
        opts, args = getopt.getopt(argv,"ht:",["help","toolkitPath="])
    except getopt.GetoptError:
        print 'test_csdlpy.py -t <toolkitPath>'        
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'test_csdlpy.py -t <toolkitPath>'
        elif opt in ("-t", "--toolkitPath"):
            toolkitPath = arg

    test_csdlpy (toolkitPath)

#==============================================================================
def test_csdlpy (toolkitPath):    
    
    sys.path.insert(0,toolkitPath)

    from csdlpy import version
    ver = version.__version__
    
    #........................................................................
    # Input
    webLoc_gridFile   = "ftp://ocsftp.ncd.noaa.gov/estofs/atl/fort.14"
    webLoc_stnFile    = "ftp://ocsftp.ncd.noaa.gov/estofs/atl/stations.txt"
    webLoc_maxeleFile = \
    "ftp://ocsftp.ncd.noaa.gov/estofs/hsofs-atl/2016_Matthew/best.2016092300.biasCorr/maxele.63.nc"
    webLoc_trackFile  = \
    "ftp://ocsftp.ncd.noaa.gov/estofs/hsofs-atl/2016_Matthew/best.2016092300/fort.22"
    #........................................................................
    # Output
    tableFile      = './bias_table.csv'
    offsetFile     = './Offset.63'
    biasPlotFile   = './test_csdlpy_2016_Matthew_bias.png'
    maxelePlotFile = './test_csdlpy_2016_Matthew_maxele.png'
    #........................................................................
    
    
    print '\n***************************************************************\n' 
    now = dt.now() # timer
    print '[test]: Initiating csdlpy version ' + ver + ' test at ' + \
           dt.strftime(now,'%Y/%m/%d %H:%M:%S')
    print '[test]: sourced from ',  toolkitPath + '\n'
    
    print '[test]: We will attempt to download these required files: '
    print webLoc_gridFile
    print webLoc_stnFile
    print webLoc_maxeleFile
    print webLoc_trackFile
    print '[test]: Otherwise, you need to provide them to your workdir manually.\n'
    print '[warn]: If you do not have web access, comment out CO-OPS data block.\n'
    print '[test]: Test will produce the following files:'
    print tableFile
    print offsetFile
    print biasPlotFile
    print maxelePlotFile
    print '\n'
    print '[test]: Please share your benchmark result and log file with us'
    print '[test]: Sergey.Vinogradov@noaa.gov\n'
    
    from csdlpy import adcirc
    from csdlpy import transfer
    from csdlpy import plotter
    from csdlpy import obs
    from csdlpy import interp
    from csdlpy import atcf
   
    print '[test]: # Download ESTOFS-Atl grid file...'    
    gridFile = "./fort.14"
    transfer.download (webLoc_gridFile, gridFile)
    grid = adcirc.readGrid ( gridFile )    

    # CO-OPS data block starts ###############################################
    print '[test]: # Compute data biases...'
    if not os.path.exists (tableFile):
        obs.coops.bias_table(tableFile, 10.0, now=dt(2016,9,23))
    xo,yo,vo = obs.coops.read_bias_table (tableFile)    

    print '[test]: # Compute bias surface on the grid...'    
    vg = np.zeros(len(grid['depth']), dtype=float)
    
    # Interpolation parameters...............................................
    z_full  = 0.   # meters
    z_zero  = 200. # meters
    p       = 2.0  # scalar 
    R       = 2.0  # degrees
    #........................................................................
        
    print '[test]: ## Interpolate on the shelf...'
    ind_shelf     = np.where(grid['depth'] < z_zero)[0]
    vg[ind_shelf] = interp.shepard_idw (xo, yo, vo, grid['lon'][ind_shelf], 
                                                    grid['lat'][ind_shelf], p)

    print '[test]: ## Taper by depth...'
    ind_taper     = np.where (np.logical_and(z_full <= grid['depth'], 
                                             z_zero >= grid['depth']))[0]    
    vg[ind_taper] = interp.taper_linear (z_full, z_zero, 
                                          grid['depth'][ind_taper], 
                                          vg[ind_taper])
    
    print '[test]: ## Zero out the results that are too distant from data'
    dist = interp.distance_matrix(xo, yo, grid['lon'], grid['lat'])
    for n in range(len(grid['lon'])):
        if np.min(dist[:,n]) > R:
            vg[n] = 0.

    print '[test] :## Write out Offset file'
    adcirc.writeOffset63 (vg, offsetFile)
    
    print '[test]: ## Plot bias surface and data'
    plotter.plotMap    (grid['lon'], grid['lat'],   fig_w=8.0)
    plotter.addSurface (grid,    vg, clim=[-0.3, 0.3])
    plotter.addTriangles ((xo,yo,vo),clim=[-0.3,0.3])
    plt.title(grid['GridDescription'],fontsize=8)
    plt.savefig(biasPlotFile)
    plt.close()
    # CO-OPS data block ends #################################################


    print '[test]: # Download stations file'    
    stnFile = "./stations.txt"
    transfer.download (webLoc_stnFile, stnFile)
    stations = adcirc.read_adcirc_stations(open(stnFile,'r'))    

    print '[test]: # Download 2016 Matthew hindcast maxele'    
    maxeleFile = "./maxele.63.nc"
    transfer.download (webLoc_maxeleFile, maxeleFile)    
    maxele = adcirc.readSurfaceField ( maxeleFile )    

    print '[test]: # Download 2016 Matthew best track'    
    trackFile = "./fort.22"
    transfer.download (webLoc_trackFile, trackFile )    
    track = atcf.readTrack( trackFile )    

    print '[test]: # Plot maxele file '
    plotter.plotMap    (grid['lon'], grid['lat'],   fig_w=8.0)
    plotter.addSurface (grid,    maxele['value'], clim=[0.,3.])
    plt.plot(track['lon'],track['lat'],'o-k',markersize=2)
    plt.title(grid['GridDescription'],fontsize=8)    

    plt.scatter (stations['lon'], stations['lat'], 
                 c='r', marker='o', s=20, edgecolors='w')

    for n in range(len(stations['lon'])):
        plt.text(stations['lon'][n], stations['lat'][n], 
                 str(n+1).zfill(3), fontsize=6)
    plt.savefig(maxelePlotFile)

    print '\n'
    print '[test]:[total runtime]: ', (dt.now()-now).seconds, ' sec'

    transfer.cleanup()
    
#==============================================================================
if __name__ == "__main__":
    run_test_csdlpy (sys.argv[1:])    
    
