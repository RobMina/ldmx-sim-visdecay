#!/bin/bash

mA="0.005"
run="4100"
dblib_dir="/scratch/ram2aq/dblib"
output_fname="/scratch/ram2aq/dblib/all_mA_${mA}_run_${run}.csv"

echo "target_Z,incident_energy,recoil_energy,recoil_px,recoil_py,recoil_pz,centerMomentum_energy,centerMomentum_px,centerMomentum_py,centerMomentum_pz" >> ${output_fname}

for i in `ls ${dblib_dir}/electron_*_mA_${mA}_*_run_${run}.csv`; do
  [ -f "$i" ] || break
  tail -n +2 $i >> ${output_fname}
  echo "$i"
done

echo "done"
