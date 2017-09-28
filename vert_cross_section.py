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


filenameA="/home/wrudisill/scratch/WRF_PROJECTS/INIT/wrf_cfsr_1996123000_1997010100_INIT_2003-11-20/wrf_out/wrfout_d02_1996-12-31_00:00:00"

filenameB="/home/wrudisill/scratch/WRF_PROJECTS/INIT/wrf_cfsr_1996123000_1997010100_INIT_1996-01-27/wrf_out/wrfout_d02_1996-12-31_00:00:00"

start = (45.0, -115.85)
end   = (42.8, -115.78)




#var = "uvmet_wspd_wdir"
var = 'temp'
plot_title= 'temp (K)'
plot_name= 'temp_vertcross_1996-01-27'

def vert_cross_section(filename, var,time):

    ncfile = Dataset(filename)

    # Extract the model height and wind speed
    z = getvar(ncfile, "z")
    

    #wspd =  getvar(ncfile, "uvmet_wspd_wdir", units="kt")[0,:]
    field =  getvar(ncfile, var)
    # Create the start point and end point for the cross section

    start_point = CoordPair(lat= start[0], lon= start[1]) # Cascade
    end_point   = CoordPair(lat= end[0],  lon= end[1])

    # Compute the vertical cross-section interpolation.  Also, include the lat/lon
    # points along the cross-section.
    field_cross = vertcross(field, z, wrfin=ncfile, start_point=start_point, end_point=end_point,
                            latlon=True,meta=True,timeidx=time)
    return field_cross


A = vert_cross_section(filenameB, var, 20) 
a = to_np(A)

#B = vert_cross_section(filenameB, var, 20) 
#b = to_np(B)




#diff_array = to_np(B) - to_np(A)
#diff_array = a - b

# Create the figure
#fig,(ax0,ax1) = plt.subplots(1,2)
fig,ax1 = plt.subplots(1,1)

# Make the contour plot
#levels = np.linspace(diff_array.min(), diff_array.max(), 50)
levels = np.linspace(a.min(), a.max(), 50)
#print diff_array.min()

#wspd_contours = ax.contourf(to_np(wspd_cross), cmap=get_cmap("jet"), levels=levels)
contours = ax1.contourf(a, cmap=get_cmap("jet"), levels=levels)

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
