import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree


name = "/home/wrudisill/scratch/WRF_PROJECTS/wrf_cfsr_1996123000_1997010100/wrf_out/wrfout_d02_1996-12-30_00:00:00"


ds = xr.open_dataset(name)
times_strings = list(map(lambda x: x.decode('utf-8'), ds['Times'].values))
ds['Times'] = ('Time', pd.to_datetime(times_strings, format='%Y-%m-%d_%H:%M:%S'))
ds = ds.assign(Time=ds.Times).drop('Times')

lat = 43.5
lon = -116.0

# Use cKDTree to find indices of nearest grid cell
lonlat = np.column_stack((ds.XLONG[0].data.ravel(),ds.XLAT[0].data.ravel()))
tree = cKDTree(lonlat)
dist,idx = tree.query((lon,lat),k=1)
ind = np.column_stack(np.unravel_index(idx,ds.XLAT.data.shape))

# Print indices
print(ind)
j = ind[0][1]
k = ind[0][2]

# Print lat / lon of indices
print(ds.XLAT[0,j,k].data)
print(ds.XLONG[0,j,k].data)

print '-----SNOW-----' 

for i in range(len(ds.Time)):
    print ds.Time[i] ,ds.SNOW[i,j,k]
