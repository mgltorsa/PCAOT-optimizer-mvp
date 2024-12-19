import sys
from experiments.experimenter import test_diff


def validate_full(loop_ids,full_version_flag,benchmark_folder,kernel_folder,routine_folder,binary_file):
    status = 'Success'
    for loop_id in loop_ids:
        status = test_diff(["SERIAL"], full_version_flag, full_version_flag,str(loop_id),benchmark_folder,kernel_folder,routine_folder,binary_file)
        if status != 'Success':
            break
    kernel_comparison_name = routine_folder.replace("/","-")
    comparison_output_file = f"{benchmark_folder}/bin/comparisons_{kernel_comparison_name}.txt"
    comparison_output_file = f"{benchmark_folder}/bin/comparisons_{kernel_comparison_name}.csv"

    lines=[]
    correct_str = status
    splitted_flags ="".join(full_version_flag).split("_")
    if "FULL" not in splitted_flags:
        optimizer = "".join(full_version_flag)
        for loop_id in loop_ids:
            line=f"none;POLYBENCHMARK;{kernel_folder};{routine_folder};Large;4;1;default;{optimizer.lower()};0.2;0.1;LOOP_{loop_id};{correct_str};-;-;-;-;-;-;-;unknown"
            # line=f"{optimizer}-default-LOOP_{loop_id}:{correct_str}"
            lines.append(line)
    else:
        optimizer, approach, version = splitted_flags[0], splitted_flags[1], splitted_flags[2]
        
        for loop_id in loop_ids:
            line=f"none;POLYBENCHMARK;{kernel_folder};{routine_folder};Large;4;{version};{approach};{optimizer}_FULL;0.2;0.1;LOOP_{loop_id};{correct_str};-;-;-;-;-;-;-;unknown"
            # line=f"{optimizer}-{approach}-{version}-LOOP_{loop_id}:{correct_str}"
            lines.append(line)
    with open(comparison_output_file, 'a') as f:
        content = "\n".join(lines)
        f.write(f"{content}\n")
        f.close()
    return status

def validate_per_loop(baseline_compilation_flags,compilation_flags, base_flags, loopId, benchmark_folder, kernel_folder, routine_folder,binary_file):
    status = test_diff(baseline_compilation_flags,compilation_flags, base_flags, loopId, benchmark_folder, kernel_folder, routine_folder,binary_file)
    
    kernel_comparison_name = routine_folder.replace("/","-")
    comparison_output_file = f"{benchmark_folder}/bin/comparisons_{kernel_comparison_name}.txt"
    comparison_output_file = f"{benchmark_folder}/bin/comparisons_{kernel_comparison_name}.csv"
    splitted_flags ="".join(compilation_flags).split("_")
    print("SPLITTED_GG",splitted_flags)
    optimizer,approach,version,loop_id = splitted_flags[0],splitted_flags[1],splitted_flags[2],splitted_flags[4]
    correct_str=status
    line=f"none;POLYBENCHMARK;{kernel_folder};{routine_folder};LARGE;4;{version};{approach};{optimizer};0.2;0.1;LOOP_{loop_id};{correct_str};-;-;-;-;-;-;-;unknown"
    # line=f"{optimizer}-{approach}-{version}-LOOP_{loop_id}:{correct_str}"
    
    with open(comparison_output_file, 'a') as f:
        f.write(f"{line}\n")
        f.close()

    return status
    

if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        print("Remember Usage: nas or poly")
        
    benchmark_compilation_version = sys.argv[1]

    with open("experiment_plans.txt", "r") as file:
        source_code_infos = [line.split(",") for line in file.read().splitlines()[1:]]
        
    llms = ['GPT4','CODELLAMA']
    prompt_approaches = ['INSTRUCTIONS',"COT"]
    
    for number_of_loops,number_of_versions, class_type, benchmark_folder, kernel_folder, routine_folder, binary_file in source_code_infos:
        code_versions = range(1, int(number_of_versions) + 1)
        loop_ids = list(range(1, int(number_of_loops) + 1))
        jobs_ids_file=f"{kernel_folder}_{routine_folder}_jobs.txt"
        
        if (benchmark_compilation_version == 'poly'):
            validate_full(loop_ids, ["CETUS"], benchmark_folder,kernel_folder,routine_folder,binary_file)
            validate_full(loop_ids, ["OPT"], benchmark_folder,kernel_folder,routine_folder,binary_file)
            validate_full(loop_ids, ["PLUTO"], benchmark_folder,kernel_folder,routine_folder,binary_file)
            
        for llm in llms:
            for prompt_approach in prompt_approaches:
                for code_version in code_versions:
                    full_version_flag = "_".join([llm, prompt_approach, str(
                                code_version), "FULL"])
                    base_flag = [full_version_flag]
                    validate_full(loop_ids, base_flag, benchmark_folder,kernel_folder,routine_folder,binary_file)
                    
                    for loop_id in loop_ids:
                        try:
                            flags = [llm,prompt_approach,str(code_version),"LOOP",str(loop_id)]
                            comp_flag = "_".join(flags)
                            serial_test_flag = ['SERIAL']
                            base_flag = [llm,prompt_approach,str(code_version)]
                            validate_per_loop(serial_test_flag,[comp_flag],base_flag,str(loop_id),benchmark_folder,kernel_folder,routine_folder,binary_file)
                            
                            pass
                        except Exception as e:
                            print("ERROR")
                            print(e)
            