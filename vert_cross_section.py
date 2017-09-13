import numpy as np
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
from netCDF4 import Dataset
from wrf import to_np, getvar, CoordPair, vertcross
import xarray as xr
from plot_domain import plot_cross_section

# Open the NetCDF file

'''
---------------------------------------
Plots vertical cross sections of domain and some field 
between a lat/lon point

---------------------------------------
'''


filenameA="/home/wrudisill/scratch/WRF_PROJECTS/wrf_cfsr_1996123000_1997010100_INIT_2003-11-20/wrf_out/wrfout_d02_1996-12-31_00:00:00"

filenameB="/home/wrudisill/scratch/WRF_PROJECTS/wrf_cfsr_1996123000_1997010100_INIT_2015-12-30/wrf_out/wrfout_d02_1996-12-31_00:00:00"

start = (44.0, -116.7)
end   = (44.0, -113.85)


#var = "uvmet_wspd_wdir"
var = 'wa'
plot_title= 'wa (m/s)'
plot_name= 'w_vertcross'

def vert_cross_section(filename, var,time):

    ncfile = Dataset(filename)

    # Extract the model height and wind speed
    z = getvar(ncfile, "z")
    

    #wspd =  getvar(ncfile, "uvmet_wspd_wdir", units="kt")[0,:]
    field =  getvar(ncfile, var, units='m s-1')
    # Create the start point and end point for the cross section

    start_point = CoordPair(lat= start[0], lon= start[1]) # Cascade
    end_point = CoordPair(lat=start[0],  lon= end[1])

    # Compute the vertical cross-section interpolation.  Also, include the lat/lon
    # points along the cross-section.
    field_cross = vertcross(field, z, wrfin=ncfile, start_point=start_point, end_point=end_point,
                            latlon=True,meta=True,timeidx=time)
    return field_cross


A = vert_cross_section(filenameA, var, 10) 
#a = to_np(A)
#for i in range(1,24):
#    print i
#    a = a + to_np(vert_cross_section(filenameA, var, i))

B = vert_cross_section(filenameB, var, 10) 
#b = to_np(B)
#for i in range(1,24):
#    print i
#    b = b + to_np(vert_cross_section(filenameA, var, i))




diff_array = to_np(B) - to_np(A)
#diff_array = a - b

# Create the figure
#fig,(ax0,ax1) = plt.subplots(1,2)
fig,ax1 = plt.subplots(1,1)

# Make the contour plot
levels = np.linspace(diff_array.min(), diff_array.max(), 50)
#print diff_array.min()

#wspd_contours = ax.contourf(to_np(wspd_cross), cmap=get_cmap("jet"), levels=levels)
contours = ax1.contourf(diff_array, cmap=get_cmap("jet"), levels=levels)

# Add the color bar
plt.colorbar(contours, ax=ax1)

# Set the x-ticks to use latitude and longitude labels.
coord_pairs = to_np(A.coords["xy_loc"])
x_ticks = np.arange(coord_pairs.shape[0])
x_labels = [pair.latlon_str(fmt="{:.2f}, {:.2f}") for pair in to_np(coord_pairs)]
ax1.set_xticks(x_ticks[::20])
ax1.set_xticklabels(x_labels[::20], rotation=45, fontsize=8)

# Set the y-ticks to be height.
vert_vals = to_np(A.coords["vertical"])
v_ticks = np.arange(vert_vals.shape[0])
ax1.set_yticks(v_ticks[::20])
ax1.set_yticklabels(vert_vals[::20], fontsize=8)
        
# Set the x-axis and  y-axis labels
ax1.set_xlabel("Latitude, Longitude", fontsize=12)
ax1.set_ylabel("Height (m)", fontsize=12)

#plot_cross_section(start, end, ax0)

plt.title(plot_title)
plt.savefig(plot_name)

print 'done'
