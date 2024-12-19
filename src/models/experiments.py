class Experiment():
    def __init__(self, benchmark_type, trials, dataset, benchmark_folder, kernel_folder, routine_name, binary_file, compilation_flags=[], source_placeholder=""):
        self.benchmark_type = benchmark_type
        self.trials = trials
        self.dataset = dataset
        self.benchmark_folder = benchmark_folder
        self.kernel_folder = kernel_folder
        self.routine_name = routine_name
        self.binary_file = binary_file
        self.compilation_flags = compilation_flags
        self.source_placeholder = source_placeholder
        pass
    
    def get_c_path(self):
        if (self.benchmark_type == 'nas'):
            return f"{self.benchmark_folder}/common:${self.benchmark_folder}/{self.kernel_folder}"
        else:
            return f"{self.benchmark_folder}/utilities:${self.benchmark_folder}/{self.kernel_folder}/{self.routine_name}"

