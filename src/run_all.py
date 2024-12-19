from models.experiments import Experiment
from preparation.preparation import prepare_llm_experiment, prepare_tiling_experiment
from compilation.compiler import compile_experiment
from experiments.experimenter import run_experiment as run_experimenter
import sys
from typing import Dict

def _run_baseline(experiment: Experiment):
    runnable_experiment = compile_experiment(experiment)
    run_experimenter(runnable_experiment)
    pass

def _run_cetus_experiment(aot, parameters, experiment: Experiment):
    pass

def _run_llm_experiments(aot, parameters: Dict[str], experiment: Experiment):
    total_compilable_experiments = []
    
    for prompt_name, prompt_path in parameters.items():
        compilable_experiments = prepare_llm_experiment(aot, prompt_name, prompt_path, experiment)
        total_compilable_experiments.append()
    
    
    return total_compilable_experiments

def run_experiment(aot, parameters, experiment: Experiment):
    
    
    compilable_experiments = []
    aot_params = parameters[aot]
    
    if(aot == 'mock' or aot == 'gpt-4' or aot == 'llama'):
        _run_llm_experiments(aot, aot_params, experiment)
    
    if aot == 'cetus-tiling':
        _run_llm_experiments(aot, aot_params, experiment)

        
    for compilable_experiment in compilable_experiments:
        runnable_experiment = compile_experiment(compilable_experiment)
        run_experimenter(runnable_experiment)
    pass


if __name__ == "__main__":
    
    experiment_plans_file_path_from_args = "experiment_plans.csv"
    if len(sys.argv) > 1:
        experiment_plans_file_path_from_args = sys.argv[1]

    with open(experiment_plans_file_path_from_args, "r") as file:
        source_code_infos = [line.split(";")
                             for line in file.read().splitlines()[1:]]

    aots = ['mock','cetus-tiling', 'cetus']
    # prompt_approaches = []
    parameters = {
        "mock":{
            "naive-tiler": "/mnt/d/workspace/ud-masters/research-ideas/LLM/use-cases/prompts/naive-tiler",
            "augmented-naive-tiler": "/mnt/d/workspace/ud-masters/research-ideas/LLM/use-cases/prompts/augmented-naive-tiler",
            "parallel-aware-tiler": "/mnt/d/workspace/ud-masters/research-ideas/LLM/use-cases/prompts/parallel-aware-tiler"
        },
        "gpt-4": {
            "naive-tiler": "/mnt/d/workspace/ud-masters/research-ideas/LLM/use-cases/prompts/naive-tiler",
            "augmented-naive-tiler": "/mnt/d/workspace/ud-masters/research-ideas/LLM/use-cases/prompts/augmented-naive-tiler",
            "parallel-aware-tiler": "/mnt/d/workspace/ud-masters/research-ideas/LLM/use-cases/prompts/parallel-aware-tiler"
        },
        "cetus-tiling": {
            "tiling-level": "2",
        },
        "cetus":{
            
        }
        
    }

    for benchmark_type, trials, dataset, benchmark_folder, kernel_folder, routine_name, source_placeholder, binary_file in source_code_infos:
        baseline_comp_flags = ["SERIAL"]
        experiment = Experiment(benchmark_type, trials, dataset, benchmark_folder.strip(), kernel_folder.strip(
        ), routine_name.strip(), binary_file.strip(), baseline_comp_flags, source_placeholder.strip())
        _run_baseline(experiment)
        for aot in aots:
            run_experiment(aot, parameters, experiment)
