import subprocess
import os
import os
from models.experiments import Experiment, CompilableExperiment
from typing import List, Dict
import json

def prepare_cetus_experiment(pass_name, experiment: Experiment, cetus_parameters: Dict[str,str]) -> List[Experiment]:
    benchmark = experiment.benchmark_folder
    kernel = experiment.kernel_folder
    routine_name = experiment.routine_name
    
    parent_experiment_path = f"{routine_name}/{pass_name}"
    outdir = f"{benchmark}/{kernel}/{parent_experiment_path}"
    
    
    opts = []
    
    for key, value in cetus_parameters.items():
        opts.append(f"-{key}={value}")
    
    opts_str = " ".join(opts)
    # Build the command dynamically
    options = f"-verbosity=3 -paw-tiling -outdir={outdir} {opts_str}"
    
    file_path = f"{benchmark}/{kernel}/{routine_name}.c"
    command = f"echo $CPATH && cetus_wsl {options} {file_path}"
    
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    process.communicate()  # This waits for the process to finish and prints the output
    output = process.stdout
    errors = process.stderr
    
    compilable_experiment = CompilableExperiment(experiment.benchmark_type, experiment.trials, experiment.dataset, experiment.benchmark_folder,
                                            experiment.kernel_folder, parent_experiment_path, experiment.routine_name, experiment.binary_file, [], experiment.source_placeholder)
    
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
                compilable_experiments.append(compilable_experiment)
            
            
        if len(compilable_experiments) == 0:
            raise Exception("Compilable experiments not found")

        return compilable_experiments
    except Exception as e:
        print("ERROR: ", e)
        #TODO SAVE TO MONGO
        return []
