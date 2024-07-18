#!/bin/bash
base_dir=/home/ram2aq/ldmx

### setting up dbgen
module load apptainer
dbgen_env_path=$base_dir/db-gen-lib/env_w_apptainer.sh
source $dbgen_env_path

dbgen_version=v4.6
dbgen_cachedir=/scratch/ram2aq/cache
dbgen_workdir=/scratch/ram2aq/work
dbgen_destdir=/scratch/ram2aq/temp
dbgen use $dbgen_version
dbgen cache $dbgen_cachedir
dbgen work $dbgen_workdir
dbgen dest $dbgen_destdir

### setting up G4DarkBreM (needed for g4db-extract-library)
source $base_dir/G4DarkBreM_mod/setup.sh
module load gcc
module load boost

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
g4db-extract-library -o ${output_filename} ${dbgen_output}
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
  g4db-extract-library -o ${output_filename} ${dbgen_output}
  ### delete the lhe file
  rm -rf ${dbgen_output}
  ### add the new events from the most recent run into the original run
  tail -n +2 ${output_filename} >> ${orig_output_filename}

  let eventsSoFar=${eventsSoFar}+`wc -l ${output_filename} | awk -F" " '{print $1}'`-1

  ### remove the most recent run (which is now a duplicate)
  rm ${output_filename}
done

echo "Total events generated=${eventsSoFar}"