import os

run_script="scripts/run_g4db_scale.sh"
def run_for_params(run_number, material, mass, scale_from_energy, scale_to_energy):
    command = "{run_script} {run_number} {material} {mass} {scale_from_energy} {scale_to_energy}".format(
        run_script=run_script,
        run_number=run_number,
        material=material,
        mass=mass,
        scale_from_energy=scale_from_energy,
        scale_to_energy=scale_to_energy
    )
    print(command)
    return os.system(command)

materials = ["lead", "oxygen"] #["tungsten", "silicon", "copper", "lead", "oxygen"]
masses = ["0.005", "0.01", "0.05", "0.1"]
energies = [  
             (["1.1", "1.2", "1.5", "2.0", "3.0", "4.0"], "1.0"),
             (["2.2", "2.4", "2.5", "2.6", "2.8", "3.0", "4.0"], "2.0"),
             (["3.3", "3.6", "3.9", "4.0", "5.0", "6.0"], "3.0"),
             (["4.2", "4.4", "4.8", "6.0", "7.0", "8.0"], "4.0"),
             (["5.5", "6.0", "7.0", "8.0"], "5.0"),
             (["6.06", "6.12", "6.18", "6.24", "6.3", "6.6", "6.9", "7.0",
               "7.5", "8.0"], "6.0"),
             (["7.5", "8.0"], "7.0")
            ]

run_number = 4000

continue_on_fail = False

for material in materials:
    for mass in masses:
        for energy_pair in energies:
            energy_to = energy_pair[1]
            for energy_from in energy_pair[0]:
                retval = run_for_params(run_number, material, mass, energy_from, energy_to)
                if retval != 0 and not continue_on_fail:
                    exit()
