from models.experiments import Experiment, experiment_from_json
import os
from typing import List

def save_checkpoint(experiment: Experiment, current_step: str):
    experiment.export_json(current_step)

def load_checkpoint(benchmark_folder, current_step, flags) -> Experiment:
    flags_name = get_flags_name(flags)
    file_path = f"{benchmark_folder}/{current_step}-checkpoint/{flags_name}.json"
    return experiment_from_json(file_path, current_step)


def collect_llms_checkpoints(benchmark_folder, current_step) -> List[Experiment]:
    folder_root = f"{benchmark_folder}/{current_step}-checkpoint"
    checkpoint_files = [f for f in os.listdir(folder_root) if "PCAOT_LLM" in f]
    json_files = [f for f in checkpoint_files if f.endswith(".json")]
    return [_load_checkpoint_from_file(f, current_step) for f in json_files]

def _load_checkpoint_from_file(file_path, current_step) -> Experiment:
    return experiment_from_json(file_path, current_step)

def exists_checkpoint(benchmark_folder, current_step, flags) -> bool:
    flags_name = get_flags_name(flags)
    file_path = f"{benchmark_folder}/{current_step}-checkpoint/{flags_name}.json"
    return os.path.exists(file_path)

def get_flags_name(flags) -> str:
    flag_name = ""
    for raw_flag in flags:
        flag = raw_flag.replace(":", "_")
        flag_name += f"{flag}_"
    flag_name = flag_name[:-1]
    return flag_name

