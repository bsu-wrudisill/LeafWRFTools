import pandas as pd
import xarray as xr
import xesmf as xe
import argparse
import glob 
import datetime
import sys 
import numpy as np


# Input Arguments 
#daymet_file = sys.argv[1]       # full filepath to the DAYMET 
#output_dir  = kwargs.get(sys.argv[3], './')

# target grid 
for var in ["vp", "tmin", "tmax"]:
	for daymet_file in glob.glob("./TMP_DayMetFiles/{}/*.nc4".format(var)):
		print("working on ..."+daymet_file)
		name_only = daymet_file.split("/")[-1]
		ds_target = xr.open_dataset('sample_wrf_file.nc')
		ds_target.rename({'XLONG': 'lon', 'XLAT': 'lat'}, inplace=True)
		ds_target['lat'] = ds_target['lat'][0,:,:]
		ds_target['lon'] = ds_target['lon'][0,:,:]

		# loop through wrfout file list 
		ds = xr.open_dataset(daymet_file)

		# create the regridding weight file 
		regridder = xe.Regridder(ds, ds_target, 'bilinear', reuse_weights=True)

		# create a new output file 
		newds = xr.Dataset(data_vars=None, attrs=ds.attrs)
		new_ds_var_shape = ds['time'].shape[0], ds_target['lat'].shape[0],  ds_target['lat'].shape[1]

		# create a precip variable of the correct dimensions 
		newds[var] = (['Time', 'south_north','west_east'], np.zeros(new_ds_var_shape))     

		# divide up regridding to avoid memory problems 
		chunksize=10
		chunklist = np.arange(0,364,chunksize)
		chunklist[-1] = 364 # this way the last "chunk" ends on the final index

		# create a list of tuples (start_index,end_index)
		zip_list = [z for z in zip(chunklist[:-1], chunklist[1:])]

		def RegridAssignToArray(tpl):
		    start = tpl[0]
		    end   = tpl[1]
		    var_regrid = regridder(ds[var][start:end, :, :])
		    newds[var][start:end,:,:] = var_regrid 
			

		# get the number of processors 
		#nproc = mp.cpu_count()     

		# do some simple parallel stuff 
		for z in zip_list:
		    RegridAssignToArray(z)
		    print(z)
		print('write netcdf...')
		newds.to_netcdf("ID_Regridded/{}Regridded_{}".format(var, name_only))

# loop thru varlist and regrid variables; assign these to the newds
#var_regrid = regridder(ds['prcp'])
#newds[var] = (['Time', 'south_north','west_east'], np.zeros_like(var_regrid))     
#newds[var] = var_regrid 
#print('done with...{}'.format(var))

#newds.to_netcdf("TEST")

