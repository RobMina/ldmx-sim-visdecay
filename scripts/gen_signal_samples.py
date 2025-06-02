import math
import os

# you should modify the following:
ldmx_denv_dir = "/home/ram2aq/ldmx/ldmx-sw"
output_dir = "/scratch/ram2aq"
# note: this one is defined as an _absolute_ path
db_lib_dir = "/scratch/ram2aq/dblib"
scripts_dir = "/home/ram2aq/ldmx/ldmx-sim-visdecay/scripts/"
# note: this path must be relative to the ldmx_denv_dir defined above
config_path = "test_config.py"

run_script = "{scripts_dir}/setup_ldmx_and_fire.sh".format(
    scripts_dir=scripts_dir
)
def write_slurm_to_fh(fh, path_to_ldmx_denv, 
                      path_to_config_script, path_to_mg_db_lib, n_events,
                      output_path):
    fh.write("#!/bin/bash\n")
    fh.write("\n")
    fh.write("#SBATCH --ntasks=1\n")
    fh.write("#SBATCH --mem=4000\n")
    fh.write("#SBATCH --partition=standard\n")
    fh.write("#SBATCH --account=ldmxuva\n")

    hours = math.ceil(n_events / 1000) # guessing 1000 events/hour
    fh.write("#SBATCH --time={hours:02d}:00:00\n".format(hours=hours))

    # Get A' mass from the dark brem library name
    lib_parameters = os.path.splitext(

            os.path.basename(path_to_mg_db_lib)
 
        )[0].split('_')
    ap_mass = float(lib_parameters[lib_parameters.index('mA')+1])*1000.
    run_num = int(lib_parameters[lib_parameters.index('run')+1])
    output_fstem = "category_signal_Nevents_{n_events}_MaxTries_10k_mAMeV_{ap_mass:04d}_epsilon_0.01_minApE_4000_minPrimEatEcal_7000_run_{run_num}".format(
        n_events = n_events,
        ap_mass = int(ap_mass),
        run_num = run_num
    )

    slurm_out = "{output_path}/slurm/slurm_{output_fstem}.out".format(
        output_path = output_path, output_fstem = output_fstem
    )
    slurm_err = "{output_path}/slurm/slurm_{output_fstem}.err".format(
        output_path = output_path, output_fstem = output_fstem
    )
    fh.write("#SBATCH --output={slurm_out}\n".format(slurm_out=slurm_out))
    fh.write("#SBATCH --error={slurm_err}\n".format(slurm_err=slurm_err))
    fh.write("\n")
    fh.write("{run_script} {path_to_ldmx_denv} {path_to_config_script} {path_to_mg_db_lib} {n_events}\n".format(
        run_script = run_script,
        path_to_ldmx_denv = path_to_ldmx_denv,
        path_to_config_script = path_to_config_script,
        path_to_mg_db_lib = path_to_mg_db_lib,
        n_events = n_events
    ))
    # move output file into desired output path
    fh.write("mv {path_to_ldmx_denv}/{output_fstem}.root {output_path}".format(
        path_to_ldmx_denv=path_to_ldmx_denv,
        output_fstem=output_fstem,
        output_path=output_path
    ))

def run_for_params(run_number, mass, path_to_ldmx_denv, 
                      path_to_config_script, db_lib_dir, n_events,
                      output_path):
    db_lib_fname = "{db_lib_dir}/all_mA_{mass}_run_{run_number}.csv".format(
        db_lib_dir = db_lib_dir, mass = mass, run_number = run_number
    )
    slurm_fname = "{output_path}/all_mA_{mass}_run_{run_number}.slurm".format(
        output_path = output_path, mass = mass, run_number = run_number
    )
    with open(slurm_fname, "w") as fh:
        write_slurm_to_fh(fh, path_to_ldmx_denv, path_to_config_script,
                          db_lib_fname, n_events, output_path)
    os.system("sbatch {slurm_fname}".format(slurm_fname=slurm_fname))

for mass in [0.005]:#, 0.01, 0.05, 0.1]:
    for run_number in [4100]:
        run_for_params(run_number, mass, ldmx_denv_dir,
                       config_path, db_lib_dir,
                       10000, output_dir)
