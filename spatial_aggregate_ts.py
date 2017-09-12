import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from netCDF4 import Dataset
import sys,os
from multiprocessing import Pool, cpu_count
import time 
import pandas as pd 
import matplotlib.dates as mdates
import glob




#A = ['/home/wrudisill/scratch/WRF_PROJECTS/wrf_cfsr_1996123000_1997010100/wrf_out/wrfout_d02_1996-12-30_00:00:00']
A = ['/home/wrudisill/scratch/WRF_PROJECTS/wrf_cfsr_1996123000_1997010100_INIT_2005-12-30/wrf_out/wrfout_d02_1996-12-30_00:00:00']
B = ['/home/wrudisill/scratch/WRF_PROJECTS/wrf_cfsr_1996123000_1997010100_INIT_1996-12-31/wrf_out/wrfout_d02_1996-12-30_00:00:00']
C = ['/home/wrudisill/scratch/WRF_PROJECTS/wrf_cfsr_1996123000_1997010100_INIT_2003-11-20/wrf_out/wrfout_d02_1996-12-30_00:00:00'] 
D = ['/home/wrudisill/scratch/WRF_PROJECTS/wrf_cfsr_1996123000_1997010100_INIT_2015-12-30/wrf_out/wrfout_d02_1996-12-30_00:00:00'] 
E = ['/home/wrudisill/scratch/WRF_PROJECTS/wrf_cfsr_1996123000_1997010100_INIT_2016-03-14/wrf_out/wrfout_d02_1996-12-30_00:00:00'] 


class init_compare:
    # Spatially aggregates wrfout files using a provided statistic
    # Plotting gets passed off to elsewhere


    def __init__(self, filelist, var):
        self.fx = np.mean
        self.df = pd.DataFrame()        
        self.filelist = filelist
        # loops through the filelist we input
        map(self.aggregate_stats, filelist)

    def time_format(self, ts):
        times_tmp = reduce(lambda x,y: x+y, ts)
        return pd.to_datetime(times_tmp, format='%Y-%m-%d_%H:%M:%S')

    def aggregate_spatial(self, filename):
        print filename
        ds            = Dataset(filename)
        var           = ds.variables[self.var]
        raw_times     = ds.variables['Times'][:]
        times         = map(self.time_format, raw_times)
        mean_list     = np.asarray(map(lambda X: self.fx(var[X, :, :]), range(len(times))))
        df            = pd.DataFrame(index = times, data=mean_list, columns= [var+'_Mean'])
        self.df       = self.df.append(df)
        ds.close()
    
    def ratio(self,var1,var2):
        var_old = self.var
        self.var = var1
        map(self.aggregate_spatial, self.filelist)
        self.var = var2
        map(self.aggregate_spatial, self.filelist)
        self.var = var_old

    def __call__(self):
        return self.df



# Plotting 

fig = plt.figure()
fig.subplots_adjust(bottom=0.2)
ax  = fig.gca()
a = init_compare(A)
b = init_compare(B)
c = init_compare(C)
d = init_compare(D)
e = init_compare(E)



ax.plot(a.df.index, a.df.Mean, label = 'Base')
ax.plot(b.df.index, b.df.Mean, label = '1996-12-31')
ax.plot(c.df.index, c.df.Mean, label = '2003-11-20')
ax.plot(d.df.index, d.df.Mean, label = '2015-12-30')
ax.plot(e.df.index, e.df.Mean, label = '2016-03-14')

xtick_formatter = mdates.DateFormatter('%d_%H:00')
ax.xaxis.set_major_formatter(xtick_formatter)
plt.title('d02 Mean T2')
plt.xticks(rotation=45)
plt.legend()
plt.savefig('foo.png')
plt.clf()
del fig

print 'done'



