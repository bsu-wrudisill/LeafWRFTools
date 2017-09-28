#!/bin/bash



base=/home/wrudisill/scratch/WRF_PROJECTS/INIT/
#hires=/home/wrudisill/scratch/WRF_PROJECTS/wrf_cfsr_1996123000_1997010100_HiRes/wrf_out

#base=/home/wrudisill/scratch/WRF_PROJECTS/INIT/wrf_cfsr_1996123000_1997010100_INIT_1996-12-31/wrf_out
#base1=/home/wrudisill/scratch/WRF_PROJECTS/INIT/wrf_cfsr_1996123000_1997010100_INIT_2003-11-20/wrf_out

#base has MORE snow than base1

#diff_dir=/home/wrudisill/scratch/WRF_PROJECTS/diff_dir
#varlist=T


#hgt='/home/wrudisill/scratch/WRF_SIM_CFSR_1996-12-28_00__1997-01-08_00/wps_cfsr_1996122800_1997010800/met_em.d02.1997-01-07_09:00:00.nc'

#for i in $(ls $base/wrfout_d02*); do 
#   OUTNAME=$(echo $i | awk -F '[/]' '{print $8}')
#   #ncks -v SNOW,RAINNC,SNOWNC,SR $base/$OUTNAME -o $diff_dir/$OUTNAME\_A
#   ncks -v $varlist $base/$OUTNAME -o $diff_dir/$OUTNAME\_A
#   ncks -v $varlist $base1/$OUTNAME -o $diff_dir/$OUTNAME\_B
#   ncdiff $diff_dir/$OUTNAME\_A $diff_dir/$OUTNAME\_B $diff_dir/$OUTNAME\_diff   

   #append lat lon to the ncdiff file
#   ncks -A -v XLAT,XLONG $base/$OUTNAME $diff_dir/$OUTNAME\_diff   
#   # appeng height 
#   ncks -A -v GHT $hgt $diff_dir/$OUTNAME\_diff   


#   rm $diff_dir/*_A*
#   rm $diff_dir/*_B*

#done 


ncdiff $base/wrf_cfsr_1996123000_1997010100_INIT_1996-01-27/wrf_out/wrfout_d02_1996-12-31_00:00:00 $base/wrf_cfsr_1996123000_1997010100_INIT_2003-11-20/wrf_out/wrfout_d02_1996-12-31_00:00:00 -o foo.nc







