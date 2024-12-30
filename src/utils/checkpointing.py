from models.experiments import Experiment, experiment_from_json, get_flags_name
import os
from typing import List

def save_checkpoint(experiment: Experiment, current_step: str):
    experiment.export_json(current_step)

def load_checkpoint(benchmark_folder, kernel_folder, current_step, flags) -> Experiment:
    flags_name = get_flags_name(flags)
    file_path = f"{benchmark_folder}/{kernel_folder}/{current_step}-checkpoint/{flags_name}.json"
    return experiment_from_json(file_path, current_step)


def collect_llms_checkpoints(llm, raw_prompt_name, benchmark_folder, kernel_folder, current_step) -> List[Experiment]:
    folder_root = f"{benchmark_folder}/{kernel_folder}/{current_step}-checkpoint"
    if not os.path.exists(folder_root):
        return []
    
    prompt_name = raw_prompt_name.replace(":", "_").replace("-", "_")
    checkpoint_files = [f for f in os.listdir(folder_root) if llm.upper() in f]
    json_files = [f for f in checkpoint_files if f.endswith(".json")]
    found_checkpoints = [f for f in json_files if str(f).lower().find(prompt_name.lower()) != -1]
    return [_load_checkpoint_from_file(f"{folder_root}/{f}", current_step) for f in found_checkpoints]

def _load_checkpoint_from_file(file_path, current_step) -> Experiment:
    return experiment_from_json(file_path, current_step)

def exists_checkpoint(benchmark_folder, kernel_folder, current_step, flags) -> bool:
    flags_name = get_flags_name(flags)
    file_path = f"{benchmark_folder}/{kernel_folder}/{current_step}-checkpoint/{flags_name}.json"
    return os.path.exists(file_path)


