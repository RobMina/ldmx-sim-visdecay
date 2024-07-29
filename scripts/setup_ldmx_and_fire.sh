#!/bin/bash

# first argument is the _absolute_ path to ldmx-sim-visdecay
PATH_TO_LDMX_SIM_VISDECAY=$1
# second argument is the _relative_ path to the config script to run
PATH_TO_CONFIG_SCRIPT=$2
# third argument is the _relative_ path to the MG dark brem event library
PATH_TO_MG_DB_LIB=$3
# fourth argument is number of events
N_EVENTS=$4

cd ${PATH_TO_LDMX_SIM_VISDECAY}
module load apptainer # needed to load container
alias singularity="apptainer" # needed to load container
source ldmx-sw/scripts/ldmx-env.sh

ldmx fire ${PATH_TO_CONFIG_SCRIPT} ${PATH_TO_MG_DB_LIB} ${N_EVENTS}