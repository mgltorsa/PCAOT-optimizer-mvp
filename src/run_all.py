from models.experiments import Experiment, CompilableExperiment, RunnableExperiment
from preparation.preparation import prepare_llm_experiment, prepare_cetus_experiment, prepare_cetus_baseline
from compilation.compiler import compile_experiment as internal_compile_experiment
from experiments.experimenter import run_experiment as internal_run_experiment
import sys
from typing import Dict, List

available_llms = ['mock', 'gpt-4', 'llama']
available_compilers = ['cetus', 'cetus-tiling']

def _run_baseline(experiment: Experiment):
    compilable_experiment = prepare_cetus_baseline(experiment)
    # compilable_experiment = CompilableExperiment(experiment.benchmark_type, experiment.trials, 
    #                                              experiment.dataset, experiment.benchmark_folder, 
    #                                              experiment.kernel_folder, experiment.routine_name, experiment.routine_name, 
    #                                              experiment.binary_file, experiment.compilation_flags, 
    #                                              experiment.source_placeholder)
    runnable_experiment = compile_experiment(compilable_experiment)
    internal_run_experiment(runnable_experiment)
    pass

def _prepare_cetus_experiment(aot, experiment: Experiment, parameters: Dict[str, str]):
    return prepare_cetus_experiment(aot, experiment, parameters)

def _prepare_llm_experiments(aot, experiment: Experiment, parameters: Dict[str, str]) -> List[Experiment]:
    total_compilable_experiments = []
    
    for prompt_name, prompt_path in parameters.items():
        compilable_experiments = prepare_llm_experiment(aot, prompt_name, prompt_path, experiment)
        total_compilable_experiments.extend(compilable_experiments)
    
    
    return total_compilable_experiments

def prepare_experiments(aot, experiment: Experiment, parameters: Dict[str, str]) -> List[CompilableExperiment]:
    
    compilable_experiments = []
    aot_params = parameters[aot]
    
    if(aot in available_llms):
        compilable_experiments = _prepare_llm_experiments(aot, experiment, aot_params)
    
    if aot in available_compilers:
        compilable_experiments = _prepare_cetus_experiment(aot, experiment, aot_params)
        
    return compilable_experiments
    
def compile_experiment(compilable_experiment: CompilableExperiment):
    runnable_experiment = internal_compile_experiment(compilable_experiment)
    return runnable_experiment

def run_experiment(runnable_experiment: RunnableExperiment):
    internal_run_experiment(runnable_experiment)
    


if __name__ == "__main__":
    
    experiment_plans_file_path_from_args = "experiment_plans.csv"
    if len(sys.argv) > 1:
        experiment_plans_file_path_from_args = sys.argv[1]

    with open(experiment_plans_file_path_from_args, "r") as file:
        source_code_infos = [line.split(";")
                             for line in file.read().splitlines()[1:]]
#
    # aots = ['mock','cetus-tiling', 'cetus']
    # aots =["cetus", 'cetus-tiling']
    aots =['mock']
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
            "verbose": "3",
            "profile-loops": "2"
        }
        
    }

    for benchmark_type, trials, dataset, benchmark_folder, kernel_folder, routine_name, source_placeholder, binary_file in source_code_infos:
        baseline_comp_flags = ["SERIAL"]
        
        try:
            experiment = Experiment(benchmark_type, trials, dataset, benchmark_folder.strip(), kernel_folder.strip(), 
                                routine_name.strip(), binary_file.strip(), baseline_comp_flags, source_placeholder.strip())

            
            _run_baseline(experiment)
            
            compilable_experiments = []
            for aot in aots:
                prepared_experiments = prepare_experiments(aot, experiment, parameters)
                compilable_experiments.extend(prepared_experiments)
            
            for compilable_experiment in compilable_experiments:
                runnable_experiment = compile_experiment(compilable_experiment)
                run_experiment(runnable_experiment)
        
        except Exception as e:
            print(f"Error creating experiment-{routine_name}: {e}")
            continue
