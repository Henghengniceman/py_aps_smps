# py_aps_smps
This project deals with the import, analysis, plotting and export of size distributions measured with Aerodynamic Particle Sizers (APS) and Scanning Mobility Particle Sizers (SMPS).


## Setup

### a) Download/clone the project to your computer.

Cloning via git is recommended, so you can keep the code up to date easily.

```shell
$ git clone https://git.scc.kit.edu/agm-software-tools/size-distributions/py_aps_smps.git
$ cd py_aps_smps
```

### b) Setup a fresh python environment

Either via pip (recommended)

```shell
$ python -m venv VE_SizeDist
$ source VE_SizeDist/bin/activate
(VE_SizeDist) $ pip install --upgrade pip
(VE_SizeDist) $ pip install -r requirements.txt
```

or via conda

```shell
$ conda env create -f environment.yml
$ conda activate VE_SizeDist
(VE_SizeDist) $ ...
```

or manually install the python modules `numpy scipy pandas matplotlib sqlalchemy mariadb`.

The code was tested with python 3.7 and 3.10., so it probably works with all intermediate versions.


## How to use
The main user frontend for size distribution analysis is the function `analyze_sd()`.

Start your python interpreter within the new python environment with the projects base directory as current working directory.

```python
import py_aps_smps
py_aps_smps.analyze_sd(campaign, exp_num, density, shapefactor)
```

These first four keywords must be defined.
Several other optional keywords are available.
- The function takes many other keyword arguments such as options to (de-)activate merging of overlaps, interpolation of gaps, (partial) smoothing and/or fitting.
- for (bi-)lognormal fitting you can pass custom start parameters
- For further details have a look at the functions docstring, e.g. by typing in python
```python
help(py_aps_smps.analyze_sd)
```


## Contributing

For information about how to contribute to this project, please see the `CONTRIBUTING.md` file.

### Acknowledgments
The basic data processing is based on IDL scripts originally written by Ottmar Möhler and maintained by Romy Fößig at KIT-IMK-AAF.

### Contributors in this python project
* Tobias Schorr
* Barbara Bertozzi


## License
Copyright (C) 2021-2022 KIT/IMK-AAF (Karlsruhe Institute of Technology, Institute of Meteorology and Climate Research, Atmospheric Aerosol Research).

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

A copy of the GNU General Public License can be found in the LICENSE file that comes along with this program, or see http://www.gnu.org/licenses/.
