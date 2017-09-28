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
#USER INPUT
#------------------------------------

y1=$1
m1=$2
d1=$3
h1=$4
y2=$5
m2=$6
d2=$7
h2=$8

d02_INIT_FILE=$9
d01_INIT_FILE="${INIT_FILE//d02/d01}"  # replaces the d02 with d02 in the filename
INIT_NAME=${10}

#The file containing the WRF output files that we want to insert into the WRF intut file
#find /mnt/wrf_history/*/wrf_out/*/d02/ -name wrfout_d02_2003-11-20*
#INIT_FILE=/mnt/wrf_history/vol12/wrf_out/wy_2016/d02/wrfout_d02_2016-03-14_00:00:00



#------------------------------------
# FILES AND DIRECTORIES
#------------------------------------

WRF_DIR=/home/wrudisill/scratch/WRF_SIM_CFSR_${y1}-${m1}-${d1}_${h1}__${y2}-${m2}-${d2}_${h2}/wrf_cfsr_${y1}${m1}${d1}${h1}_${y2}${m2}${d2}${h2}  

PROJ_DIR=/home/wrudisill/scratch/WRF_PROJECTS/wrf_cfsr_${y1}-${m1}-${d1}_${h1}__${y2}-${m2}-${d2}_${h2}                        

# The directory containing matt's wrf run funcs scripts
FUNCS=/home/wrudisill/WRF-R2/funcs/std_funcs.sh

#------------------------------------
# More Options
#------------------------------------

#DOMAIN=d02
VARLIST=SNOW,SNOWH,SNOWC

#------------------------------------
# FUNCTIONS
#------------------------------------
function filecheck()
{
    if [ -e $1 ]
    then
	echo -e "found" $1 
    else
	echo -e "not found" $1
	exit 2 
    fi
}


datediff() {
    local d1=$(date -d "$1" +%s)
    local d2=$(date -d "$2" +%s)
    days=$(( (d2 - d1) / 86400))   # These are global
    hours=$(($days*24))            # These are global
}



function Re_Init()
{
    # $1 : The high res file to stick in the wrfinput file
    # $2 : The wrfinput file to be updated
    ncks -A -v $VARLIST -d Time,1 $1 $2 
    local status=$?

    if [ "$status" != 0 ]; then
	echo -e "\nNo ncks failed; check yourself\n"
	echo -e "Exiting.\n\n"
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
# MAIN
#------------------------------------------------------------
exec >> INIT_$INIT_NAME.log 
exec 2>&1 

sleep 2

echo -e "#############################################"
echo -e ""
echo -e " Starting Re-Initialization Run for:        "
echo -e "                                            "
echo -e "     WRF Run:  ${WRF_DIR}                    "
echo -e "                                            "
echo -e "     Initializing Variables:  ${VARLIST}  "
echo -e "                                            "
echo -e "     from Files:  ${d02_INIT_FILE}, ${d01_INIT_FILE}"
echo -e " "
echo -e "#############################################"

sleep 20

# Source std_funcs.sh
source $FUNCS

# Create a copy of the WRF_DIR to house the new simulation; Maybe later we want to delete this; 

echo -e "####### Checking that paths and files make sense ##########"
echo -e " "

filecheck $PROJ_DIR
filecheck $WRF_DIR
filecheck $d01_INIT_FILE
filecheck $d02_INIT_FILE


echo -e "####### Copy Directories and Files ##########"
echo -e " "
echo -e "creating a copy of $WRF_DIR..."

WRF_DIR_COPY=$WRF_DIR\_INIT_$INIT_NAME

#copy files, exclude previous wrfout files from copying

rsync -av --exclude 'wrfout*' --exclude 'wrfxtrm*' --exclude 'wrfrst*' $WRF_DIR/ $WRF_DIR_COPY 
echo -e "created $WRF_DIR_COPY"

# Create RUN_DIR variable path for the run directory within the new WRF_DIR copy
RUN_DIR=$WRF_DIR_COPY/run


# COPY AND SET UP NAMELIST FILE
echo -e "copying namelist.input to $RUN_DIR"
# Copy namelist.input_YYYY-MM-DD_HH to the RUN_DIR (The namelist.input gets removed from the directory for whatever readson)

namelist_file=$(ls -d $PROJ_DIR/wrf_log/namelist.input_*| head -n 1)
echo -e $namelist_file 

cp -v $namelist_file $RUN_DIR/namelist.input


# create args to sed into namelist file
n_args="RUN_DAYS::$run_days RUN_HOURS::$run_hours START_YEAR::$y1"
n_args="$n_args START_MONTH::$m1 START_DAY::$d1"
n_args="$n_args START_HOUR::$h1 END_YEAR::$y2 "  
n_args="$n_args END_MONTH::$m2 END_DAY::$d2 END_HOUR::$h2"
  

echo -e "sed-ing times into namelist file"

sed_file $RUN_DIR/namelist.input $n_args

echo -e "done sed-ing times into namelist.input"
echo -e ""
echo -e "--------------------------------------"
echo -e ""


echo -e "Creating OUTPUT Directories"
# Create New Directory and Sub-Directories for Re_Init Run
OUT_DIR=$PROJ_DIR\_INIT_$INIT_NAME
mkdir $OUT_DIR
mkdir $OUT_DIR/wrf_out
mkdir $OUT_DIR/wrfinput
mkdir $OUT_DIR/wrf_xtrm
mkdir $OUT_DIR/wrf_log

# maybe more....

# Copy submit script from OG directory to the New Directory
submit_script=$(ls -d $PROJ_DIR/wrf_log/submit_wrf*| head -n 1)

filecheck $submit_script
cp $submit_script $OUT_DIR

# Modify the path of the submit script to the correct directory ($RUN_DIR)
# sed in line-by-line. Note the DOUBLE QUOTES... otherwise variables are not evaluated.
# ALSO, note the @. sed can take many delimiters. / causes an error 


echo -e "######### WRF RUN SETUP  #############"
echo -e ""
echo -e "Sed-ing filepaths into WRF Submit script"

sed -i "27s@.*@TIMING_FILE=${WRF_DIR_COPY}@" $OUT_DIR/submit_wrf*
sed -i "28s@.*@RUN_DIR=${RUN_DIR}@" $OUT_DIR/submit_wrf*



echo -e "Insert $VARLIST into WRFINPUT file"

# Insert New Variables into wrfinput files;
Re_Init $d02_INIT_FILE $RUN_DIR/wrfinput_d02 
Re_Init $d01_INIT_FILE $RUN_DIR/wrfinput_d01    # Comment this out if ya don't want it


echo -e "copy $RUN_DIR/wrfinput_$DOMAIN  file to $OUTDIR/wrfinput"

# Copy WRF_INPUT Files to Output Directory ; maybe this is superfluous 
cp $RUN_DIR/wrfinput_$DOMAIN $OUT_DIR/wrfinput/.


echo -e "######### WRF RUN SETUP  #############"
echo -e ""
#------WRF SUBMISSION---------# 
# Check submit script 

echo "Submitting WRF Job"
cd $OUT_DIR  # Change to the output directory 

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

cp -v $RUN_DIR/wrfout* wrf_out/.
cp -v $RUN_DIR/wrfxtrm* wrf_xtrm/.
cp -v $RUN_DIR/rsl.error* wrf_log/.
cp -v $RUN_DIR/rsl.out* wrf_log/.
cp -v $RUN_DIR/wrf_*.log .

mv INIT_$INIT_NAME.log $OUT_DIR

echo -e "#################  DONE   ##############"






