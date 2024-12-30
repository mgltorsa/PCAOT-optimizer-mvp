#!/bin/bash
#SBATCH --partition=devel
#SBATCH --nodes=1
#SBATCH --job-name=run-all-job
#SBATCH --time=07:00:00

vpkg_require papi/5.4.3
vpkg_require python/3.7.4
vpkg_require gcc/11.2.0

python3 src/run_all.py