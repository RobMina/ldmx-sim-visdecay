import numpy as np
import pandas as pd
import math
import json
import pickle

# baseSeq is the sequence that will be used to set the bin widths/edges
# assuming the bins are not passes as a parameter
# return (baseHist, bins, [compHists]) where compHists is in the same
# order as the argument compSeqs
def make_comparison_hists(baseSeq, compSeqs,
                          minX=None, maxX=None, bins=None,
                          logX=False, cumulative=False):
    if bins is None:
        minVal = np.min(baseSeq)
        maxVal = np.max(baseSeq)
        if len(compSeqs) > 0:
            minVal = min(minVal, min([np.min(seq) for seq in compSeqs]))
            maxVal = max(maxVal, max([np.max(seq) for seq in compSeqs]))
        if minX is None:
            minX = minVal - 0.05 * (maxVal - minVal)
        if maxX is None:
            maxX = maxVal + 0.05 * (maxVal - minVal)

        if logX:
            bins = np.histogram_bin_edges(np.log(baseSeq), bins='auto', range=(np.log(minX), np.log(maxX)))
        else:
            bins = np.histogram_bin_edges(baseSeq, bins='auto', range=(minX, maxX))

        # sometimes histogram_bin_edges returns a huge number (30000+),
        # so truncate
        if len(bins) > 50:
            if logX:
                bins = np.histogram_bin_edges(np.log(baseSeq), bins=50, range=(np.log(minX), np.log(maxX)))
            else:
                bins = np.histogram_bin_edges(baseSeq, bins=50, range=(minX, maxX))
    
    baseHist = np.histogram(log(baseSeq) if logX else baseSeq, bins=bins,
                            weights=np.full(len(baseSeq), 1./len(baseSeq)))[0]
    compHists = [
        np.histogram(log(seq) if logX else seq, bins=bins,
                     weights=np.full(len(seq), 1./len(seq)))[0]
            for seq in compSeqs
    ]

    if cumulative:
        baseHist = np.cumsum(baseHist)
        compHists = [np.cumsum(hist) for hist in compHists]
    if logX: # exponentiate bins so that we return in correct units
        bins = np.exp(bins)
    return (baseHist, bins, compHists)

# returns (baseEHist, bins, [compEsHists]) where compEsHists is in the
# same order as the argument compEs
def make_comparison_unscaled_hists(unscaled, varName, baseE, compEs, 
                                   minX=None, maxX=None, bins=None, 
                                   logX=False, cumulative=False):
    baseESeq = unscaled[unscaled['incident_energy'] == baseE][varName]
    compEsSeqs = [unscaled[unscaled['incident_energy'] == compE][varName] for compE in compEs]
    return make_comparison_hists(baseESeq, compEsSeqs, 
                                 minX, maxX, bins, logX, cumulative)

# similar to above, but we make the comparison histograms using the scaled
# dataframes
def make_comparison_scaled_hists(unscaled, scaled, varName, baseE, compEs,
                                 minX=None, maxX=None, bins=None,
                                 logX=False, cumulative=False):
    baseESeq = unscaled[unscaled['incident_energy'] == baseE][varName]
    compEsSeqs = [
        scaled[(scaled['incident_energy'] == baseE) 
                & (scaled['scaled_from_E'] == compE)][varName]
        for compE in compEs
    ]
    return make_comparison_hists(baseESeq, compEsSeqs,
                                 minX, maxX, bins, logX, cumulative)

# filename: dblib_[un]scaled_<lepton>_<material>_mA_<mA>.feather
def load_dblib(dblib_path, scaled, material, mA, lepton="electron"):
    filename = dblib_path + "/dblib_{sc}_{lep}_{mat}_mA_{m}.feather".format(
        sc = "scaled" if scaled else "unscaled",
        lep = lepton,
        mat = material,
        m = mA
    )
    return pd.read_feather(filename)

# var_specs is a list of tuples:
#    (variable name, kwargs dict which must match the keywords above
# energy_pairs is also a list of tuples:
#   (base energy, [list of comparison energies])
# return dictionary organized like so:
# material -> mass -> variable name -> base energy -> 
#    (baseEHist, bins, compEs, compEHists_unscaled, compEHists_scaled)
def make_scaling_hists_dict(dblib_path, materials, masses, 
                            var_specs, energy_pairs):
    retval = {}
    for material in materials:
        retval[material] = {}
        for mass in masses:
            retval[material][mass] = {}

            unscaled = load_dblib(dblib_path, False, material, mass)
            scaled = load_dblib(dblib_path, True, material, mass)

            setup_derived_columns(unscaled)
            setup_derived_columns(scaled)

            for var_spec in var_specs:
                varName = var_spec[0]

                retval[material][mass][varName] = {}

                for energy_pair in energy_pairs:
                    baseE = energy_pair[0]
                    compEs = energy_pair[1]

                    baseEHist, bins, compEHists_unscaled = make_comparison_unscaled_hists(
                        unscaled, varName, baseE, compEs, **var_spec[1]
                    )
                    print(material, mass, varName, baseE, len(bins))

                    var_spec[1]['bins'] = bins
                    compEHists_scaled = make_comparison_scaled_hists(
                        unscaled, scaled, varName, baseE, compEs, **var_spec[1]
                    )[2]

                    retval[material][mass][varName][baseE] = (
                        baseEHist, bins, compEs, compEHists_unscaled, compEHists_scaled
                    )
                # for energy_pair in energy_pairs
            # for var_spec in var_specs

            del unscaled
            del scaled
        # for mass in masses
    # for material in materials
    return retval

def setup_derived_columns(df):
    df["ap_energy"] = df["centerMomentum_energy"] - df["recoil_energy"]
    df["ap_px"] = df["centerMomentum_px"] - df["recoil_px"]
    df["ap_py"] = df["centerMomentum_py"] - df["recoil_py"]
    df["ap_pz"] = df["centerMomentum_pz"] - df["recoil_pz"]

    df["recoil_pt"] = np.sqrt(df["recoil_px"]**2 + df["recoil_py"]**2)
    df["ap_pt"] = np.sqrt(df["ap_px"]**2 + df["ap_py"]**2)
    df["recoil_phi"] = np.arctan2(df["recoil_py"], df["recoil_px"])
    df["ap_phi"] = np.arctan2(df["ap_py"], df["ap_px"])
    df["recoil_theta"] = np.arctan2(df["recoil_pt"], df["recoil_pz"])
    df["ap_theta"] = np.arctan2(df["ap_pt"], df["ap_pz"])

    df["recoil_energy_frac"] = df["recoil_energy"] / df["incident_energy"]
    df["ap_energy_frac"] = df["ap_energy"] / df["incident_energy"]
    df["delta_phi"] = np.abs(df["recoil_phi"] - df["ap_phi"])
                     #np.minimum(np.abs(df["recoil_phi"] - df["ap_phi"]), 
                     #2*math.pi - np.abs(df["recoil_phi"] - df["ap_phi"]))

    df["angle_recoil_ap"] = np.arccos(
        (df["ap_px"] * df["recoil_px"] + 
         df["ap_py"] * df["recoil_py"] + 
         df["ap_pz"] * df["recoil_pz"]) 
        /
        (np.sqrt((df["ap_pt"]**2 + df["ap_pz"]**2) *
                 (df["recoil_pt"]**2 + df["recoil_pz"]**2))
        ))

materials = ["copper", "lead", "oxygen", "silicon", "tungsten"]
masses = [0.005, 0.01, 0.05, 0.1]
var_specs = [
    ('recoil_energy_frac', {'minX' : 0.0, 'maxX' : 1.0, 'cumulative' : True}),
    ('ap_energy_frac', {'minX' : 0.0, 'maxX' : 1.0, 'cumulative' : True}),
    ('recoil_theta', {'minX' : 0.0, 'maxX' : math.pi}),
    ('ap_theta', {'minX' : 0.0, 'maxX' : math.pi}),
    #('recoil_phi', {'minX' : -math.pi, 'maxX' : math.pi}), # uninteresting
    #('ap_phi', {'minX' : -math.pi, 'maxX' : math.pi}), # uninteresting
    ('delta_phi', {'minX' : 0.0, 'maxX' : 2.0 * math.pi}),
    ('angle_recoil_ap', {'minX' : 0.0, 'maxX' : math.pi})
]
energy_pairs = [
    (1.0, [1.1, 1.2, 1.5, 2.0, 3.0, 4.0]),
    (2.0, [2.2, 2.4, 2.5, 2.6, 2.8, 3.0, 4.0]),
    #(3.0, [3.3, 3.6, 3.9, 4.0, 5.0, 6.0]),
    (4.0, [4.2, 4.4, 4.8, 6.0, 7.0, 8.0]),
    #(5.0, [5.5, 6.0, 7.0, 8.0]),
    (6.0, [6.06, 6.12, 6.18, 6.24, 6.3, 6.6, 6.9, 7.0, 7.5, 8.0])#,
    #(7.0, [7.5, 8.0])
]

theDict = make_scaling_hists_dict(
    "/home/ram2aq/ldmx/data",
    materials,
    masses,
    var_specs,
    energy_pairs
)

outfile = "/home/ram2aq/ldmx/data/scaling_hists.pkl"
with open(outfile, 'wb') as fp:
    pickle.dump(theDict, fp)