from MultiNC import *

sample_wrf_file = "/home/wrudisill/scratch/WRF_PROJECTS/wrf_cfsr_1998-02-01_00__1998-03-03_00/wrf_out/wrfout_d02_1998-03-01_00:00:00"

ds = xr.open_mfdataset("../Data/AR96_NoSpinUp.nc")
t1 = ds['FWALL'][0:75,:,:].sum(axis=0)/(75*60*60)
t1.to_netcdf("fwall.tmp")
NCL(FNAME="fwall.tmp", VARNAME="FWALL", WRF_EXAMPLE_FILE=sample_wrf_file, PLOTTITLE="no_spin", UNITS="W/m2")
