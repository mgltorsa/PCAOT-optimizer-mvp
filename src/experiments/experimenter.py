import subprocess
from models.experiments import RunnableExperiment

def run_experiment(experiment: RunnableExperiment):
    
    compilation_flags = experiment.compilation_flags
    benchmark_folder = experiment.benchmark_folder
    kernel_folder = experiment.kernel_folder
    routine_folder = experiment.routine_name
    binary_file = experiment.binary_file
    
    if(len(compilation_flags)>1):
        no_serial_cflags = compilation_flags[1:]
        new_binary_folder="".join(no_serial_cflags)
    else:
        new_binary_folder="_".join(compilation_flags)
        
    new_binary_folder =new_binary_folder.replace(":","_")
    
    cores=4
    if len(compilation_flags)>0 and "SERIAL" in compilation_flags[0] and len(compilation_flags)==1:
        cores=1

    compilation_folder = f"{benchmark_folder}/bin/{kernel_folder}/"
    
    if experiment.parent_preparation_folder is not None:
        compilation_folder += f"{experiment.parent_preparation_folder}/{new_binary_folder}"
    else:
        compilation_folder += f"{new_binary_folder}"
        
        
    runtime_wrapper_executable = f"runtime_wrapper.py"
    executable = f"{compilation_folder}/{binary_file}"
    executable_args = "-args=" + " -args=".join(experiment.compilation_flags)

    experiment_job_name = f"{kernel_folder}_{routine_folder}_{new_binary_folder}_job"
    
    sbatch_content = f"""#!/bin/bash
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --tasks-per-node=1
#SBATCH --ntasks=1
#SBATCH --sockets-per-node=1
#SBATCH --array=1-3
#SBATCH --open-mode=truncate
#SBATCH --cores-per-socket={cores}
#SBATCH --cpus-per-task={cores}
#SBATCH --exclusive
#SBATCH --output={compilation_folder}/results_%a.txt
#SBATCH --error={compilation_folder}/errors_%a.txt
#SBATCH --job-name={experiment_job_name}
#SBATCH --constraint='Gen2'
#SBATCH --time=07:00:00

export OMP_NUM_THREADS=4

cd {compilation_folder}
{runtime_wrapper_executable} {executable} {executable_args}
"""

    
    script_file = f"{compilation_folder}/jobs.sh"
    with open(script_file, 'w') as f:
        f.write(sbatch_content)
    
    exec_sbatch(script_file)


def exec_sbatch(script_file):
    sbatch_command = f"sbatch {script_file}"
    print("SBATCH COMMAND: ", sbatch_command)
    process = subprocess.Popen(sbatch_command, shell=True)
    process.communicate()  # This waits for the process to finish and prints the output
