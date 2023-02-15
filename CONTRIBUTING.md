# CONTRIBUTING
This document provides information about how to contribute to this project.

## Code style and structure
The style and structure of this code should follow
- [PEP8](https://www.python.org/dev/peps/pep-0008/) (Style Guide for Python Code)
- [PEP20](https://www.python.org/dev/peps/pep-0020/) (The Zen of Python)
- [NumPy docstring guide](https://numpydoc.readthedocs.io/en/latest/format.html), [NumPy docstring style example](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_numpy.html)

## Creating environment files

The files `requirements.txt.` and `environment.yml` are provided to set up a python environment with all dependencies using pip or conda, respecively.

The specific dependency versions are not pinned, yet.
Once the project runs into dependency problems, consider to remove the options supressing version pinning.

### With pip: creating the requirements.txt
Use pipreqs to generate the requirements.txt file.
Run the following commands from the projects base folder.

```shell
$ pip install pipreqs
$ pipreqs ./py_aps_smps/ --savepath ./requirements.txt --mode no-pin
```

### With conda: creating the environment.yml
Create a new clean conda environment.
Install all dependencies which are provided by conda (pip numpy scipy pandas matplotlib sqlalchemy).
Additional dependencies (mariadb) have to be installed via pip.

```shell
(base) $ conda create -n VE_SizeDist --no-default-packages python=3.10 pip numpy scipy pandas matplotlib sqlalchemy
(base) $ conda activate VE_SizeDist
(VE_SizeDist) $ pip install <all additional packages not provided by conda>
(VE_SizeDist) $ conda env export --no-builds --from-history | grep -v "^prefix: " > environment.yml
```

Currently, `conda env export` with `--from-history` misses the feature to include pip dependencies (see [issue](https://github.com/conda/conda/issues/9628)).
As long as this is not solved, you have to manually add the missing pip dependencies:

```yml
  - ...
  - CONDA_DEP_Y
  - CONDA_DEP_Z
  - pip:
    - PIP_DEP_A
    - PIP_DEP_B
```
