# import main functions as aliases
from py_aps_smps.main.analyze_sd import analyze_sd

# import main fuctions with full path
import py_aps_smps.main
import py_aps_smps.main.analyze_sd


# import lib with all subfolder structures
import py_aps_smps.lib

import py_aps_smps.lib.io
import py_aps_smps.lib.io.ambient_conditions
import py_aps_smps.lib.io.sd
import py_aps_smps.lib.io.sql

import py_aps_smps.lib.sd_processing
import py_aps_smps.lib.sd_processing.content
import py_aps_smps.lib.sd_processing.distributions
import py_aps_smps.lib.sd_processing.structure

# import mariadb, so pipreqs finds it as dependency
import mariadb
