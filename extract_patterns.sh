#!/bin/bash
#SBATCH --partition=devel
#SBATCH --nodes=1
#SBATCH --job-name=patterns


vpkg_require papi/5.4.3
vpkg_require python/3.7.4
vpkg_require gcc/11.2.0
vpkg_require jdk/17.0.9
vpkg_require pcaot

python3 patterns_extractor.py patterns_extractor_list_all.txt 0