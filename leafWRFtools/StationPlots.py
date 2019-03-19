from MultiNC import *
from matplotlib import pyplot as plt

# deadwood summit 
coords = (44.54,-115.56)

filelist="../Data/1998_spinup.nc"
inds = xr.open_mfdataset(filelist)

# point to plot 
xlat, xlon = 200,200

def Anomaly(array):
    pass

# create a plot 
def FourPanel():
    colors = ['red','blue','green','purple']
    varlist = ["dEdt", "Fwall", "FSFC", "FTOA"]
    fig,ax= plt.subplots(len(varlist),1)

    for varb,p in zip(varlist,range(len(varlist))):
        wm2 = inds[varb][:,xlat,xlon]/(60.*60.)
        anom = (wm2 - wm2.mean())/wm2.std()

        ax[p].plot(anom, label=varb,color=colors[p])
    #    ax[p].legend()
#        ax[p].set_ylim(-500,500)
        ax[p].set_ylabel(varb)
    
    plt.savefig("Lineplot100100", dpi=600)


#fig,ax= plt.subplots()
#ax.plot(inds['Estore'][:,xlat,xlon], label='Estore')
##ax.legend()
#plt.savefig('Estore')

FourPanel()
