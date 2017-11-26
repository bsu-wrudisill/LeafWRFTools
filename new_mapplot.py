import numpy as np
import numpy.ma as ma
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib import ticker
from netCDF4 import Dataset
import sys,os
from mpl_toolkits.axes_grid1 import make_axes_locatable




def read(f,var,timestep):
  ds      = Dataset(f)
  var     = ds.variables[var][timestep, :, :]
  ds.close()
  return var

def colorbar(mappable):
    ax = mappable.axes
    fig = ax.figure
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    return fig.colorbar(mappable, cax=cax)


def make_plot(VAR):
	base ='/Volumes/PASSPORT/wrfout/THESIS_WRF_PROJECTS/1997_AR/'
	hi   = base+'subset_wrf_cfsr_1996-12-28_00__1997-01-08_00_INIT_1996-01-27_D01D02'
	low  = base+'subset_wrf_cfsr_1996-12-28_00__1997-01-08_00_INIT_1990-09-10_D01D02'
	name = '/precip_wrfout_d02_1997-01-07_00:00:00'

	# base='/Volumes/PASSPORT/wrfout/THESIS_WRF_PROJECTS/2010_AR/'
	# hi  = base+'subset_wrf_cfsr_2010-05-28_00__2010-06-10_00_INIT_1996-01-27_D01D02'
	# low = base+'subset_wrf_cfsr_2010-05-28_00__2010-06-10_00_INIT_1990-09-10_D01D02'
	# name = '/precip_wrfout_d02_2010-06-09_00:00:00'


	hisno  =  read(hi+name, 'FROZENNC', 0)[::-1,:]
	hirain =  read(hi+name, 'LIQUIDNC', 0)[::-1,:]
	lowsno  = read(low+name,'FROZENNC', 0)[::-1,:]
	lowrain = read(low+name,'LIQUIDNC', 0)[::-1,:]
	hi_tot  = hisno+hirain
	low_tot = lowsno+lowrain


	#-----PLOT CONTROLS -----#
	if VAR=='total':
		HIGH = hirain + hisno
		LOW  = lowrain + lowsno

	elif VAR =='snow':
		HIGH = hisno
		LOW  = lowsno

	elif VAR =='rain':
		HIGH = hirain
		LOW  = lowrain

	else:
		'print unknown option.'
		return
	#------------------------#
	diff = HIGH - LOW



	# ---------------- wrfinput snow fields --------------------- # 
	init1 = "/Volumes/PASSPORT/wrfout/wrfin/" + 'init_snow_1990_d02.nc'   #  LOW   #
 	init2 = "/Volumes/PASSPORT/wrfout/wrfin/" + 'init_snow_1996_d02.nc'   #  HIGH  # 
	# ---------------- wrfinput snow fields --------------------- # 


	init_lowsno =  ma.masked_equal(read(init1, 'SNOWC', 0), 0)[::-1,:] # read snow, mask out snow=0
	init_hisno  =  ma.masked_equal(read(init2, 'SNOWC', 0), 0)[::-1,:] # read snow, mask out snow=0

	fig, ax = plt.subplots(2,3)
	fig.set_size_inches(18, 12)


	im0 = ax[0,0].imshow(init_hisno, cmap='Reds', vmin=0, vmax=1.)
	colorbar(im0)

	im1 = ax[0,1].imshow(HIGH, cmap='Blues', vmax=225.)
	colorbar(im1)

	im2 = ax[1,0].imshow(init_lowsno, cmap='Reds', vmin=0, vmax=1.)
	colorbar(im2)   #not needed.

	im3 = ax[1,1].imshow(LOW, cmap='Blues', vmax=225.)
	colorbar(im3)

	# -- difference --# 
	#diff = hi_tot - low_tot
	im4  = ax[1,2].imshow(diff,cmap='seismic', vmin=-25., vmax=25.)
	colorbar(im4)

	ax[0,2].axis('off')


	# -- remove tick labels ---- # 
	for x in ax.flatten():
		x.set_xticklabels('')
		x.set_yticklabels('')



	# -- remove SAVE FIGURES---- # 
	plt.savefig('ar96_panel_plot_'+VAR+'.png', dpi=200)
#	plt.savefig('ar10_panel_plot_'+VAR+'.png', dpi=200)

	print 'saved: ar96_panel_plot_'+VAR+'.png'
#	print 'saved: ar10_panel_plot_'+VAR+'.png'




	### --------- colorbar only ---------------- ####

	# fig = plt.figure(figsize=(8, 3))
	# ax1 = fig.add_axes([0.05, 0.80, 0.9, 0.15])
	# ax2 = fig.add_axes([0.05, 0.475, 0.9, 0.15])
	# ax3 = fig.add_axes([0.05, 0.15, 0.9, 0.15])


	# cmap = mpl.cm.seismic
	# norm = mpl.colors.Normalize(vmin = -25. ,vmax=25.)
	# cb1 = mpl.colorbar.ColorbarBase(ax1, cmap=cmap, norm=norm, orientation='horizontal')
	# cb1.set_label('mm')


	# cmap = mpl.cm.Reds
	# norm = mpl.colors.Normalize(vmin=0. ,vmax=1.)
	# cb1 = mpl.colorbar.ColorbarBase(ax2, cmap=cmap, norm=norm, orientation='horizontal')
	# cb1.set_label('Snowcover Area Fraction')


	# cmap = mpl.cm.Blues
	# norm = mpl.colors.Normalize(vmin=0, vmax=200.)
	# cb1 = mpl.colorbar.ColorbarBase(ax3, cmap=cmap, norm=norm, orientation='horizontal')
	# cb1.set_label('mm')
	# #plt.savefig('ar10_panel_plot_snow_cbar.png', dpi=200)
	# plt.savefig('ar96_panel_plot_'+VAR+'_cbar.png', dpi=200)



# fig.colorbar(diff, ax=ax[1,2], fraction=0.06, pad=0.01)

