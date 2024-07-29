#!/bin/bash
base_dir=${PWD}

### setting up dbgen
module load apptainer
alias singularity="apptainer"
dbgen_env_path=$base_dir/scripts/db-gen-lib-env.sh
source $dbgen_env_path

dbgen_version=v4.6
dbgen_cachedir=/scratch/${USER}/cache
dbgen_workdir=/scratch/${USER}/work
dbgen_destdir=/scratch/${USER}/temp
dbgen use $dbgen_version
dbgen cache $dbgen_cachedir
dbgen work $dbgen_workdir
dbgen dest $dbgen_destdir

### setting up ldmx (needed for g4db-extract-library)
ldmx_env_path=$base_dir/ldmx-sw/scripts/ldmx-env.sh
source $ldmx_env_path

### arguments: {run number} {target material} {A' mass} {incident energy} {number of events} {output path}
run_number=$1
material=$2
mass=$3
energy=$4
events=$5
output_path=$6
output_filename=${output_path}/electron_${material}_mA_${mass}_E_${energy}_unscaled_run_${run_number}.csv

if [[ -f ${output_filename} ]]; then
  >&2 echo "Output file already exists: $output_filename"
  exit 1
fi

### run dbgen to generate lhe file
dbgen run --run ${run_number} --nevents ${events} --max_energy ${energy} --min_energy ${energy} --apmass ${mass} --target ${material} --lepton electron
dbgen_output=$dbgen_destdir/electron_${material}_MaxE_${energy}_MinE_${energy}_RelEStep_0.1_UndecayedAP_mA_${mass}_run_${run_number}
### extract only relevant info (recoil e and A' kinematics) to csv file
ldmx g4db-extract-library -o ${output_filename} ${dbgen_output}
### delete the lhe file
rm -rf ${dbgen_output}

let eventsSoFar=`wc -l ${output_filename} | awk -F" " '{print $1}'`-1
orig_output_filename=${output_filename}
### keep running, with increasing run numbers, until we get the desired events
while [ ${eventsSoFar} -lt ${events} ]; do
  let run_number=${run_number}+1
  echo "Found only $eventsSoFar events of requested $events. Running again with run number $run_number."

  output_filename=${output_path}/electron_${material}_mA_${mass}_E_${energy}_unscaled_run_${run_number}.csv

  if [[ -f ${output_filename} ]]; then
    >&2 echo "Output file already exists: $output_filename"
    exit 1
  fi

  ### run dbgen to generate lhe file
  dbgen run --run ${run_number} --nevents ${events} --max_energy ${energy} --min_energy ${energy} --apmass ${mass} --target ${material} --lepton electron
  dbgen_output=$dbgen_destdir/electron_${material}_MaxE_${energy}_MinE_${energy}_RelEStep_0.1_UndecayedAP_mA_${mass}_run_${run_number}
  ### extract only relevant info (recoil e and A' kinematics) to csv file
  ldmx g4db-extract-library -o ${output_filename} ${dbgen_output}
  ### delete the lhe file
  rm -rf ${dbgen_output}
  ### add the new events from the most recent run into the original run
  tail -n +2 ${output_filename} >> ${orig_output_filename}

  let eventsSoFar=${eventsSoFar}+`wc -l ${output_filename} | awk -F" " '{print $1}'`-1

  ### remove the most recent run (which is now a duplicate)
  rm ${output_filename}
done

echo "Total events generated=${eventsSoFar}"