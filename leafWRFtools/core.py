'''
Functions/Classes containing the 'core' module functionality 
'''

import xarray as xr
import pandas as pd
import pathlib 
import xesmf

def RegridData():
	# WRF variable --> Destination grid 
	# Checks/Warnings:
	# - Destination grid lat/lon grid is within the WRF XLAT/XLONG grid 
	# Returns:
	# - xarray data object (DataArray or Dataset)
	# Considerations  
	# - Does this function operate on an entire file?
	# - Does it operate on one variable at a time?
	pass	

def AggregateTemporal():
	# Description
	# Xarray Dataset With Timestep K --> Xarray Dataset with Timestep K* 
	# K* can either be upsampled (hourly to daily  or downsampled)
	# Checks/Warnings:
	# 
	# Returns:
	# - xarray data object w/ new timestep 
	pass 	

def SubsetVariables():
	pass

def SubsetSpatial():
	# 
	pass
	


def WriteWRFHydro():
	# wrapper function around the variable subset script
	pass
