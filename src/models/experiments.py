import json
import os

class Experiment():
    def __init__(self, benchmark_type, trials, dataset, benchmark_folder, kernel_folder, routine_name, binary_file, compilation_flags=[], source_placeholder=""):
        self.benchmark_type = benchmark_type
        self.trials = trials
        self.dataset = dataset
        self.benchmark_folder = benchmark_folder.replace(":", "_")
        self.kernel_folder = kernel_folder.replace(":", "_")
        self.routine_name = routine_name.replace(":", "_")
        self.binary_file = binary_file.replace(":", "_")
        self.compilation_flags = compilation_flags
        self.source_placeholder = source_placeholder.replace(":", "_")
        pass
    
    def to_json(self):
        mapper = {
            "benchmark_type": self.benchmark_type,
            "trials": self.trials,
            "dataset": self.dataset,
            "benchmark_folder": self.benchmark_folder,
            "kernel_folder": self.kernel_folder,
            "routine_name": self.routine_name,
            "binary_file": self.binary_file,
            "compilation_flags": self.compilation_flags,
            "source_placeholder": self.source_placeholder
        }
        
        return mapper
    
    def export_json(self, current_step):
        json_obj = self.to_json()
        json_obj["experiment_type"] = current_step
        
        flags_name = get_flags_name(self.compilation_flags)
        runtime_folder = f"{self.benchmark_folder}/{self.kernel_folder}"
        file_path = f"{runtime_folder}/{current_step}-checkpoint/{flags_name}.json"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "w") as file:
            json.dump(json_obj, file)
            file.close()

    def get_c_path(self):
        if (self.benchmark_type == 'nas'):
            return f"{self.benchmark_folder}/common:{self.benchmark_folder}/{self.kernel_folder}"
        else:
            return f"{self.benchmark_folder}/utilities:{self.benchmark_folder}/{self.kernel_folder}/{self.routine_name}"

class CompilableExperiment(Experiment):
    def __init__(self, benchmark_type, trials, dataset, benchmark_folder, kernel_folder, parent_preparation_folder, routine_name, binary_file, compilation_flags=[], source_placeholder=""):
        super().__init__(benchmark_type, trials, dataset, benchmark_folder, kernel_folder, routine_name, binary_file, compilation_flags, source_placeholder)
        self.parent_preparation_folder = str(parent_preparation_folder).replace(":", "_")
        
    def to_json(self):
        mapper = {
            "benchmark_type": self.benchmark_type,
            "trials": self.trials,
            "dataset": self.dataset,
            "benchmark_folder": self.benchmark_folder,
            "kernel_folder": self.kernel_folder,
            "routine_name": self.routine_name,
            "binary_file": self.binary_file,
            "compilation_flags": self.compilation_flags,
            "source_placeholder": self.source_placeholder,
            "parent_preparation_folder": self.parent_preparation_folder
        }
        
        return mapper
        
class RunnableExperiment(CompilableExperiment):
    pass


def experiment_from_json(file_path:str, last_step:str) -> Experiment:
    with open(file_path, "r") as file:
        json_obj = json.load(file)
        file.close()
    
    if(last_step == 'preparation'):
        return CompilableExperiment(json_obj["benchmark_type"], json_obj["trials"], json_obj["dataset"], json_obj["benchmark_folder"], json_obj["kernel_folder"], json_obj["parent_preparation_folder"], json_obj["routine_name"], json_obj["binary_file"], json_obj["compilation_flags"], json_obj["source_placeholder"])
    else:
        return RunnableExperiment(json_obj["benchmark_type"], json_obj["trials"], json_obj["dataset"], json_obj["benchmark_folder"], json_obj["kernel_folder"], json_obj["parent_preparation_folder"], json_obj["routine_name"], json_obj["binary_file"], json_obj["compilation_flags"], json_obj["source_placeholder"])

def get_flags_name(flags) -> str:
    flag_name = ""
    for raw_flag in flags:
        flag = raw_flag.replace(":", "_")
        flag_name += f"{flag}_"
    flag_name = flag_name[:-1]
    return flag_name
