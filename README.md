# CHALET
Charging locations for Electric Trucks (CHALET) is an optimization tool for the strategic planning of electric heavy-duty truck charging infrastructure.
It identifies an optimal subset of locations among given candidates to place charging stations such that the provided origin‐destination (OD) pairs can be served by electric vehicles (EVs).
The locations are selected to maximize the eligibility of OD pairs for electrification and minimize the total cost for opening charging stations. Eligibility of OD pairs is subject to an adjustable transit time constraint that limits the admissible time overhead spent on detours and charging.

CHALET supports the following features:
* It can be used to maximize the number of OD pairs eligible for EVs given a charging station budget or to minimize the number of charging stations required for maximum possible eligibility of the specified OD pairs.
* The user can assign preferences to certain OD pairs or candidate locations by specifying demands and/or costs, respectively.
* The solution is controlled by transit time constraints, vehicle properties (battery/range), charger power output and further input parameters.

### Model
CHALET solves an integer programming formulation derived from a graph-based abstraction of the problem.
The implementation is related to the mathematical formulation introduced by the academic work [1].
In contrast to [1], CHALET introduces a transit time constraint that takes into account charging time and legally required truck driver breaks in Europe (45 mins every 4.5 hours), and implements modified separation routines for solving the integer program.

## Installation Requirements
The main requirements are:
*	Python (>=3.6, <=3.9)
*	Pip (>=19.3)
*	Xpress (8.14.4)

A complete list of package dependencies can be found in ``setup.cfg``.

The installation should be done in a [Python virtual environment](https://docs.python.org/3/library/venv.html).
This [user guide](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/) can help with that.


#### Xpress
CHALET depends on [FICO Xpress Optimization](https://www.fico.com/en/products/fico-xpress-optimization) to solve the integer program.
The free community license that comes with the installation of Xpress restricts the problem sizes that can be solved.
For full functionality, it may be necessary to provide an unrestricted license, which can be found in the official [Xpress licensing options](https://www.fico.com/en/fico-xpress-trial-and-licensing-options).
It should be noted that, as of Feb 2023, Xpress does not support ARM CPUs (e.g. Mac with M1 chip).
A possible remedy is to use Python in an Intel-64 emulation mode (executable python3-intel64 available from Python 3.9.5 onwards).

## Installation

### Repository Setup
To install the code, the repository needs to be cloned through the following command:

```shell
git clone git@github.com:amzn/chalet-charging-location-for-electric-trucks.git
cd chalet-charging-location-for-electric-trucks
```
A virtual environment is created in a folder `venv` by running:
```shell
python -m venv venv
```
Subsequent commands should be run after activating the environment:
```shell
source venv/bin/activate
```
The pip install commands installs requirements defined in `setup.cfg` in the `install_requires` section.
The `[dev]` and `[testing]` options additionally install requirements defined in the `[options.extras_require]` section.
```shell
python -m pip install -e .[dev]
python -m pip install -e .[testing]
```
If zsh is used, square brackets need to be omitted or quotes inserted:
```shell
python -m pip install -e ".[dev,testing]"
```

### Input Setup
CHALET is run by the following command:
```shell
chalet
```
By default, CHALET expects input data in a folder called `data/` and writes output data into `output/` inside the root directory.
Different input/output file paths can be specified via:
```shell
chalet -i PATH_TO_LOCAL_INPUT_FILES -o PATH_TO_LOCAL_OUTPUT_FILES
```

#### Required Inputs
To setup the inputs for CHALET, the following four files are needed:
*	`arcs.csv`: Defines arcs between any two nodes in a network graph. Arcs represent fastest road connections and have associated transit times and distances.
*	`nodes.csv`: Nodes of the network graph representing either sites of origin-destination pairs or (potential) charging station locations. Charging stations can be assigned with optional setup costs.
*	`od_pairs.csv`: Origin-destination pairs of sites with optional demands.
*	`parameters.json`: Parameters to control the optimization algorithm.

The definitions of column fields and data types can be found in:  ``src/chalet/model/input/``

A small example test instance can be found in: `src/tests/end2end/input_data/`

### Testing Setup
The code can be tested using the below command:
```shell
tox
```
[Tox](https://tox.wiki/en/latest/user_guide.html) runs tests, linters, and checks for formatting issues and line coverage.
The following formatters and linters are used:
*	isort - For checking order of import statements.
*	flake8 - For checking code style guidelines. (_Note:_ flake8 does not reformat the code by itself and requires the changes to be made manually).
*	black - For reformatting the code according to the settings of the black formatter.
*	mypy - For type checking. Any errors have to be manually corrected, similar to flake8.

For building the package and generating wheel and source distributions:
```shell
tox -e build
```
For cleaning up build and virtual env files and folders:
```shell
tox -e clean
```
To apply black and isort formatters:
```shell
tox -e format
```
## References
[1] Arslan et al. A branch-and-cut algorithm for the alternative fuel refueling station location problem with routing. Transportation Science 53(4):1107–1125, 2019
## License
This project is licensed under the Apache-2.0 License.
