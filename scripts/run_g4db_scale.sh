#!/bin/bash
base_dir=${PWD}

### setting up ldmx (needed for g4db-scale)
ldmx_env_path=$base_dir/ldmx-sw/scripts/ldmx-env.sh
source $ldmx_env_path

### arguments: {run number} {target material} {A' mass} {scale from energy} {scale to energy} {directory containing unscaled libs}
run_number=$1
material=$2
mass=$3
scale_from_energy=$4
scale_to_energy=$5
dblib_dir=$6

if [[ `echo "${scale_from_energy} <= ${scale_to_energy}" | bc` == 1 ]]; then
    >&2 echo "Cannot scale from $scale_from_energy to $scale_to_energy -- must scale from higher to lower energy."
    exit 1
fi

unscaled_fname=${dblib_dir}/electron_${material}_mA_${mass}_E_${scale_from_energy}_unscaled_run_${run_number}.csv

if [[ ! -f ${unscaled_fname} ]]; then
    >&2 echo "Unscaled file missing: $unscaled_fname"
    exit 1
fi

scaled_fname=${dblib_dir}/scaled/electron_${material}_mA_${mass}_E_${scale_to_energy}_scaledFrom_${scale_from_energy}_run_${run_number}.csv

if [[ -f ${scaled_fname} ]]; then
    >&2 echo "Output file already exists: $scaled_fname"
    exit 1
fi

declare -A material_Z=( ["tungsten"]="74" ["copper"]="29" ["lead"]="82" ["oxygen"]="8" ["silicon"]="14")

let events=`wc -l ${unscaled_fname} | awk -F" " '{print $1}'`-1

massMeV="$(echo "$mass * 1000" | bc)"

ldmx g4db-scale --scale-APrime -o ${scaled_fname} -E ${scale_to_energy} -Z ${material_Z[${material}]} -N ${events} -M ${massMeV} ${unscaled_fname}