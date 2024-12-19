import subprocess
import os
import sys
from models.experiments import Experiment


def compile_experiment(experiment: Experiment):

    compilation_flags = experiment.compilation_flags

    # Define the options dynamically
    d_compilation_flags = "-D" + " -D".join(compilation_flags)

    # print(d_compilation_flags)
    if (len(compilation_flags) > 1):
        no_serial_cflags = compilation_flags[1:]
        new_binary_folder = "".join(no_serial_cflags)
    else:
        new_binary_folder = "_".join(compilation_flags)

    # Build the command dynamically
    os.environ["CFLAGSLLMS"] = f"{d_compilation_flags}"

    cpath = experiment.get_c_path()

    os.environ["CPATH"] = f"{cpath}"

    benchmark_folder = experiment.benchmark_folder
    kernel_folder = experiment.kernel_folder
    routine_folder = experiment.routine_name
    class_type = experiment.dataset
    benchmark_compilation_version = experiment.benchmark_type
    binary_file = experiment.binary_file

    compilation_folder = f"{benchmark_folder}/bin/{kernel_folder}/{routine_folder}/{new_binary_folder}"
    compilation_info_file = f"{compilation_folder}/compilation_info_CLASS_{class_type}.txt"

    source_placeholder = experiment.source_placeholder

    compilation_command = [
        f"make -C {benchmark_folder}/{kernel_folder} clean > {compilation_info_file} 2>&1",
        f"make -C {benchmark_folder}/{kernel_folder} CLASS={class_type} BINDIR={compilation_folder} {source_placeholder}={experiment.binary_file}.c  >> {compilation_info_file} 2>&1"
    ]

    compilation_command = " && ".join(compilation_command)
    if benchmark_compilation_version == 'poly':
        # gcc -O3 -I utilities -I linear-algebra/kernels/atax utilities/polybench.c
        # linear-algebra/kernels/atax/atax.c -DPOLYBENCH_TIME -o atax_time
        compilation_command = [
            f"gcc -std=c99  -O3 -I {benchmark_folder}/utilities -I {benchmark_folder}/{kernel_folder}/{routine_folder} {benchmark_folder}/utilities/polybench.c",
            f"{benchmark_folder}/{kernel_folder}/{routine_folder}/{binary_file}.c -DPOLYBENCH_TIME -DCORRECTNESS -D{class_type} {d_compilation_flags}  -o {benchmark_folder}/bin/{binary_file} -lm -fopenmp  > {compilation_info_file} 2>&1"
        ]

        # Temporaly for tiling
        # compilation_command = [
        #     f"gcc -std=c99  -O3 -I {benchmark_folder}/utilities -I {benchmark_folder}/{kernel_folder}/{routine_folder} {benchmark_folder}/utilities/polybench.c",
        #     f"{benchmark_folder}/{kernel_folder}/{routine_folder}/{binary_file}_tiling.c -DPOLYBENCH_PAPI  -D{class_type} {d_compilation_flags} -o {benchmark_folder}/bin/{binary_file} -lm -lpapi -fopenmp  > {compilation_info_file} 2>&1"
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

    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    process.communicate()  # This waits for the process to finish and prints the output

    process.stdout
    process.stderr

    return Experiment(experiment.benchmark_type, experiment.trials, experiment.dataset, experiment.benchmark_folder,
                      experiment.kernel_folder, experiment.routine_name, binary_file, compilation_flags, experiment.source_placeholder)
