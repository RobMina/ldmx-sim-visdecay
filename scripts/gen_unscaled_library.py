import math
import os

# update this with path to your directory
scripts_dir = "/home/ram2aq/ldmx/ldmx-sim-visdecay/scripts/"
run_script = "{scripts_dir}/dbgen_then_extract.sh".format(
    scripts_dir=scripts_dir
)
def write_slurm_to_fh(fh, run_number, material, mass, energy, events, output_path):
    fh.write("#!/bin/bash\n")
    fh.write("\n")
    fh.write("#SBATCH --ntasks=1\n")
    fh.write("#SBATCH --mem=1000\n") # testing shows MG/ME uses << 1 GB of RAM
    fh.write("#SBATCH --partition=standard\n")
    fh.write("#SBATCH --account=ldmxuva\n")
    hours = math.ceil(events / 80000) # estimated 80,000 events/hr at slowest
    fh.write("#SBATCH --time={hours:02d}:00:00\n".format(hours=hours))
    output_fstem = "electron_{material}_mA_{mass}_E_{energy}_unscaled_run_{run_number}".format(
        material=material, mass=mass, energy=energy, run_number=run_number)
    slurm_out="{output_path}/slurm/slurm_{output_fstem}.out".format(
        output_path=output_path, output_fstem=output_fstem)
    slurm_err="{output_path}/slurm/slurm_{output_fstem}.err".format(
        output_path=output_path, output_fstem=output_fstem)
    fh.write("#SBATCH --output={slurm_out}\n".format(slurm_out=slurm_out))
    fh.write("#SBATCH --error={slurm_err}\n".format(slurm_err=slurm_err))
    fh.write("\n")
    fh.write("{run_script} {run_number} {material} {mass} {energy} {events} {output_path}".format(
        run_script=run_script, run_number=run_number, material=material, mass=mass, 
        energy=energy, events=events, output_path=output_path
    ))

def run_for_params(run_number, material, mass, energy, events, output_path):
    slurm_fname = "{output_path}/slurm/electron_{material}_mA_{mass}_E_{energy}_unscaled_run_{run_number}.slurm".format(
        output_path=output_path, material=material, mass=mass, energy=energy, run_number=run_number
    )
    with open(slurm_fname, "w") as fh:
        write_slurm_to_fh(fh, run_number, material, mass, energy, events, output_path)
    os.system("sbatch {slurm_fname}".format(slurm_fname=slurm_fname))

materials = ["tungsten", "silicon", "copper", "lead", "oxygen"]
masses = ["0.005"]#, "0.01", "0.05", "0.1"]
energies = ["4.0", "4.4", "4.8", "5.2", "5.6", "6.0", "6.4",
            "6.8", "7.2", "7.6", "8.0"]
neventsPerPoint = 10000
output_dir = "/scratch/ram2aq/dblib"
run_number = 4100

for material in materials:
    for mass in masses:
        for energy in energies:
            run_for_params(run_number, material, mass, energy, neventsPerPoint, output_dir)
