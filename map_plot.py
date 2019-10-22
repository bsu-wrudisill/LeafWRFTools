"""
----------------------------------------------------------------------
Creates Panel Plots of 



----------------------------------------------------------------------
"""


import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib import ticker
from mpl_toolkits.basemap import Basemap
from netCDF4 import Dataset
import sys,os



class diff_plots:
  def __init__(self, filename, variable):
    self.filename = filename
    self.var      = variable
    self.timestep = 0
  
  def ncdiff(self, file1, file2,var):
    def read(f,var,timestep):
      ds      = Dataset(f)
      var     = ds.variables[var][timestep, :, :]
      ds.close()
      return var
    return read(file1, var, self.timestep) - read(file2, var, self.timestep) 


  def add_diff(self, fileA, fileB, fig, new_ax, title, var, **kwargs):

    diff = self.ncdiff(fileA, fileB, var)
    m_diff = ma.masked_equal(diff, 0)

    vmin = kwargs.get('vmin', m_diff.min())
    vmax = kwargs.get('vmax', m_diff.max())

    self.bmap_args['ax'] = new_ax
    basemap = Basemap(**self.bmap_args)
    clr  = basemap.pcolor(self.x, self.y, m_diff, vmin=vmin, vmax=vmax, cmap='bwr')
    cb = fig.colorbar(clr, ax=new_ax, fraction=0.04, pad=0.02)
    cb.ax.tick_params(labelsize=5) 
    tick_locator = ticker.MaxNLocator(nbins=5)
    cb.locator = tick_locator
    cb.update_ticks()



#    new_ax.set_title(title)
#    new_ax.set_xlabel('K')
    #---Define parallels and meridians to draw.
    parallels = np.arange(20., 60, 5)
    meridians = np.arange(-120., -60., 60)
    basemap.drawcoastlines(linewidth=1.5)
    basemap.drawparallels(parallels)
    basemap.drawmeridians(meridians)
    basemap.drawstates()


  def make_plot(self, fig, ax, title, **kwargs):
      
    #---Open file and read some variables
    ds      = Dataset(self.filename)
    var     = ds.variables[self.var][0, :, :]
    xlon    = ds.variables['XLONG'][0, :, :]
    xlat    = ds.variables['XLAT'][0, :, :]
    varmask = ma.masked_equal(var, 0)
    

    #---Read file attributes
    #atts         = file.ncattrs
    map_proj     = ds.getncattr('MAP_PROJ')
    dx           = ds.getncattr('DX')
    dy           = ds.getncattr('DY')
    truelat1     = ds.getncattr('TRUELAT1')
    truelat2     = ds.getncattr('TRUELAT2')
    cen_lat      = ds.getncattr('MOAD_CEN_LAT')
    cen_lon      = ds.getncattr('STAND_LON')
    mx           = ds.getncattr('WEST-EAST_GRID_DIMENSION')
    my           = ds.getncattr('SOUTH-NORTH_GRID_DIMENSION')
    mz           = ds.getncattr('BOTTOM-TOP_GRID_DIMENSION')
    ds.close()

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

    bmap_args = { 'projection':'lcc',
                  'lon_0':cen_lon,
                  'lat_0':cen_lat,
                  'lat_1':truelat1,
                  'lat_2':truelat2,
                  'llcrnrlat':lat_ll,
                  'urcrnrlat':lat_ur,
                  'llcrnrlon':lon_ll,
                  'urcrnrlon':lon_ur,
                  'resolution':'l',
                  'ax': ax}

    self.bmap_args = bmap_args
    basemap = Basemap(**bmap_args)
    #---Compute native x,y coordinates of grid.
    x, y = basemap(xlon, xlat)
    self.x = x
    self.y = y
    
    #---colorbar, axes title
    vmin = kwargs.get('vmin', varmask.min())
    vmax = kwargs.get('vmax', varmask.max())
    


    CS1 = basemap.pcolor(x, y, varmask, vmin=vmin, vmax=vmax)
    cb = fig.colorbar(CS1, ax=ax, fraction=0.04, pad=0.02)
    tick_locator = ticker.MaxNLocator(nbins=5)
    cb.locator = tick_locator
    cb.ax.tick_params(labelsize=5) 
    cb.update_ticks()

 #   ax.set_title(title)
 #   ax.set_xlabel('K')

    #---Define parallels and meridians to draw.
    parallels = np.arange(20., 60, 5)
    meridians = np.arange(-120., -60., 60)
    basemap.drawcoastlines(linewidth=1.5)
    basemap.drawparallels(parallels)
    basemap.drawmeridians(meridians)
    basemap.drawstates()

  def __call__(self):
    return self.basemap, self.x, self.y




#----------------------------------------#
# MAIN PLOTTING
#----------------------------------------#




#flist = [
#"/home/wrudisill/scratch/WRF_PROJECTS/wrf_cfsr_1996123000_1997010100_INIT_1996-12-31",0
#"/home/wrudisill/scratch/WRF_PROJECTS/wrf_cfsr_1996123000_1997010100_INIT_2003-11-20",1
#"/home/wrudisill/scratch/WRF_PROJECTS/wrf_cfsr_1996123000_1997010100_INIT_2016-03-14",2
#"/home/wrudisill/scratch/WRF_PROJECTS/wrf_cfsr_1996123000_1997010100_INIT_2005-12-30",3
#"/home/wrudisill/scratch/WRF_PROJECTS/wrf_cfsr_1996123000_1997010100_INIT_1996-01-27"]4
# flist = [
# "/home/wrudisill/scratch/WRF_PROJECTS/INIT/wrf_cfsr_1996123000_1997010100_INIT_1996-01-27",
# "/home/wrudisill/scratch/WRF_PROJECTS/INIT/wrf_cfsr_1996123000_1997010100_INIT_1996-12-31"]


# ----- WRFOUT Subset to Plot ------# 
base='/Volumes/PASSPORT/wrfout/THESIS_WRF_PROJECTS/1997_AR/'
flist = [base+'subset_wrf_cfsr_1996-12-28_00__1997-01-08_00_INIT_1990-09-10_D01D02',
         base+'subset_wrf_cfsr_1996-12-28_00__1997-01-08_00_INIT_1996-01-27_D01D02']

out  = "/precip_wrfout_d02_1997-01-07_00:00:00"

# ----- WRFinput files to show alongside ------# 
init1 = "/Volumes/PASSPORT/wrfout/wrfin/" + 'init_snow_1990_d02.nc'
inti2 = "/Volumes/PASSPORT/wrfout/wrfin/" + 'init_snow_1996_d02.nc'


variable = "RAINNC_TOTAL"


fig, axes = plt.subplots(5,3)


aa = diff_plots(init1, "SNOWC")
a = diff_plots(flist[0]+out, variable)
b = diff_plots(flist[1]+out, variable)


#variable, Left Colu
a.make_plot(fig, axes[0,1], variable)
b.make_plot(fig, axes[1,1], variable)

# variable Diff; Center column
#a.add_diff(flist[0]+out,flist[0]+out, fig, axes[0,2], ' ', variable)#, vmin=-5, vmax=5)
a.add_diff(flist[1]+out,flist[0]+out, fig, axes[1,2], ' ', variable, vmin=-7, vmax=7)
#a.add_diff(flist[2]+out,flist[0]+out, fig, axes[2,2], ' ', variable, vmin=-7, vmax=7)


#add_diff(fileA, filesB) shows fileA - fileB
# SNOWH Diff; Right Columns
aa.make_plot(fig, axes[0,0], 'SNOWC', vmin=0, vmax=1)

diff_plots(init1, "SNOWC").make_plot(fig, axes[1,0], "SNOWC", vmin=0, vmax=1)
diff_plots(init2, "SNOWC").make_plot(fig, axes[2,0], "SNOWC", vmin=0, vmax=1)

fig.suptitle('T2', fontsize=14, fontweight='bold')
axes[0,2].axis('off')
axes[2,2].axis('off')


plt.savefig('RAINNC_TOTAL.png', dpi=200)
fig.clf()
plt.clf()
del fig
del axes

print 'done'