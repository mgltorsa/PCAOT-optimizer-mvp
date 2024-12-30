import subprocess
import os
import os
from models.experiments import Experiment, CompilableExperiment
from utils.checkpointing import save_checkpoint, load_checkpoint, exists_checkpoint, collect_llms_checkpoints
from typing import List, Dict
import json

def prepare_cetus_baseline(experiment: Experiment) -> CompilableExperiment:
    # cetus default parameters
    # -induction=3, -privatize=2, -reduction=2, -ddt=2, -parallelize-loops=1, 
    # -ompGen=1, -alias=1, -range=1, -teliminate-branch=1, -profitable-omp=1

    # deactive cetus default parameters
    cetus_parameters = {
        "induction": 0,
        "privatize": 0,
        "reduction": 0,
        "ddt": 0,
        "parallelize-loops": 0,
        "ompGen": 0,
        "alias": 0,
        "range": 0,
        "teliminate-branch": 0,
        "profitable-omp": 0,
        "profile-loops": 2,
        "profile-instruments": 1,
    }

    return prepare_cetus_experiment("baseline", experiment, cetus_parameters, profiler_command='pcaot_wsl')[0]

def prepare_cetus_experiment(pass_name, experiment: Experiment, cetus_parameters: Dict[str,str], profiler_command: str='cetus_wsl') -> List[Experiment]:
    benchmark = experiment.benchmark_folder
    kernel = experiment.kernel_folder
    routine_name = experiment.routine_name

    
    
    parent_experiment_path = f"{routine_name}/{pass_name}"
    outdir = f"{benchmark}/{kernel}/{parent_experiment_path}"
    
    os.makedirs(outdir, exist_ok=True)

    opts = []
    
    for key, value in cetus_parameters.items():
        opts.append(f"-{key}={value}")
    
    opts_str = " ".join(opts)
    # Build the command dynamically
    options = f"-verbosity=3 -outdir={outdir} {opts_str}"
    
    file_path = f"{benchmark}/{kernel}/{routine_name}.c"
    command = f"echo $CPATH && {profiler_command} {options} {file_path}"

    if exists_checkpoint(benchmark, kernel, 'preparation', [pass_name]):
        experiment = load_checkpoint(benchmark, kernel, 'preparation', [pass_name])
        return [experiment]

        
    cpath = experiment.get_c_path()
    
    os.environ["CPATH"] = f"{cpath}"
    
    process = subprocess.Popen(command, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    process.communicate()  # This waits for the process to finish and prints the output

    
    compilation_flags = [pass_name] if pass_name != "baseline" else ['SERIAL']

    compilable_experiment = CompilableExperiment(experiment.benchmark_type, experiment.trials, experiment.dataset, experiment.benchmark_folder,
                                            experiment.kernel_folder, parent_experiment_path, experiment.routine_name, experiment.binary_file, compilation_flags, experiment.source_placeholder)
    
    save_checkpoint(compilable_experiment, 'preparation')
    
    return [compilable_experiment]
    

def prepare_llm_experiment(llm, prompt_name, prompt_path, experiment: Experiment, parameters={'temperature':0.4, "top_p":0.1}) -> List[Experiment]:
    # Define the options dynamically
    benchmark = experiment.benchmark_folder
    kernel = experiment.kernel_folder
    routine_name = experiment.routine_name
    trials = experiment.trials
    
    parent_experiment_path = f"{routine_name}/{prompt_name}"
    outdir = f"{benchmark}/{kernel}/{parent_experiment_path}"
    
    
    os.makedirs(outdir, exist_ok=True)    

    # Build the command dynamically
    options = f"-verbosity=3 -aot=0 -llm-opt={llm} -llm-prompts={prompt_name} -llm-trials={trials} -outdir={outdir} -llm-opt-temp={parameters['temperature']} -llm-opt-top-p={parameters['top_p']}"
    
    parent_file_path = f"{benchmark}/{kernel}"
    filename = f"{routine_name}.c"
    
    output_file = f"{outdir}/preparation-{llm}.log"
    error_file = f"{outdir}/preparation-{llm}.err"
    
    commands = [
        "echo \"**** CPATH ****\n\""
        "echo $CPATH",
        str(f"cd {parent_file_path}"),
        "echo \"**** STARTING PCAOT ****\n\"",
        str(f"pcaot_wsl {options} {filename} >> {output_file} 2>> {error_file}")
    ]
    


    command =  " && ".join(commands)
    print("COMMAND: ",command)
    
    cpath = experiment.get_c_path()
    
    os.environ["CPATH"] = f"{cpath}"
    os.environ["OPENAI_API"] = ""
    
    os.environ["PCAOT_PROMPT"] = prompt_path
    os.environ["HF_TOKEN"] = ""
    os.environ["HF_URL"] = ""
    os.environ["HF_URL"] = ""

    checkpoints = collect_llms_checkpoints(llm, prompt_name, benchmark, kernel, 'preparation')
    if len(checkpoints) > 0:
        return checkpoints

    try:
        # Execute the command
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        process.communicate()
        
        compilable_experiments = []    
        
        with open(f"{outdir}/metadata.json", "r") as file:
            metadata_json = json.load(file)
            parent_name_flag = metadata_json["parent_name"]
            loop_flags = metadata_json["versions"]
            for loop_flag in loop_flags:
                if loop_flag == None or loop_flag == "":
                    continue

                compilation_flags = [parent_name_flag, loop_flag]
                
                compilable_experiment = CompilableExperiment(experiment.benchmark_type, experiment.trials, experiment.dataset, experiment.benchmark_folder,
                                            experiment.kernel_folder, parent_experiment_path, experiment.routine_name, experiment.binary_file, compilation_flags, experiment.source_placeholder)
                
                save_checkpoint(compilable_experiment, 'preparation')
                compilable_experiments.append(compilable_experiment)
            
            
        if len(compilable_experiments) == 0:
            raise Exception("Compilable experiments not found")

        return compilable_experiments
    except Exception as e:
        print("ERROR: ", e)
        #TODO SAVE TO MONGO
        return []


