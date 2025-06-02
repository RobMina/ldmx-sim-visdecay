#!/bin/bash

# update these with paths to your directories
dbgen_denv_dir=/home/ram2aq/ldmx/dbgen
dbgen_version=v5.1.1
ldmx_denv_dir=/home/ram2aq/ldmx/ldmx-sw
ldmx_sw_version=v4.3.1

# note: requires denv (https://tomeichlersmith.github.io/denv/)
### setting up dbgen
module load apptainer
cd ${dbgen_denv_dir}
yes | denv init ldmx/dark-brem-lib-gen:${dbgen_version}

dbgen_scratchdir=/scratch/${USER}/scratch
dbgen_destdir=/scratch/${USER}/temp

mkdir -p ${dbgen_scratchdir}
mkdir -p ${dbgen_destdir}

denv config mounts ${dbgen_scratchdir}
denv config mounts ${dbgen_destdir}

### setting up ldmx (needed for g4db-extract-library)
cd ${ldmx_denv_dir}
yes | denv init ldmx/pro:${ldmx_sw_version}

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
cd ${dbgen_denv_dir}
denv dark-brem-lib-gen -o ${dbgen_destdir} -s ${dbgen_scratchdir} --run ${run_number} --nevents ${events} --max-energy ${energy} --min-energy ${energy} --apmass ${mass} --target ${material} --lepton electron
dbgen_output=$dbgen_destdir/electron_${material}_MaxE_${energy}_MinE_${energy}_RelEStep_0.1_UndecayedAP_mA_${mass}_run_${run_number}
### extract only relevant info (recoil e and A' kinematics) to csv file
cd ${ldmx_denv_dir}
denv g4db-extract-library --aprime-id 1023 -o ${output_filename} ${dbgen_output}
### delete the lhe file
rm -rf ${dbgen_output}

first_line=$(head -n 1 ${output_filename})
test_line="target_Z,incident_energy,recoil_energy,recoil_px,recoil_py,recoil_pz,centerMomentum_energy,centerMomentum_px,centerMomentum_py,centerMomentum_pz"
if [[ ${first_line} != ${test_line} ]]; then
  sed -i '1i\'"$test_line" $output_filename
fi

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
  cd ${dbgen_denv_dir}
  denv dark-brem-lib-gen -o ${dbgen_destdir} -s ${dbgen_scratchdir} --run ${run_number} --nevents ${events} --max-energy ${energy} --min-energy ${energy} --apmass ${mass} --target ${material} --lepton electron
  dbgen_output=$dbgen_destdir/electron_${material}_MaxE_${energy}_MinE_${energy}_RelEStep_0.1_UndecayedAP_mA_${mass}_run_${run_number}
  ### extract only relevant info (recoil e and A' kinematics) to csv file
  cd ${ldmx_denv_dir}
  denv g4db-extract-library --aprime-id 1023 -o ${output_filename} ${dbgen_output}
  ### delete the lhe file
  rm -rf ${dbgen_output}
  ### add the new events from the most recent run into the original run
  tail -n +2 ${output_filename} >> ${orig_output_filename}

  let eventsSoFar=${eventsSoFar}+`wc -l ${output_filename} | awk -F" " '{print $1}'`-1

  ### remove the most recent run (which is now a duplicate)
  rm ${output_filename}
done

echo "Total events generated=${eventsSoFar}"
