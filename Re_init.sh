#!/bin/bash

#------------------------------------
#    USAGE: This script modifies WRF input files and re-runs wrf.exe
#           It depends on having an already completed WRF run executed by 
#           ./WPS_WRF_Run_R2.sh. This script does not run Real.exe again. 
#                   
#
#
#------------------------------------

#------------------------------------
# USER INPUT
#------------------------------------

y1=$1
m1=$2
d1=$3
h1=$4
y2=$5
m2=$6
d2=$7
h2=$8
INIT_DATE=$9         #Date of format YYYY-MM-DD
INIT_NAME=${10}      #Name for the run. gets appened to folder name. Can be Left Blank

INIT_NAME=${INIT_DATE}_$INIT_NAME

d02_INIT_FILE=$(find /mnt/wrf_history/*/wrf_out/*/d02/ -name wrfout_d02_$INIT_DATE*)
d01_INIT_FILE="${d02_INIT_FILE//d02/d01}"  # replaces the d02 with d02 in the filename


#------------------------------------
# FILES AND DIRECTORIES
#------------------------------------
BASE_DIR=/home/wrudisill/scratch/WRF_SIM_CFSR_${y1}-${m1}-${d1}_${h1}__${y2}-${m2}-${d2}_${h2}
WRF_DIR=/$BASE_DIR/wrf_cfsr_${y1}${m1}${d1}${h1}_${y2}${m2}${d2}${h2}  
PROJ_DIR=/home/wrudisill/scratch/WRF_PROJECTS/wrf_cfsr_${y1}-${m1}-${d1}_${h1}__${y2}-${m2}-${d2}_${h2}                        
FUNCS=/home/wrudisill/WRF-R2/funcs/std_funcs.sh    #The directory containing matt's wrf run funcs scripts
TRASHLIST=''



#------------------------------------
#  Options
#------------------------------------
VARLIST=SNOW,SNOWH,SNOWC

#------------------------------------
# FUNCTIONS
#------------------------------------


function clean()
# Clean up directories. USE WITH CAUTION
{ 
echo -e "================================="
echo -e ""
echo -e "Something went awry :( \n" 
echo -e ""
echo -e "Removing directories: \n"
echo -e "$TRASHLIST \n"
echo -e ""
echo -e "================================="

rm -rf $TRASHLIST
}




function filecheck()

# Check That Files Exist 

{
    if [ -e $1 ]
    then
	echo -e "found" $1  # THE problem here is that if $1 is totally blank that is True
    else
	echo -e "not found" $1
	clean
	exit 2 
    fi
}



function datediff() {
    
# Calculate time difference between two dates  
    local d1=$(date -d "$1" +%s)
    local d2=$(date -d "$2" +%s)
    run_days=$(( (d2 - d1) / 86400))   # These are global
    run_hours=$(( (d2 - d1) / 3600))   # These are global; exist outside of fx
}



function Re_Init()

# Insert specified wrf vars from 1 file to another
o
{
    # $1 : The high res file to stick in the wrfinput file
    # $2 : The wrfinput file to be updated
    ncks -A -v $VARLIST -d Time,1 $1 $2 
    local status=$?

    if [ "$status" != 0 ]; then
	echo -e "\n ncks failed; check yourself\n"
	echo -e "Exiting.\n\n"
	clean
	exit 2
    else
	echo -e "----------------------"
	echo -e " Sub'd variables: $VARLIST  \n"
	echo -e "-----------------------"
	echo -e " from $1 \n"
	echo -e " into $2 \n"
    fi

}



#------------------------------------------------------------
        #----------------  MAIN -----------------# 
#------------------------------------------------------------
exec >> wrf_${y1}${m1}${d1}${h1}_${y2}${m2}${d2}${h2}_INIT_$INIT_NAME.log 
exec 2>&1 

sleep 2

echo -e "                                                       "
echo -e "                                                       "
echo -e "#######################################################"
echo -e "                                                       "
echo -e " Starting Re-Initialization Run for:                   "
echo -e "                                                       "
echo -e "     WRF Run:  ${WRF_DIR}                              "
echo -e "                                                       "
echo -e "     Initializing Variables:  ${VARLIST}               "
echo -e "                                                       "
echo -e "     from Files:  ${d02_INIT_FILE}, ${d01_INIT_FILE}   "
echo -e "                                                       "
echo -e "#######################################################"

sleep 20

# Source std_funcs.sh
source $FUNCS

# Create a copy of the WRF_DIR to house the new simulation; Maybe later we want to delete this; 

echo -e "####### Checking that paths and files make sense ##########"
echo -e " "

filecheck $BASE_DIR
filecheck $PROJ_DIR
filecheck $WRF_DIR
filecheck $d01_INIT_FILE
filecheck $d02_INIT_FILE


echo -e "####### Create directories ##########"
echo -e " "
echo -e "creating a copy of $WRF_DIR..."

WRF_DIR_COPY=$WRF_DIR\_INIT_$INIT_NAME
TRASHLIST="$TRASHLIST $WRF_DIR_COPY"

echo -e "rsyncing..... /n"
#copy files, exclude previous wrfout files from copying
rsync -a --exclude 'wrfinput*' --exclude 'wrfbdy*' --exclude 'wrfout*' --exclude 'wrfxtrm*' --exclude 'wrfrst*' $WRF_DIR/ $WRF_DIR_COPY  # removed verbose (-v) flag
echo -e "created $WRF_DIR_COPY /n"

# Create RUN_DIR variable path for the run directory within the new WRF_DIR copy
RUN_DIR=$WRF_DIR_COPY/run



echo -e "####### Create namelist files ##########"
echo -e " "

# Copy namelist.input_YYYY-MM-DD_HH to the RUN_DIR (The namelist.input gets removed from the directory for whatever readson)
namelist_file=$BASE_DIR/WRF-R2_${y1}${m1}${d1}${h1}_${y2}${m2}${d2}${h2}/namelists/namelist.input.template
filecheck $namelist_file

echo -e "copying $namelist_file to $RUN_DIR/namelist.input"
cp -v $namelist_file $RUN_DIR/namelist.input

# calculate date range 
datediff $y1-$m1-$d1 $y2-$m2-$d2

# create args to sed into namelist file
n_args="RUN_DAYS::$run_days RUN_HOURS::$run_hours START_YEAR::$y1"
n_args="$n_args START_MONTH::$m1 START_DAY::$d1"
n_args="$n_args START_HOUR::$h1 END_YEAR::$y2 "  
n_args="$n_args END_MONTH::$m2 END_DAY::$d2 END_HOUR::$h2"
n_args="$n_args FRAMES_PER_OUTFILE::24"
n_args="$n_args RESTART_RUN::false"  
n_args="$n_args RESTART_INTERVAL_MINS::2880"
n_args="$n_args FRAMES_PER_AUXHIST3::24"

echo -e "sed-ing times into namelist file"
sed_file $RUN_DIR/namelist.input $n_args

echo -e "done sed-ing times into namelist.input"
echo -e ""
echo -e "--------------------------------------"
echo -e ""


echo -e "creating directories in WRF_PROJECTS"
# Create New Directory and Sub-Directories for Re_Init Run
OUT_DIR=$PROJ_DIR\_INIT_$INIT_NAME
mkdir $OUT_DIR
mkdir $OUT_DIR/wrf_out
mkdir $OUT_DIR/wrfinput
mkdir $OUT_DIR/wrf_xtrm
mkdir $OUT_DIR/wrf_log
TRASHLIST="$TRASHLIST $OUT_DIR"



echo -e "copying submit scripts"
# Copy submit script from OG directory to the New Directory
wrf_submit_script=$(ls -d $PROJ_DIR/wrf_log/submit_wrf*| head -n 1)
real_submit_script=$(ls -d $PROJ_DIR/wrf_log/submit_wrf*| head -n 1)

filecheck $wrf_submit_script
filecheck $real_submit_script
cp $wrf_submit_script $OUT_DIR/


# ------------ sed submit script files for real and wrf --------------------# 

# Modify the path of the submit script to the correct directory ($RUN_DIR)
# sed in line-by-line. Note the DOUBLE QUOTES... otherwise variables are not evaluated.
# ALSO, note the @. sed can take many delimiters. / causes an error 


echo -e "######### WRF/REAL RUN SETUP  #############"
echo -e ""
echo -e "Sed-ing filepaths into WRF Submit script ... "

sed -i "27s@.*@TIMING_FILE=${WRF_DIR_COPY}@" $OUT_DIR/submit_wrf*
sed -i "28s@.*@RUN_DIR=${RUN_DIR}@" $OUT_DIR/submit_wrf*

echo -e "Sed-ing filepaths into Real Submit script ..."

sed -i "27s@.*@TIMING_FILE=${WRF_DIR_COPY}@" $OUT_DIR/submit_real*
sed -i "28s@.*@RUN_DIR=${RUN_DIR}@" $OUT_DIR/submit_real*

echo -e "Done sed-ing submit scripts"

# Change to the projects directory (it's ok to submit the job from here)
cd $OUT_DIR  # Change to the output directory 



# ------------ REAL.exe run --------------------# 

echo -e "######### Submit real.exe  #############"
echo -e ""

sbatch submit_real_* > ./catch_REALJOB_id

s_str='Submitted batch job'   # s_str = search string
job_id_real=$(grep "$s_str" ./catch_${job_name}_id | cut -d' ' -f4)
if [ "$job_id_real" = "" ]; then
    echo -e "\nNo $job_name.exe job ID found.\n"
    echo -e "Exiting.\n\n"
    exit 2
else
    echo -e "\nFound $job_name.exe job ID: $job_id_real\n"  
    echo -e "Removing temp job submission output file: catch_${job_name}_id.."
    rm -vf ./catch_${job_name}_id
    sleep 2
fi

wrf_loop_sec=60
wait_for_jobs $wrf_loop_sec $job_id_wrf



# ------------ Change WRFinput fields  --------------------# 

# Check that files exist 
filecheck $RUN_DIR/wrfinput_d01
filecheck $RUN_DIR/wrfinput_d02
echo -e "Insert $VARLIST into WRFINPUT file"

# Insert New Variables into wrfinput files;
Re_Init $d02_INIT_FILE $RUN_DIR/wrfinput_d02 
Re_Init $d01_INIT_FILE $RUN_DIR/wrfinput_d01    # Comment this out if ya don't want it





#------WRF SUBMISSION---------# 
# Check submit script 

echo -e "######### Submit WRF Run  #############"
echo -e ""



echo "Submitting WRF Job"
sbatch submit_wrf_* > ./catch_WRFJOB_id

# wrf.exe: recover job ID from job submission output file, and check it
s_str='Submitted batch job'   # s_str = search string
job_id_wrf=$(grep "$s_str" ./catch_WRFJOB_id | cut -d' ' -f4)

if [ "$job_id_wrf" = "" ]; then
    echo -e "\nNo $job_name.exe job ID found.\n"
    echo -e "Exiting.\n\n"
    exit 2
else
    echo -e "\nFound $job_name.exe job ID: $job_id_wrf\n"  
    echo -e "Removing temp job submission output file: catch_${job_name}_id.."
    rm -vf ./catch_${job_name}_id
    sleep 2
fi

#Timestep to query and check if WRF is still running in the Queue; I think
wrf_loop_sec=60
wait_for_jobs $wrf_loop_sec $job_id_wrf


echo -e "#################   WRF RUN FINISHED        ##############"
echo -e "#################   Completed $job_id_wrf   ##############"

#-----END WRF run --------------# 


echo -e ""
echo -e ""
echo -e ""
echo -e ""
echo -e ""
echo -e "#################   Clean UP, Move Files  ##############"
echo -e "copying files to PROJECT directory"

# move output files to OUTDIR
# Note, we are still w/in the OUTDIR directory

mv -v $RUN_DIR/wrfout* wrf_out/.
mv -v $RUN_DIR/wrfxtrm* wrf_xtrm/.
cp -v $RUN_DIR/rsl.error* wrf_log/.
cp -v $RUN_DIR/rsl.out* wrf_log/.
cp -v $RUN_DIR/wrf_*.log .

mv INIT_$INIT_NAME.log $OUT_DIR

echo -e "#################  DONE   ##############"






