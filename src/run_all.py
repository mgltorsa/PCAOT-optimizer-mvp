from models.experiments import Experiment
from preparation.preparation import prepare_experiment
from compilation.compiler import compile_experiment
from experiments.experimenter import run_experiment as run_experimenter


def run_baseline(experiment: Experiment):
    runnable_experiment = compile_experiment(experiment)
    run_experimenter(runnable_experiment)
    pass


def run_experiment(llm, prompt_name, prompt_path, experiment: Experiment):

    compilable_experiments = prepare_experiment(
        llm, prompt_name, prompt_path, experiment)
    for compilable_experiment in compilable_experiments:
        runnable_experiment = compile_experiment(compilable_experiment)
        run_experimenter(runnable_experiment)
    pass


if __name__ == "__main__":

    with open("experiment_plans.txt", "r") as file:
        source_code_infos = [line.split(",")
                             for line in file.read().splitlines()[1:]]

    aots = ['mock']
   # prompt_approaches = []
    prompt_approaches = {
        "naive-tiler": "/mnt/d/workspace/ud-masters/research-ideas/LLM/use-cases/prompts/naive-tiler",
        "augmented-naive-tiler": "/mnt/d/workspace/ud-masters/research-ideas/LLM/use-cases/prompts/augmented-naive-tiler",
        "parallel-aware-tiler": "/mnt/d/workspace/ud-masters/research-ideas/LLM/use-cases/prompts/parallel-aware-tiler"
    }
    # prompt_approaches = ["SIP", ""]

    for benchmark_type, trials, dataset, benchmark_folder, kernel_folder, routine_name, source_placeholder, binary_file in source_code_infos:
        baseline_comp_flags = ["SERIAL"]
        experiment = Experiment(benchmark_type, trials, dataset, benchmark_folder.strip(), kernel_folder.strip(
        ), routine_name.strip(), binary_file.strip(), baseline_comp_flags, source_placeholder.strip())
        run_baseline(experiment)
        for aot in aots:
            for prompt_name, prompt_path in prompt_approaches.items():
                run_experiment(aot, prompt_name, prompt_path, experiment)
