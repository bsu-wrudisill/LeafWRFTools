from multinc import *
import sys
import glob 
#dirc="/home/wrudisill/scratch/WRF_PROJECTS/wrf_cfsr_1998-03-19_00__1998-03-27_00/wrf_out/{}"
#files="wrfout_d02_1998*"
#filelist = dirc.format(files)

# Gather files 
#
#
#
filepath = sys.argv[1]
ncname   = sys.argv[2]
#
#
# create filelist
filelist = "{}/wrfout_d02*".format(filepath)
print glob.glob(filelist)

ds = xr.open_mfdataset(filelist)
newds = xr.Dataset(data_vars=None, coords=ds.coords, attrs=ds.attrs) 
#
VerticalEnergyStorage(newds, ds, glob.glob(filelist))
FTOA(ds, newds)
FSFC(ds, newds)
FWALL(ds)
RainRate(ds, newds)
AddVar(inds,ods, "T2")
AddVar(inds,ods, "ACSNOM", rate=True)
AddVar(inds,ods, "GRDFLX", rate=True)

newds.to_netcdf(ncname)
