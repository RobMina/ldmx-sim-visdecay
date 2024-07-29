
## Instructions to Setup and Run Simulation

- Clone this repo: `git clone --recursive git@github.com:RobMina/ldmx-sim-visdecay.git`

- cd into the new directory:
`cd ldmx-sim-visdecay`

- The container runner available on Rivanna is apptainer,
but the ldmx-sw environment assumes we will be using either docker
or singularity. So, we need to make an alias: 
`module load apptainer`
`alias singularity="apptainer"`

- Set the TMPDIR environment variable 
(necessary for ldmx-env.sh to run the first time on Rivanna):
`export TMPDIR=/scratch/<your Rivanna username>`

- Setup the ldmx-sw environment. 
This will take a long time (~30 minutes) the first time you do it.
`source ldmx-sw/scripts/ldmx-env.sh`



## Table of Contents

### Scripts for Generating MadGraph Dark Brem. Library

- `scripts/db-gen-lib-env.sh`: Set up the MadGraph dark brem container.
This is sourced within `scripts/run_db_gen_then_extract.sh`.
You can also source this to run the MadGraph generation interactively.

- `scripts/run_db_gen_then_extract.sh`: Set up, run MadGraph to generate
dark brem vertices in an lhe file, then run `g4db-extract-library` to extract
the relevant info (recoil e and A' kinematics) to a csv file. This should be
run from the base directory of the repository. Because MadGraph sometimes
fails to generate the desired number of vertices, this script automatically
re-runs the generation with sequentially increasing run numbers until the
desired number of vertices has been generated.

- `scripts/gen_unscaled_library.py`: Automatically generate batch scripts and
call sbatch for specified materials, A' masses, and incident energies. This 
creates a library of unscaled DB vertices that is needed for using the
G4DarkBreM module in simulation. Each material-mass-energy point is submitted
as a separate job.

### Scripts for Studying G4DarkBreM Dark Brem. Scaling

- `scripts/run_g4db_scale.sh`: Set up and run G4DarkBreM scaling of dark brem 
vertices, starting with a csv file created by `g4db-extract-library` and
producing another csv file using `g4db-scale`. Note that you must scale from a 
higher energy to a lower energy. This should be run from the base directory of 
the repository.

- `scripts/perform_scalings.py`: 

- `scripts/compile_dblib_into_df.py`: Merge 