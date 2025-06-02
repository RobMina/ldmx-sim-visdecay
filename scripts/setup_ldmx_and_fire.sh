#!/bin/bash

# first argument is the path to directory with ldmx container
PATH_TO_LDMX_DENV=$1
LDMX_VERSION=v4.3.1
# second argument is the path to the config script to run
PATH_TO_CONFIG_SCRIPT=$2
# third argument is the path to the MG dark brem event library
PATH_TO_MG_DB_LIB=$3
# fourth argument is number of events
N_EVENTS=$4

module load apptainer # needed to load container
cd ${PATH_TO_LDMX_DENV}
yes | denv init ldmx/pro:${LDMX_VERSION}

denv config mounts $(dirname ${PATH_TO_CONFIG_SCRIPT})
denv config mounts $(dirname ${PATH_TO_MG_DB_LIB})

denv fire ${PATH_TO_CONFIG_SCRIPT} ${PATH_TO_MG_DB_LIB} ${N_EVENTS}