#!/bin/bash

# A function to ncview any date from Katelyn's 30 year run


function ncdt() 
{
module load nco
# $1 is the date in format YYYY-MM-DD
# $2 is the domain
INIT_FILE=$(find /mnt/wrf_history/*/wrf_out/*/$2/ -name wrfout_$2_$1*)
ncview $INIT_FILE
}

