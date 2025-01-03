import subprocess
import os
from models.experiments import CompilableExperiment, RunnableExperiment
from utils.checkpointing import save_checkpoint, load_checkpoint,exists_checkpoint

def compile_experiment(experiment: CompilableExperiment)->RunnableExperiment:

    compilation_flags = experiment.compilation_flags

    # Define the options dynamically

    if (len(compilation_flags) > 1):
        no_serial_cflags = compilation_flags[1:]
        new_binary_folder = "".join(no_serial_cflags)
    else:
        new_binary_folder = "_".join(compilation_flags)

    new_binary_folder = new_binary_folder.replace(":","_")

    benchmark_folder = experiment.benchmark_folder
    kernel_folder = experiment.kernel_folder
    routine_folder = experiment.routine_name
    class_type = experiment.dataset
    benchmark_compilation_version = experiment.benchmark_type
    binary_file = experiment.binary_file
    parent_preparation_folder = experiment.parent_preparation_folder
    
    compilation_folder = f"{benchmark_folder}/bin/{kernel_folder}/"

    if parent_preparation_folder is not None:
        compilation_folder += f"{parent_preparation_folder}/{new_binary_folder}"
    else:
        compilation_folder += f"{new_binary_folder}"

    root_file_base_flag = f"ROOT_FILE_BASE={compilation_folder}"

    extra_cflags = ['CETUS_PAPI', 'CETUS_CHECKPOINT_WRITE', root_file_base_flag]

    cflags =[*extra_cflags, *compilation_flags]

    d_cflags_str = "-D" + " -D".join(cflags)

    # Build the command dynamically
    os.environ["CFLAGSLLMS"] = f"{d_cflags_str} -I{parent_preparation_folder}"

    os.environ["CFLAGS"] = f"{d_cflags_str}"

    cpath = experiment.get_c_path()

    os.environ["CPATH"] = f"{cpath}"


    # compilation_folder = f"{kernel_folder}/{routine_folder}/{new_binary_folder}/bin"
    compilation_info_file = f"{compilation_folder}/compilation_info_CLASS_{class_type}.txt"

    source_placeholder = experiment.source_placeholder
    source_placeholder_value = f"{benchmark_folder}/{kernel_folder}/{parent_preparation_folder}/{experiment.routine_name}.c"
    
    cetus_papi_libs = f"{parent_preparation_folder}/cetus_papi.c"
    cetus_checkpoint_libs = f"{parent_preparation_folder}/cetus_correctness.c"
    
    clibs_str = " ".join(["-lm", "-lpapi", "-fopenmp", cetus_papi_libs, cetus_checkpoint_libs])


    compilation_command = [
        # f"make -C {benchmark_folder}/{kernel_folder} clean > {compilation_info_file} 2>&1",
        f"make -C {benchmark_folder}/{kernel_folder} CLASS={class_type} BINDIR={compilation_folder} {source_placeholder}={source_placeholder_value} C_LIB={clibs_str}  >> {compilation_info_file} 2>&1"
    ]

    compilation_command = " && ".join(compilation_command)
    if benchmark_compilation_version == 'poly':
        # gcc -O3 -I utilities -I linear-algebra/kernels/atax utilities/polybench.c
        # linear-algebra/kernels/atax/atax.c -DPOLYBENCH_TIME -o atax_time
        compilation_command = [
            f"gcc -std=c99  -O3 -I {benchmark_folder}/utilities -I {benchmark_folder}/{kernel_folder}/{routine_folder} {benchmark_folder}/utilities/polybench.c",
            f"{source_placeholder_value} -DPOLYBENCH_TIME -DCORRECTNESS -D{class_type} {d_cflags_str}  -o {benchmark_folder}/bin/{binary_file} -lm -fopenmp  > {compilation_info_file} 2>&1"
        ]

        # Temporaly for tiling
        # compilation_command = [
        #     f"gcc -std=c99  -O3 -I {benchmark_folder}/utilities -I {benchmark_folder}/{kernel_folder}/{routine_folder} {benchmark_folder}/utilities/polybench.c",
        #     f"{benchmark_folder}/{kernel_folder}/{routine_folder}/{binary_file}_tiling.c -DPOLYBENCH_PAPI  -D{class_type} {d_cflags_str} -o {benchmark_folder}/bin/{binary_file} -lm -lpapi -fopenmp  > {compilation_info_file} 2>&1"
        # ]

        compilation_command = " ".join(compilation_command)

    command_list = [
        # f"mkdir -p {benchmark_folder}/bin",
        # f"rm -ff {benchmark_folder}/bin/{binary_file}",
        f"rm -rf {compilation_folder}/{binary_file}",
        f"mkdir -p {compilation_folder}",
        f"touch {compilation_info_file}",
        compilation_command
    ]
    # f"mv {benchmark_folder}/bin/{binary_file} {compilation_folder}"]

    # print("COMMAND_LIST: ", command_list)

    command = " && ".join(command_list)

    print("COMMAND: ", command)

    if exists_checkpoint(benchmark_folder, kernel_folder, 'compilation', compilation_flags):
        return load_checkpoint(benchmark_folder, kernel_folder, 'compilation', compilation_flags)

    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    process.communicate()  # This waits for the process to finish and prints the output

    save_checkpoint(experiment, 'compilation')

    return RunnableExperiment(experiment.benchmark_type, 
                              experiment.trials, 
                              experiment.dataset, 
                              experiment.benchmark_folder,
                              experiment.kernel_folder, 
                              experiment.parent_preparation_folder, 
                              experiment.routine_name, 
                              binary_file, 
                              compilation_flags, 
                              experiment.source_placeholder)