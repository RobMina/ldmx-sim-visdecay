import sys
import os
import argparse

usage = "ldmx fire %s"%(sys.argv[0])
parser = argparse.ArgumentParser(usage,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("db_event_lib",type=str,default=None,
        help="the dark brem event library to use for the model.")
parser.add_argument("n_events",type=int,default=20000,
        help="number of events to simulate.")
arg = parser.parse_args()

# We need the ldmx configuration package to construct the processor objects
from LDMX.Framework import ldmxcfg

p = ldmxcfg.Process('eat_vis')
p.maxTriesPerEvent = 10000
p.maxEvents = arg.n_events

# Get A' mass from the dark brem library name
lib_parameters = os.path.splitext(

            os.path.basename(arg.db_event_lib)
 
        )[0].split('_')
ap_mass = float(lib_parameters[lib_parameters.index('mA')+1])*1000.
run_num = int(lib_parameters[lib_parameters.index('run')+1])

parameters = [
    'category', 'signal',
    'Nevents', '{n_events}'.format(n_events=arg.n_events),
    'MaxTries', '10k',
    'mAMeV', f'{int(ap_mass):04d}',
    'epsilon', '0.01',
    'minApE', '4000',
    'minPrimEatEcal', '7000',
    'run', f'{run_num:04d}'
]
p.outputFiles = [ '_'.join(parameters)+'.root' ]
p.run = run_num

# set up simulation
from LDMX.Biasing import eat
from LDMX.SimCore import generators
sim = eat.dark_brem(
    ap_mass,
    arg.db_event_lib,
    'ldmx-det-v14-8gev',
    generators.single_8gev_e_upstream_tagger(),
    scale_APrime = True,
    #ap_tau = 1.0E-12,
    dist_decay_min = 0.0,
    dist_decay_max = 4000.0,
    decay_mode = 'flat_decay'
)

import LDMX.Ecal.EcalGeometry
import LDMX.Ecal.ecal_hardcoded_conditions
import LDMX.Ecal.digi as ecal_digi
import LDMX.Ecal.vetos as ecal_vetos

import LDMX.Hcal.HcalGeometry
import LDMX.Hcal.hcal_hardcoded_conditions
import LDMX.Hcal.digi as hcal_digi

from LDMX.TrigScint.trigScint import TrigScintDigiProducer
from LDMX.TrigScint.trigScint import TrigScintClusterProducer
from LDMX.TrigScint.trigScint import trigScintTrack

import LDMX.Recon.simpleTrigger as trig
import LDMX.Recon.electronCounter as count

#from LDMX.Analysis import eat

counter = count.ElectronCounter(1, 'counter')
counter.input_pass_name = 'eat_vis'
counter.input_collection = 'TriggerPadTracksY'

trigger = trig.TriggerProcessor('trigger', 8000.)
trigger.beamEnergy = 8000.
trigger.thresholds = [ 3160. ]

p.sequence = [
        sim,
        ecal_digi.EcalDigiProducer(),
        ecal_digi.EcalRecProducer(),
        ecal_vetos.EcalVetoProcessor(),
        hcal_digi.HcalDigiProducer(),
        hcal_digi.HcalRecProducer(),
        TrigScintDigiProducer.pad1(),
        TrigScintDigiProducer.pad2(),
        TrigScintDigiProducer.pad3(),
        TrigScintClusterProducer.pad1(),
        TrigScintClusterProducer.pad2(),
        TrigScintClusterProducer.pad3(),
        trigScintTrack,
        counter,
        trigger,
        #eat.PrimaryEcalFrontFaceKinematics(),
        #eat.PullNuclearEnergy(),
        #eat.DarkBremKinematics(),
        #eat.HcalVetoVars()
        ]
