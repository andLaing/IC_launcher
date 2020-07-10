# IC_launcher
Launcher for simulated NEXT detectors processing on Odyssey

# Setup
Move to this folder and source setup.sh

# Running a city over a run
Edit or make a new launcher configuration based on the examples in launcher_conf/

`python launch.py <name_of_launcher_conf>`

# launcher config arguments

REQUIRED:
city       = String, name of the city to be launched
conf       = String, path and name to configuration template for the city.
script     = String, name of the job launching script used as template. script_template.sh recommended
detector   = String, Detector folder name
generator  = String, name of the generator folder: kr83m, 0nubb, etc
date       = String, date for the folder where the run was generated

ADDITIONAL OPTIONAL ARGUMENT

other_input = String, alternate input folder
