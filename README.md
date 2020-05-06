# University of York Computer Science Project 2020
This repo contains the simulator implementation and results for my project "Intelligent Road Self-Layout Management".

## Installing SUMO
The guidance for installing SUMO can be found [in their documentation](https://sumo.dlr.de/docs/Installing.html), with further information being available throughout their other documentation including [tutorials](https://sumo.dlr.de/docs/Tutorials.html) and [TraCI](https://sumo.dlr.de/docs/TraCI.html).

## SUMO Simulator Files
In this folder, all the files necessary to run the SUMO simulations done in this project.
`road.py` can be simply executed to perform an example simulation, with a period of 14 and a threshold of 0.3.
To repeat the experiments done in the project, use the `run_experiment` functions.

## Results
The results folders, labelled  1, 2, 3, Control and Baseline, represent the simulator outputs from the experiments done in as part of the project.
These outputs consist of:
- `consolesummary.*.txt` - the output of variables kept track of by the python control script.
- `summary.*.xml` - the simulator's summary file output.
- `tripinfo.*.xml` - information for each vehicle in the simulation, including the time loss.

## Python Scripts
### `dataConverting`
This script was used to convert the road traffic data taken from the WebTRIS system to flow definitions usable in SUMO.

### `xmlRead`
This script was used to extract the time loss information from the `tripinfo.*.xml` files.

## Road Data
With `Daily0fixed.csv` and `Daily1fixed.csv` being the Southbound and Northbound A556 Road Data files respectively, the other `.txt` files are the outputs from using the `xmlRead` script. 
