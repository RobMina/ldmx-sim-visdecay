import pandas as pd
import numpy as np
import glob

dblib_path = "/standard/ldmxuva/data/dblib"

### run params: ( lepton, material, mA [GeV], scaled [bool], 
###               incident_energy [GeV], scaled_from_E [GeV], run number )
### if scaled == False, then incident_energy == scaled_from_E
### unscaled filename: <lepton>_<material>_mA_<mA>_E_<incident_energy>_unscaled_run_<run number>.csv
### scaled filename: <lepton>_<material>_mA_<mA>_E_<incident_energy>_scaledFrom_<scaled_from_E>_run_<run number>.csv
def extract_run_params_from_filename(name):
    run_params = {}
    toks = name.split('_')
    run_params["lepton"] = toks[0]
    run_params["material"] = toks[1]
    run_params["mA"] = float(toks[3])
    run_params["incident_energy"] = float(toks[5])
    run_params["scaled"] = "scaledFrom" in toks
    if run_params["scaled"]:
        run_params["scaled_from_E"] = float(toks[7])
        run_params["run_number"] = int(toks[9][:-4])
    else:
        run_params["scaled_from_E"] = run_params["incident_energy"]
        run_params["run_number"] = int(toks[8][:-4])
    return run_params

def add_extra_columns(run_params, df):
    df['lepton'] = run_params['lepton']
    df['target'] = run_params['material']
    df['mA'] = run_params['mA']
    df['scaled'] = run_params['scaled']
    df['scaled_from_E'] = run_params['scaled_from_E']
    df['run_number'] = run_params['run_number']

def process_file(name):
    run_params = extract_run_params_from_filename(name)
    df = pd.read_csv(name)
    add_extra_columns(run_params, df)
    return df

materials = ["copper", "lead", "oxygen", "silicon", "tungsten"]
masses = ["0.005", "0.01", "0.05", "0.1"]

for material in materials:
    for mass in masses:
        unscaled = pd.concat(map(process_file, glob.iglob(dblib_path + "/electron_" + material + "_mA_" + mass + "_E_*_unscaled_run_*.csv")))
        scaled = pd.concat(map(process_file, glob.iglob(dblib_path + "/scaled/electron_" + material + "_mA_" + mass + "_E_*_scaledFrom_*_run_*.csv")))
        unscaled.reset_index().to_feather("dblib_unscaled_electron_" + material + "_mA_" + mass + ".feather")
        scaled.reset_index().to_feather("dblib_scaled_electron_" + material + "_mA_" + mass + ".feather")
