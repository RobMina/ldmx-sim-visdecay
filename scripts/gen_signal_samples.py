import math
import os

# this needs to be a relative path from the base of the ldmx-sim-visdecay repo
run_script = "scripts/setup_ldmx_and_fire.sh"
# path_to_ldmx_sim_visdecay is an _absolute_ path
# output_path can be either absolute or relative
# all other paths need to be _relative_ paths from the base of ldmx-sim-visdecay
def write_slurm_to_fh(fh, path_to_ldmx_sim_visdecay, 
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
    fh.write("{path_to_ldmx_sim_visdecay}/{run_script} {path_to_ldmx_sim_visdecay} {path_to_config_script} {path_to_mg_db_lib} {n_events}\n".format(
        run_script = run_script,
        path_to_ldmx_sim_visdecay = path_to_ldmx_sim_visdecay,
        path_to_config_script = path_to_config_script,
        path_to_mg_db_lib = path_to_mg_db_lib,
        n_events = n_events
    ))
    # move output file into desired output path
    fh.write("mv {path_to_ldmx_sim_visdecay}/{output_fstem}.root {output_path}".format(
        path_to_ldmx_sim_visdecay=path_to_ldmx_sim_visdecay,
        output_fstem=output_fstem,
        output_path=output_path
    ))


with open("test.slurm", "w") as fh:
    write_slurm_to_fh(fh, "/home/ram2aq/ldmx/ldmx-sim-visdecay", 
                      "scripts/test_config.py", "all_mA_0.005_run_4000.csv",
                      1000, "/home/ram2aq/ldmx/data/eat_vis_signal/")