import subprocess
import os
import sys
import asyncio
import os
from models.experiments import Experiment
from typing import List
import json

def prepare_experiment(llm, prompt_name, prompt_path, experiment: Experiment, parameters={'temperature':0.4, "top_p":0.1}) -> List[Experiment]:
    # Define the options dynamically
    benchmark = experiment.benchmark_folder
    kernel = experiment.kernel_folder
    routine_name = experiment.routine_name
    trials = experiment.trials
    
    outdir = f"{benchmark}/{kernel}/{routine_name}/{prompt_name}"
    
    
    os.makedirs(outdir, exist_ok=True)    

    # Build the command dynamically
    options = f"-verbosity=3 -aot=0 -llm-opt={llm} -llm-prompts={prompt_name} -llm-trials={trials} -outdir={outdir} -llm-opt-temp={parameters['temperature']} -llm-opt-top-p={parameters['top_p']}"
    
    file_path = f"{benchmark}/{kernel}/{routine_name}.c"
    command = f"echo $CPATH && pcaot_wsl {options} {file_path}"

    print("COMMAND: ", command)
    
    cpath = experiment.get_c_path()
    
    os.environ["CPATH"] = f"{cpath}"
    os.environ["OPENAI_API"] = ""
    
    os.environ["PCAOT_PROMPT"] = prompt_path
    os.environ["HF_TOKEN"] = ""
    os.environ["HF_URL"] = ""
    os.environ["HF_URL"] = ""

    # Execute the command
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    process.communicate()  # This waits for the process to finish and prints the output
    output = process.stdout
    errors = process.stderr
    
    
    compilable_experiments = []    
    
    with open(f"{outdir}/metadata.json", "w") as file:
        metadata_json = json.load(file)
        parent_name_flag = metadata_json["parent_name"]
        loop_flags = metadata_json["versions"]
        for loop_flag in loop_flags:
            compilation_flags = [parent_name_flag, loop_flag]
            compilable_experiment = Experiment(experiment.benchmark_type, experiment.trials, experiment.dataset, experiment.benchmark_folder,
                                           experiment.kernel_folder, experiment.routine_name, experiment.binary_file, compilation_flags, experiment.source_placeholder)
            compilable_experiments.append(compilable_experiment)
        
        
    if len(compilable_experiments) == 0:
        raise Exception("Compilable experiments not found")

        
    
    return compilable_experiments
    
    

async def prepare_experiment_async(llms_opt, prompt_name, prompt_path, benchmark, subroutine, cpath, file_path,parameters={'temperature':0.4}):
    try:
        print("RUNNING EXPERIMENT")
        await prepare_experiment(llms_opt, prompt_name, prompt_path, benchmark, subroutine, cpath, file_path, parameters)
    except Exception as e:  
        print("FROM_ASYNC",e)
    
    
async def main():
    if len(sys.argv) != 2:
        print("Remember Usage: python script.py llm-opts? llm-prompts?")
        
    llm_opt = "gpt-4"
    
    prompts = {
        "naive-tiler": "/mnt/d/workspace/ud-masters/research-ideas/LLM/use-cases/prompts/naive-tiler",
        "augmented-naive-tiler":"/mnt/d/workspace/ud-masters/research-ideas/LLM/use-cases/prompts/augmented-naive-tiler",
        "parallel-aware-tiler":"/mnt/d/workspace/ud-masters/research-ideas/LLM/use-cases/prompts/parallel-aware-tiler"
    }
    
    if len(sys.argv) > 1:
        llm_opt = sys.argv[1]
        
        
    print("LLMS: "+llm_opt)
    print("PROMPTS: "+prompts)
    
    with open("source_codes.txt", "r") as file:
        source_code_infos = [line.split(",") for line in file.read().splitlines()]
    
    # temperatures = [0.1, 0.4, 0.7]
    temperatures = [0.2]
    topPs=[0.1]
    tasks = []
    # for i in range(3):
    for benchmark, subroutine, cpath, file_path in source_code_infos:
        print(f"Processing {benchmark}/{subroutine}:")
        for temperature in temperatures:
            for top_p in topPs:
                parameters = {'temperature': temperature, "top_p":top_p}
                for prompt_name, prompt_path in prompts.items():
                    task = asyncio.create_task(prepare_experiment_async(llm_opt, prompt_name, prompt_path, benchmark, subroutine, cpath, file_path.strip(), parameters))
                    tasks.append(task)
            
    await asyncio.gather(*tasks)

asyncio.run(main())