
"""
----------------------------------------------------------------------
-Scripts for plotting WRF output Domain w/ some field
-plots cross section lines across domain from lat/lon
----------------------------------------------------------------------
"""


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.basemap import Basemap
from netCDF4 import Dataset
import sys,os



# plotting points 


#end  =  {'lat':42.3939, 'lon':-116.8766,  'label':'Boise'}  # Boise 
#start = {'lat':44.202, 'lon': -114.95,  'label':'Stanley'}  # Stanley



# read files, set vars, etc.
def plot_cross_section(start, end, ax):
    """
    ----------------------------------------------------------------------
    Plots the height field of a geo_em file. optionally plots a line 
    (or maybe.. multiple eventually) between a set of specified lat 
    lon points. 

    ----------------------------------------------------------------------
    """



    filename = "/scratch/wrudisill/WRF_Post/aux_files/geo_em.d02.nc"
    varname  = "HGT_M"
    index = 0


    #---Open file and read some variables
    #file  = Nio.open_file(filename)
    file  = Dataset(filename)
    xlon  = file.variables['XLONG_M'][0, :, :]
    xlat  = file.variables['XLAT_M'][0, :, :]
    hgt   = file.variables['HGT_M'][0, :, :]


    #---Read file attributes
    #atts         = file.ncattrs
    map_proj     = file.getncattr('MAP_PROJ')
    dx           = file.getncattr('DX')
    dy           = file.getncattr('DY')
    truelat1     = file.getncattr('TRUELAT1')
    truelat2     = file.getncattr('TRUELAT2')
    cen_lat      = file.getncattr('MOAD_CEN_LAT')
    cen_lon      = file.getncattr('STAND_LON')
    mx           = file.getncattr('WEST-EAST_GRID_DIMENSION')
    my           = file.getncattr('SOUTH-NORTH_GRID_DIMENSION')
    mz           = file.getncattr('BOTTOM-TOP_GRID_DIMENSION')


    if map_proj != 1:
        print("Error: the data on %s do not appear to be on a lambert conformal projection." % filename)
        sys.exit(1)

    #---Calculations needed for map projection
    lat_ll = xlat[0,0]
    lat_ur = xlat[-1,-1]
    lon_ll = xlon[0,0]
    lon_ur = xlon[-1,-1]
    width_meters  = dx * (mx - 1)
    height_meters = dy * (my - 1)

    basemap = Basemap(projection='lcc',
            lon_0=cen_lon,
            lat_0=cen_lat,
            lat_1=truelat1,
            lat_2=truelat2,
            llcrnrlat=lat_ll,
            urcrnrlat=lat_ur,
            llcrnrlon=lon_ll,
            urcrnrlon=lon_ur,
            resolution='l',
            ax = ax)

    #---Compute native x,y coordinates of grid.
    x, y = basemap(xlon, xlat)

    #---Create figure, add axes
    #fig = plt.figure(figsize=(8,10))
    #ax = fig.add_axes([0.1,0.1,0.8,0.8])

    #---Plot contours
    clevs = np.arange(0, 3500, 20)
    CS1 = basemap.contourf(x, y, hgt, clevs, cmap=cm.jet)


    #---Define parallels and meridians to draw.
    parallels = np.arange(20., 60, 5)
    meridians = np.arange(-120., -60., 60)
    basemap.drawcoastlines(linewidth=1.5)
    basemap.drawparallels(parallels)
    basemap.drawmeridians(meridians)
    basemap.drawstates()

    # plot line segment between to points (lat, lon)
    lo_ = [start[1], end[1]]
    la_ = [start[0], end[0]]
    # lat lon to projection space
    lx, ly = basemap(lo_, la_)
    basemap.plot(lx, ly)
    

if __name__== '__main__':
    fig = plt.figure(figsize=(8,10))
    ax = fig.add_axes([0.1,0.1,0.8,0.8])

    start = (45.500, -113.943)
    end   = (42.800, -113.943)

    plot_cross_section(start, end, ax)

    #---Set plot title
    # ax.set_title(varname)
    plt.show()
#    plt.savefig('outfig', bbox_inches='tight')
    del fig 
    del ax
    plt.clf()

