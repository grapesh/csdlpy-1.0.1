#!/bin/bash

# Load Python 2.7.13
module use /usrx/local/dev/modulefiles
module load python/2.7.13

# Specify a path to folder with CSDLPY repository:
export toolkitPath="/gpfs/hps/nos/noscrub/Sergey.Vinogradov/csdlpy-1.0.1"

# Specify a path to the test code (test_csdlpy.py):
export appPath="/gpfs/hps/nos/noscrub/Sergey.Vinogradov/csdlpy-1.0.1/csdlpy/tests"

# Specify a path to log file
export logFile="/gpfs/hps/nos/noscrub/Sergey.Vinogradov/csdlpy-1.0.1/csdlpy/tests/test.log"

python -W ignore ${appPath}/test_csdlpy.py -t $toolkitPath > $logFile




