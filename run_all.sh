#!/bin/bash
#SBATCH --partition=devel
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --job-name=run-all-job
###SBATCH --time=07:00:00

vpkg_rollback
vpkg_require jdk/17.0.9
# vpkg_require papi/5.4.3
# vpkg_require python/3.7.4
# vpkg_require gcc/11.2.0
vpkg_require pcaot

python3 src/run_all.py planning/experiment_plans.csv