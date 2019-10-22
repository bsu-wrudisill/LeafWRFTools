import numpy as np
import numpy.ma as ma
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib import ticker
from netCDF4 import Dataset
import sys,os
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.axes_grid1 import ImageGrid



def read(f,var,timestep):
  ds      = Dataset(f)
  var     = ds.variables[var][timestep, :, :]
  ds.close()
  return var

def colorbar(mappable):
	try:
		ax = mappable.axes
	except AttributeError:
		ax = mappable.ax

	fig     = ax.figure
	divider = make_axes_locatable(ax)
	cax     = divider.append_axes("bottom", size="5%", pad=0.01)
	#	cax = divider.new_vl(size="5%", pad =0.7)
	return fig.colorbar(mappable, cax=cax, orientation="horizontal")




def add_colorbar(mappable, **kwargs):
	# create a horizontal colorbar on a new axis underneath a plot

	try:
		ax = mappable.axes
	except AttributeError:
		ax = mappable.ax


	flag = kwargs.get('flag', 'horizontal')  # default behavior is a horiz. cbar

	fig = ax.figure
	box = ax.get_position()

	if flag == 'horizontal':
		ax.set_position([box.x0, box.y0, box.width, box.height*1.1])
		axcolor = plt.axes([box.x0+.1, box.y0, box.width, box.height*.1])
		return fig.colorbar(mappable, cax=axcolor, orientation="horizontal")

	if flag == 'vertical':
		ax.set_position([box.x0, box.y0, box.width*1.1, box.height])	
		axcolor = plt.axes([box.x0, box.y0, box.width*.1, box.height])
		return fig.colorbar(mappable, cax=axcolor, orientation="vertical")



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


	im0 = ax[0,0].contourf(init_hisno, cmap='Reds', levels= [0, .25, .5, .75,  1.])
#	colorbar(im0)

	im1 = ax[0,1].contourf(HIGH, cmap='Blues', levels = np.arange(0, 300., 50.))
	#colorbar(im1)

	im2 = ax[1,0].contourf(init_lowsno, cmap='Reds', levels= [0, .25, .5, .75,  1.])
	colorbar(im2)#, flag='vertical')   #not needed.

	im3 = ax[1,1].contourf(LOW, cmap='Blues', levels = np.arange(0, 300., 50.))
	colorbar(im3)

	# -- difference --# 
	#diff = hi_tot - low_tot
	im4  = ax[1,2].contourf(diff,cmap='seismic', levels = np.arange(-50., 60., 10.))
	colorbar(im4)
	ax[0,2].axis('off')


	# -- remove tick labels ---- # 
	for x in ax.flatten():
		x.set_xticklabels('')
		x.set_yticklabels('')

	# -- remove SAVE FIGURES---- # 
	plt.savefig('../ar96_panel_plot_'+VAR+'.png', dpi=200)
#	plt.savefig('ar10_panel_plot_'+VAR+'.png', dpi=200)
	print 'saved: ar96_panel_plot_'+VAR+'.png'
#	print 'saved: ar10_panel_plot_'+VAR+'.png'



def master_plot():
	# base ='/Volumes/PASSPORT/wrfout/THESIS_WRF_PROJECTS/1997_AR/'
	# hi   = base+'subset_wrf_cfsr_1996-12-28_00__1997-01-08_00_INIT_1996-01-27_D01D02'
	# low  = base+'subset_wrf_cfsr_1996-12-28_00__1997-01-08_00_INIT_1990-09-10_D01D02'
	# name = '/precip_wrfout_d02_1997-01-07_00:00:00'

	base='/Volumes/PASSPORT/wrfout/THESIS_WRF_PROJECTS/2010_AR/'
	hi  = base+'subset_wrf_cfsr_2010-05-28_00__2010-06-10_00_INIT_1996-01-27_D01D02'
	low = base+'subset_wrf_cfsr_2010-05-28_00__2010-06-10_00_INIT_1990-09-10_D01D02'
	name = '/precip_wrfout_d02_2010-06-09_00:00:00'



	hisno  =  read(hi+name, 'FROZENNC', 0)#[::-1,:]
	hirain =  read(hi+name, 'LIQUIDNC', 0)#[::-1,:]
	lowsno  = read(low+name,'FROZENNC', 0)#[::-1,:]
	lowrain = read(low+name,'LIQUIDNC', 0)#[::-1,:]
	hitot  = hisno+hirain
	lowtot = lowsno+lowrain


	# Difference maps 
	diff_sno  = hisno  - lowsno
	diff_rain = hirain - lowrain 
	diff_tot  = hitot  - lowtot


	# ---------------- wrfinput snow fields --------------------- # 
	init1 = "/Volumes/PASSPORT/wrfout/wrfin/" + 'init_snow_1990_d02.nc'   #  LOW   #
 	init2 = "/Volumes/PASSPORT/wrfout/wrfin/" + 'init_snow_1996_d02.nc'   #  HIGH  # 
	# ---------------- wrfinput snow fields --------------------- # 


	init_lowsno =  ma.masked_equal(read(init1, 'SNOWC', 0), 0)#[::-1,:] # read snow, mask out snow=0
	init_hisno  =  ma.masked_equal(read(init2, 'SNOWC', 0), 0)#[::-1,:] # read snow, mask out snow=0

	fig, ax = plt.subplots(3,5)
	fig.set_size_inches(30,18)


	#initial snowpack conditions
	im0 = ax[0,0].contourf(init_hisno, cmap='Reds', levels= [0, .25, .5, .75,  1.])
	im1 = ax[1,0].contourf(init_lowsno, cmap='Reds', levels= [0, .25, .5, .75,  1.])
	ax[2,0].axis('off')

	#snow 
	im2 = ax[0,1].contourf(hisno, cmap='Blues', levels = np.arange(0, 300., 50.))
	im3 = ax[1,1].contourf(lowsno, cmap='Blues', levels = np.arange(0, 300., 50.))
	im4 = ax[2,1].contourf(diff_sno,cmap='seismic', levels = np.arange(-50., 60., 10.))
	
	#rain
	im5 = ax[0,2].contourf(hirain, cmap='Blues', levels = np.arange(0, 300., 50.))
	im6 = ax[1,2].contourf(lowrain, cmap='Blues', levels = np.arange(0, 300., 50.))
	im7 = ax[2,2].contourf(diff_rain,cmap='seismic', levels = np.arange(-50., 60., 10.))

	#total
	im8   = ax[0,3].contourf(hitot, cmap='Blues', levels = np.arange(0, 300., 50.))
	im9   = ax[1,3].contourf(lowtot, cmap='Blues', levels = np.arange(0, 300., 50.))
	im10  = ax[2,3].contourf(diff_tot,cmap='seismic', levels = np.arange(-50., 60., 10.))

	# # Cbars
	# box = ax[2,0].get_position()
	# ax[2,0].set_position([box.x0, box.y0+box.height*.95, box.width, .01])		
	# fig.colorbar(im0, cax=ax[2,0], orientation="horizontal")


	for i in range(3):
		box = ax[i,4].get_position()
		ax[i,4].set_position([box.x0, box.y0, .01, box.height])
	fig.colorbar(im2, cax=ax[0,4], orientation="vertical")
	fig.colorbar(im2, cax=ax[1,4], orientation="vertical")
	fig.colorbar(im10, cax=ax[2,4], orientation="vertical")


	# -- remove tick labels ---- # 
#	for x in ax.flatten():
	for j in range(3):
		for k in range(4):
			x = ax[j,k]
			x.set_xticklabels('')
			x.set_yticklabels('')


	# -- remove SAVE FIGURES---- # 
	plt.savefig('../ar10_panel_plot_master.png', dpi=800)

#	plt.savefig('ar10_panel_plot_'+VAR+'.png', dpi=200)
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

