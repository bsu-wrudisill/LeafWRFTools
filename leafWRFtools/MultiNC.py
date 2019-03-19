# stuff here
import numpy as np
import datetime
from netCDF4 import Dataset
import xarray as xr
import glob
#from matplotlib import pyplot as plt 
from netCDF4 import Dataset     
from multiprocessing import Pool
import subprocess
import SystemFX as sfx

"""
Classes 

"""
class WRFVIZ:
    # functions to create visualizations of WRF out data 

    def __init__():
        pass

    def callNCL():
        # 
        pass       

class Regridding:
    # functions to regrid WRF variables vs. well known datasets 
    #  
    def __init__():
        pass

class SnotelCompare:
    def __init__():
        pass


class WRFOUT():
    # wrapper for a variety of functions
    filelist = [None]
    sample_wrf_file = filelist[0]  # used to make NCL plots, sometimes 

    def __init__(filelist): 
        #  
        if type(filelist)==str:
            # list of files 
            filelist=glob.glob(filelist)
            self.filelist = filelist 
            self.sample_wrf_file = filelist[0]
            
            # open the dataset 
            ds = xr.open_mfdataset(filelist)
            # create a new dataset 
            newds = xr.Dataset(data_vars=None, coords=ds.coords, attrs=ds.attrs) 

"""
Decorators 
"""




"""
Functions 
"""

def NCL(**kwargs):
    # Create Nice looking WRFout plots using the NCL plotting library 
    # literally creates an NCL script with the right parameters 
    # and executes by making a system command 

    dic = {"FNAME":None,
           "VARNAME":"NoQuotes",
           "WRF_EXAMPLE_FILE":None,
           "PLOTTITLE":None,
           "UNITS":None}
    
    for key in kwargs.keys():
        if key in dic.keys():
            if dic[key] == "NoQuotes":
                # do not add quotes 
                insert = kwargs[key]
            else:
                # add quotes 
                insert = "\"{}\"".format(kwargs[key])
            dic.update({key: insert})
    
    script="./templates/ncl_wrfmap_template.ncl"
    sfc.GenericWrite(script, dic, "./ncl_wrfmap.ncl")
    print(dic)
    # execute the plot command 
    cmd = "ncl ./ncl_wrfmap.ncl"
    out, err = sfx.system_cmd(cmd)
    print(out)
   

def MultiNC(datapath, variable, *args, **kwargs):
    # get kwargs 
    region    = kwargs.get('region', None)
    function  = kwargs.get('fx', None)    
    nodes     = kwargs.get('nodes',1)
    print(region, function, nodes)

def PrecipAnalyze():
    pass 


def __takeSecond(elem):
    # used to sort a list of tuples by the second tuple member
    return elem[1]


def ApplyWrfPyParallel(fx, datalist):
    # fx requires (file, key) to work
     
    # parse the datalist
    if type(datalist) == str:
        datalist = glob.glob(datalist) 
    from multiprocessing import Pool, cpu_count
    ncpu = cpu_count()
    print("Starting ApplyWrfPyParallel. Using {} cores".format(ncpu))
    
    p = Pool(ncpu)
    keys = range(len(datalist))
    datatuple = zip(datalist,keys)
    out=p.map(fx,datatuple)
    out.sort(key = __takeSecond)
    ConcatVar = np.concatenate([arr for arr,index in out], axis=0)
    return ConcatVar    


def VerticalEnergyStorage(outds, inds, datalist):
    # apply the _vestore function w/ apply wrf parallel
    # to calculate tropospheric energy storage and 
    # storage flux 
    
    # create new variables in file 
    outds["Estore"] = (['time','xlat','xlon'],  np.zeros_like(inds['RAINNC'])) 
    outds["dEdt"]   = (['time','xlat','xlon'],  np.zeros_like(inds['RAINNC'])) 
    
    estore = ApplyWrfPyParallel(__vestore, datalist)
    np.save('tmp_raw.npy', estore) 
    # assign values to dedt 
    outds["Estore"][:,:,:] = np.load("tmp_raw.npy")
    outds["dEdt"][1:,:,:] = calculate_rate(outds, "Estore")
    # don 


def __vestore(datalist, **kwargs):
    # Since we are using wrf-python functions, we can't use
    # all of the nice features of xarray/dask

    # import necessary modules 
    from wrf import getvar,vinterp
    from multiprocessing import pool 
    # datatuple is filenpath, index
    dataname, key = datalist  
    # vertical energy integration 
    # create a new xarray dataset to store the data  
    dataset = Dataset(dataname)
    # assume that RAINNC is in there 
    outarray = np.zeros_like(dataset['RAINNC'])
    times, xlat, xlon = outarray.shape  
    cp = 1005.7   #J k-1
    lv = 2.5e6    #J kg-1
    g = 9.81 

    def looper(time):
        # Get variables 
        gp = getvar(dataset, "geopotential", timeidx=time)
        T  = getvar(dataset, "tk", timeidx=time)
        Q  = getvar(dataset, "QVAPOR", timeidx=time)
        pres  = getvar(dataset, "pressure", timeidx=time)
        press_diff = np.zeros_like(pres)
        press_diff[1:,:,:] = np.diff(pres, axis=0)
        # Energy Storage 
        Estore = -1./g*(cp*T + lv*Q + gp)*press_diff   # sum on mass grid (eta levels)        
        # Energy storage integral
        Estore_integral = np.trapz(Estore, axis=0)
        # create outout     
        outarray[time,:,:] = Estore_integral
    map(looper,range(times))
    return [outarray,key]


def RainRate(inds,ods,**kwargs):
    # "In" dataset and "Out" dataset
    ods["PTOTAL"] = inds['RAINNC']+inds['I_RAINNC']*100.0
    # calculate rain rate  
    ods["PRATE"]  = (['time','xlat','xlon'],  np.zeros_like(inds['RAINNC']))
    ods["PRATE"][1:,:,:] = ods["PTOTAL"][1:,:,:] - ods["PTOTAL"][0:-1, :,:]
    # calculate snow rate 
    ods["SNOWRATE"]  = (['time','xlat','xlon'],  np.zeros_like(inds['RAINNC']))
    ods["SNOWRATE"][1:,:,:] = inds["SNOWNC"][1:,:,:] - inds["SNOWNC"][0:-1, :,:]
    print("Wrote PRATE, SNOWRATE")
    return      

def bucket_varname(string):
    bucket = "I_{}".format(string)
    return bucket

def calculate_rate(dataset, var, **kwargs):
    # calculate rate/timestep for accumulated variables
    # assumes array is  [time, x,y]
    bucket_value = kwargs.get("bucket_value", 1.0e9)
    bucket = kwargs.get("bucket",False)
    zeros= np.zeros_like(dataset[var][:,:,:])    
    if bucket==True:
        var_correct = dataset[var]+dataset[bucket_varname(var)]*bucket_value
        print('correcting')
    else:
        var_correct = dataset[var]
    copy = var_correct[1:,:,:] - var_correct[0:-1,:,:]
    return copy


def FSFC(inds,ods,**kwargs):
    # create variables before hand to fill in 
    for i in ["SH","LH", "SW_sfc", "LW_sfc", "SRAD", "FSFC"]:
        ods[i]  = (['time','xlat','xlon'],  np.zeros_like(inds['RAINNC']))
    
    ods["SH"][1:,:,:] = calculate_rate(inds,"ACHFX")
    ods["LH"][1:,:,:] = calculate_rate(inds,"ACLHF")

    swupb = calculate_rate(inds,"ACSWUPB",bucket=True)
    swdnb = calculate_rate(inds,"ACSWDNB",bucket=True)
    
    lwupb = calculate_rate(inds,"ACLWUPB",bucket=True)
    lwdnb = calculate_rate(inds,"ACLWDNB",bucket=True)
    # assign vars 
    ods["SW_sfc"][1:,:,:] = swupb - swdnb
    ods["LW_sfc"][1:,:,:] = lwupb - lwdnb
    ods["SRAD"] = ods["SW_sfc"] + ods["LW_sfc"]
    ods["FSFC"] = ods["SW_sfc"] + ods["LW_sfc"] + ods["SH"] + ods["LH"]
    print("wrote FSFC")
    # assig
    return      

def FTOA(inds,ods,**kwargs):
    # create variables to fill in w/ data 
    for i in ["SW_toa", "LW_toa", "FTOA"]:
        ods[i]  = (['time','xlat','xlon'],  np.zeros_like(inds['RAINNC']))
    # shortwave
    swdnt = calculate_rate(inds,"ACSWDNT",bucket=True)
    swupt = calculate_rate(inds,"ACSWUPT",bucket=True)
    ods["SW_toa"][1:,:,:] = swdnt - swupt
    # longwave 
    lwdnt = calculate_rate(inds,"ACLWDNT",bucket=True)
    lwupt = calculate_rate(inds,"ACLWUPT",bucket=True)
    ods["LW_toa"][1:,:,:] = lwdnt - lwupt
    # top of atmosphere
    ods["FTOA"] = ods["SW_toa"] + ods["LW_toa"]
    print("wrote FTOA")
    return 

def FWALL(ods,**kwargs):
    ods["FWALL"]  = (['time','xlat','xlon'],  np.zeros_like(ods['FSFC']))
    ods["FWALL"]  = ods["dEdt"] - ods["FTOA"] - ods["FSFC"]

def NanToZero(array):
    array[np.where(array == np.nan)] = 0
    return array 

def AddVar(inds,ods,var, **kwargs):
    rate = kwargs.get("rate",False)
    if rate == False:
        # simply take a var from the 'input dataset' and place it in the 'output' dataset  
        ods[var]  = (['time','xlat','xlon'],  np.zeros_like(inds[var]))
        ods[var] = inds[var]
    
    elif rate == True: 
        varr = "{}_rate".format(var)
        ods[varr]  = (['time','xlat','xlon'],  np.zeros_like(inds[var]))
        print('calculate rate')
        ods[varr][1:,:,:] = calculate_rate(inds, var)
        
def HRLDAS_to_RESTART(hrldas, wrfrestart, dictionary):
    # 
    hrldas_ds = Dataset(hrldas)
    wrfrestart_ds = Dataset(wrfrestart)
    
    for key in dictionary.keys():
        replace = hrldas_ds[key].values()

    

    
if __name__ == "__main__":
    dirc="/home/wrudisill/scratch/WRF_PROJECTS/wrf_cfsr_1998-03-19_00__1998-03-27_00/wrf_out/{}"
    files="wrfout_d02_1998*"
    filelist = dirc.format(files)
    inds = xr.open_mfdataset(filelist)
    print(inds["SNOWNC"])



