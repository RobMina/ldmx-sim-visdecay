
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
This will take a long time (~30 minutes) the first time you do it, but will be
relatively quick after the first time.
`source ldmx-sw/scripts/ldmx-env.sh`

- Compile the updated code. This also takes a while, but only the first 
time.
`ldmx compile`

## Table of Contents

### Scripts for Generating MadGraph Dark Brem Library

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

### Scripts for Studying G4DarkBreM Dark Brem Scaling

- `scripts/run_g4db_scale.sh`: Set up and run G4DarkBreM scaling of dark brem 
vertices, starting with a csv file created by `g4db-extract-library` and
producing another csv file using `g4db-scale`. Note that you must scale from a 
higher energy to a lower energy. This should be run from the base directory of 
the repository.

- `scripts/perform_scalings.py`: Automatically run G4DarkBreM scaling for a
variety of materials, A' masses, and energy scaling points. This runs
interactively rather than using sbatch.

- `scripts/compile_dblib_into_df.py`: Merge and compress csv files from
`gen_unscaled_library.py` and `perform_scalings.py` into `.feather` files:
one unscaled and one scaled for each material and A' mass.

- `scripts/fill_dblib_scaling_hists.py`: Create histograms from the `.feather`
files containing unscaled and scaled dark brem vertices to validate the scaling
done in G4DarkBreM.

- `scripts/scaling_studies.ipynb`: A Jupyter notebook with code to validate
the scaling done in G4DarkBreM.

### Scripts for Generating LDMX Dark Brem Signal Samples

- `scripts/test_config.py`: A config file passed to ldmx fire. Configures
the generator to scale A' kinematics and decays using the updated G4DarkBreM
module. Takes two arguments: the path to a MG dark brem library and the number
of events to simulate.

- `scripts/decay_validation.ipynb`: A Jupyter notebook with code to validate
the handling of A' decays within G4DarkBreM.

- `scripts/setup_ldmx_and_fire.sh`: setup, then call ldmx fire. Assumes that
the config scripts takes the same arguments as `test_config.py`: namely, the
path to a MG dark brem library and the number of events.

- `scripts/gen_signal_samples.py`: automatically configure and launch grid jobs
using sbatch to generate signal samples for each mass point and run number.
Corresponding MG dark brem libraries must have already been created and must
be in csv format. You should modify the paths defined near the bottom of this
script before using it.