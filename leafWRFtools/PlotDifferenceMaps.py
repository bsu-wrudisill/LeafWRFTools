from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.patches import PathPatch
import numpy as np
from netCDF4 import Dataset
import xarray as xr
import datetime
import pandas as pd
from parms import soils_table, lu_table

def PlotBarbs(filename, U, V, fig, ax, plot_params): 

    # pass in paraeters w/ the 'plot_params' object 
    vmin = plot_params.vmin
    vmax = plot_params.vmax
    cmap = plot_params.cmap
    cblab = plot_params.cblab         
    extend = plot_params.extend
    ticks  = plot_params.ticks 
    ticklabels  = plot_params.ticklabels
    tickadjust  = plot_params.tickadjust
    title = plot_params.title
    cbFx = plot_params.cbFx
    # static params ---- ++++ CHANGE ME +++++
    
    shp_path = "/home/wrudisill/scratch/ThirtyYrAnalysis/WatershedAnalysis/Shapefiles/Boise/"
    shpfile = "transformed" 
    ds      = Dataset("./sample_wrf_file.nc")

    # GEOG FILE  
    xlon    = ds.variables['XLONG'][0, :, :]
    xlat    = ds.variables['XLAT'][0, :, :]
    HGT     = ds.variables['HGT'][0, :, :]

    # PLOTTING GOES BELOW HERE 
    #Read file attributes
    #atts         = file.ncattrsmap_proj     = ds.getncattr('MAP_PROJ')
    dx           = ds.getncattr('DX')
    dy           = ds.getncattr('DY')
    truelat1     = ds.getncattr('TRUELAT1')
    truelat2     = ds.getncattr('TRUELAT2')
    cen_lat      = ds.getncattr('MOAD_CEN_LAT')
    cen_lon      = ds.getncattr('STAND_LON')
    mx           = ds.getncattr('WEST-EAST_GRID_DIMENSION')
    my           = ds.getncattr('SOUTH-NORTH_GRID_DIMENSION')
    mz           = ds.getncattr('BOTTOM-TOP_GRID_DIMENSION')
    
    
    # ------- Calculations needed for map projection -----# 
    lat_ll = xlat[0,0]
    lat_ur = xlat[-1,-1]
    lon_ll = xlon[0,0]
    lon_ur = xlon[-1,-1]
    width_meters  = dx * (mx - 1)
    height_meters = dy * (my - 1)

    zoom_lat =1.0
    zoom_lon = 1.0
    extra_pad =.25

    bmap_args = { 'projection':'lcc',
                  'lon_0':cen_lon,
                  'lat_0':cen_lat,
                  'lat_1':truelat1,
                  'lat_2':truelat2,
                  'llcrnrlat':lat_ll+zoom_lat+3*extra_pad,
                  'urcrnrlat':lat_ur-1.2*zoom_lat,
                  'llcrnrlon':lon_ll+(zoom_lon+3.0*extra_pad),
                  'urcrnrlon':lon_ur-1.5*zoom_lon,
                  'resolution':'h',
                  'ax': ax}

    # Create the basemap
    m = Basemap(**bmap_args)

    # native coords for the grid --- needed to plot WRF var
    x, y = m(xlon, xlat)
    
    # for barb plotting 
    yy = np.arange(0, y.shape[0], 2)
    xx = np.arange(0, x.shape[1], 2)
    points = np.meshgrid(yy, xx)

    # create magnitude 
    MAG = np.sqrt(U**2 + V**2)


    # Add Coastlines, States, and Country Boundaries
    parallels = np.round(np.arange(np.round(lat_ll), np.round(lat_ur), .20), 2)
    meridians = np.round(np.arange(np.round(lon_ll), np.round(lon_ur), .20), 2)
    
    # ---------- Basemap map functions options --------# 
    #m.drawcoastlines(linewidth=1.5)
    m.drawparallels(parallels,labels=[1,0,0,1],fontsize=4,linewidth=.6,color="gray")
    m.drawmeridians(meridians,labels=[1,0,0,1],fontsize=4,linewidth=.6,color="gray")
    #m.drawstates()
    #m.drawmapscale(-115.8,43.20,-114.72,43.20, 50, "fancy")  # for the full domain
    m.drawmapscale(-116.25,42.85,-114.72,42.85, 200, "fancy")  # for the zoom in 

    # explicitly pass in ticklabels 
    if ticks:
        # do not use vmin vmax
        colormap = m.pcolor(x, y, MAG, cmap=plt.cm.get_cmap(cmap))# vmin=vmin, vmax=vmax)
        if ticklabels:
            cb = fig.colorbar(colormap, ticks= ticks, ax=ax, fraction=0.027, pad=0.01, extend=extend)
            cb.ax.get_yaxis().set_ticks([])
            for j, lab in enumerate(ticklabels.values()):
                k = 1.5 + j*tickadjust
                cb.ax.text(2.5, k, lab, va='center')
        else: # there are ticks, but no ticklabels
            cb = fig.colorbar(colormap, ticks=ticks, ax=ax, fraction=0.030, pad=0.01, extend=extend)# format=formatter
            cb.set_label(cblab,labelpad=-2, fontsize=5)   
            cb.ax.tick_params(labelsize=5)
    # ticks are not explicitly passed in; use vmin vmax instead
    else:  
        colormap = m.pcolor(x, y, MAG, cmap=plt.cm.get_cmap(cmap), vmin=vmin, vmax=vmax, alpha=.7)
        cb = fig.colorbar(colormap, ax=ax, fraction=0.064+cbFx, pad=0.01, extend=extend)# format=formatter
        cb.set_label(cblab,labelpad=-2, fontsize=8,rotation=90)
        cb.ax.tick_params(labelsize=5)
    # Read in the shapefile 
    # 
    # -- plot wind barbs -- 
    m.quiver(x[points],y[points],U[points],V[points], scale=100, pivot='mid', width=.003, )

    m.readshapefile(shp_path+shpfile, shpfile)
    patches = []

    for shape in getattr(m,shpfile):
        patches.append( Polygon(np.array(shape), True) )
        ax.add_collection(PatchCollection(patches, facecolor=None, edgecolor='k', linewidths=1., alpha=0, zorder=2))
    
    # DRAW TERRAIN CONTOURS 
    contourLines = m.contour(x,y,HGT,[2500., 3000., 3500.],linewidths=.4,colors='white', alpha=0.4) 
    ax.clabel(contourLines, inline=1, fontsize=5, fmt = {2500.:'2.5km',3000.:'3km',3500.0:'3.5km'})
    
    
    #=================================# 
    #------ END FUNCTION # 
    #=================================# 

def PlotShape(filename, VAR, fig, ax, plot_params): 

    # pass in paraeters w/ the 'plot_params' object 
    vmin = plot_params.vmin
    vmax = plot_params.vmax
    cmap = plot_params.cmap
    cblab = plot_params.cblab         
    extend = plot_params.extend
    ticks  = plot_params.ticks 
    ticklabels  = plot_params.ticklabels
    tickadjust  = plot_params.tickadjust
    title = plot_params.title
    # static params ---- ++++ CHANGE ME +++++
    #shp_path = "./gis_data/"
    #shpfile = "EastRiver_Shapefile"
    #ds      = Dataset("./sample_wrf_file_CO.nc")

    shp_path = "/home/wrudisill/scratch/ThirtyYrAnalysis/WatershedAnalysis/Shapefiles/Boise/"
    shpfile = "transformed" 
    ds      = Dataset("./sample_wrf_file.nc")
    
    # GEOG FILE  
    xlon    = ds.variables['XLONG'][0,:,:]
    xlat    = ds.variables['XLAT'][0,:,:]
    HGT     = ds.variables['HGT'][0,:,:] 
    # PLOTTING GOES BELOW HERE 
    #Read file attributes
    #atts         = file.ncattrsmap_proj     = ds.getncattr('MAP_PROJ')
    dx           = ds.getncattr('DX')
    dy           = ds.getncattr('DY')
    truelat1     = ds.getncattr('TRUELAT1')
    truelat2     = ds.getncattr('TRUELAT2')
    cen_lat      = ds.getncattr('MOAD_CEN_LAT')
    cen_lon      = ds.getncattr('STAND_LON')
    mx           = ds.getncattr('WEST-EAST_GRID_DIMENSION')
    my           = ds.getncattr('SOUTH-NORTH_GRID_DIMENSION')
    mz           = ds.getncattr('BOTTOM-TOP_GRID_DIMENSION')
    
    
    # ------- Calculations needed for map projection -----# 
    lat_ll = xlat[0,0]
    lat_ur = xlat[-1,-1]
    lon_ll = xlon[0,0]
    lon_ur = xlon[-1,-1]
    width_meters  = dx * (mx - 1)
    height_meters = dy * (my - 1)

    zoom_lat =1.0
    zoom_lon = 1.0
    extra_pad =.25

    bmap_args = { 'projection':'lcc',
                  'lon_0':cen_lon,
                  'lat_0':cen_lat,
                  'lat_1':truelat1,
                  'lat_2':truelat2,
                  'llcrnrlat':lat_ll+zoom_lat+3*extra_pad,
                  'urcrnrlat':lat_ur-1.2*zoom_lat,
                  'llcrnrlon':lon_ll+(zoom_lon+3.0*extra_pad),
                  'urcrnrlon':lon_ur-1.5*zoom_lon,
                  'resolution':'h',
                  'ax': ax}

    # Create the basemap
    m = Basemap(**bmap_args)

    # native coords for the grid --- needed to plot WRF var
    x, y = m(xlon, xlat)

    # Add Coastlines, States, and Country Boundaries
    parallels = np.round(np.arange(np.round(lat_ll), np.round(lat_ur), .20), 2)
    meridians = np.round(np.arange(np.round(lon_ll), np.round(lon_ur), .20), 2)
    
    # ---------- Basemap map functions options --------# 
    #m.drawcoastlines(linewidth=1.5)
    m.drawparallels(parallels,labels=[1,0,0,1],fontsize=4,linewidth=.6,color="gray")
    m.drawmeridians(meridians,labels=[1,0,0,1],fontsize=4,linewidth=.6,color="gray")
    #m.drawstates()
    #m.drawmapscale(-115.8,43.20,-114.72,43.20, 50, "fancy")  # for the full domain
    m.drawmapscale(-116.25,42.85,-114.72,42.85, 200, "fancy")  # for the zoom in 

    # -------- COLORBAR TICK LOGIC --------

    # explicitly pass in ticklabels 
    if ticks:
        # do not use vmin vmax
        colormap = m.pcolor(x, y, VAR, cmap=plt.cm.get_cmap(cmap))# vmin=vmin, vmax=vmax)
        if ticklabels:
            cb = fig.colorbar(colormap, ticks= ticks, ax=ax, fraction=0.027, pad=0.01, extend=extend)
            cb.ax.get_yaxis().set_ticks([])
            for j, lab in enumerate(ticklabels.values()):
                k = 1.5 + j*tickadjust
                cb.ax.text(2.5, k, lab, va='center')
        else: # there are ticks, but no ticklabels
            cb = fig.colorbar(colormap, ticks=ticks, ax=ax, fraction=0.030, pad=0.01, extend=extend)# format=formatter
            cb.set_label(cblab,labelpad=-2, fontsize=5)   
            cb.ax.tick_params(labelsize=5)
    # ticks are not explicitly passed in; use vmin vmax instead
    else:  
        colormap = m.pcolor(x, y, VAR, cmap=plt.cm.get_cmap(cmap), vmin=vmin, vmax=vmax)
        cb = fig.colorbar(colormap, ax=ax, fraction=0.064, pad=0.01, extend=extend)# format=formatter
        cb.set_label(cblab,labelpad=-2, fontsize=8,rotation=90)
        cb.ax.tick_params(labelsize=5)
    # Read in the shapefile 
    m.readshapefile(shp_path+shpfile, shpfile)
    patches = []

    for shape in getattr(m,shpfile):
        patches.append( Polygon(np.array(shape), True) )
        ax.add_collection(PatchCollection(patches, facecolor=None, edgecolor='k', linewidths=1., alpha=0, zorder=2))
    
    # DRAW TERRAIN CONTOURS 
    contourLines = m.contour(x,y,HGT,[2500., 3000., 3500.],linewidths=.4,colors='black', alpha=0.3) 
    ax.clabel(contourLines, inline=1, fontsize=5, fmt = {2500.:'2.5km',3000.:'3km',3500.0:'3.5km'})
    
    #=================================# 
    #------ END FUNCTION # 
    #=================================# 

class PlotPar():
    def __init__(self,**kwargs):
        self.var   = kwargs.get("var", "T2")
        self.cblab = kwargs.get("cblab", None)
        self.vmin = kwargs.get("vmin", -50)
        self.vmax = kwargs.get("vmax", 50)
        self.cmap = kwargs.get("cmap", "bwr")
        self.scale = kwargs.get("scale", 1)
        self.extend = kwargs.get("extend", "both")
        self.ticks = kwargs.get("ticks", None)
        self.ticklabels = kwargs.get("ticklabels", None)
        self.tickadjust = kwargs.get("tickadjust", 1.0)
        self.cbFx = kwargs.get("cbFx", 0)
        self.title = kwargs.get("title", 0)
    def __call__():
        return self


cmap_luindex = plt.cm.get_cmap("tab20", 18)
cmap_soilindex = plt.cm.get_cmap("tab20", 16)

if __name__ == '__main__':
	#import accessories as acc
	#ds = Dataset("./sample_wrf_file_CO.nc","r")["HGT"][0,:,:]
	#hillshade = acc.hillshade(ds, 60,30)	
	#
	#plist = PlotPar(var="HGT", scale=1, vmin = 2000, vmax = 4000, cmap='terrain', cblab="m",extend="max")

	#fig,ax = plt.subplots(1,1)
#	#fig.set_size_inches(8.4,5.0)
	#PlotShape('test', ds, fig, ax, plist)
	#
	#plt.subplots_adjust(right=.70)
	#plt.savefig("TERRAIN", dpi=600)
	#plt.cla()
	#plt.close(fig)

	ds = xr.open_mfdataset("/home/wrudisill/scratch/MasterThesis/WRF_Forcings/thesis_sims/MScase/wrfout*", concat_dim='Time')
	#U = ds["U10"].loc['2017-01-01'].values
	#V = ds["V10"].loc['2017-01-01'].values

	#plist = PlotPar(var="HGT", scale=1, vmin = 2000, vmax = 4000, cmap='terrain', cblab="m",extend="max")

#	#fig,ax = plt.subplots(1,1)
#	PlotBarbs('test', U,V, fig, ax, plist)
#	plt.subplots_adjust(right=.70)
#	plt.savefig("WINDS", dpi=600)
#	plt.cla()
#	plt.close(fig)
