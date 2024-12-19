import sys
import subprocess
import os
  

def extract_patterns(compilation_flags, mode ,filename, cpath, append_mode, benchmark_name, benchmark_folder,kernel_folder,routine_folder,source_file):
    
    d_compilation_flags = "-D" + " -D".join(compilation_flags)
    
    os.environ["CFLAGS"]=d_compilation_flags
    
    os.environ["CPATH"]=cpath
    
    # print("CFLAGS",d_compilation_flags)
    
    commands=[
        f"pcaot -aot=1 -pcaot_analysis={mode} -append={append_mode}",
        f"-bench={benchmark_name}",
        f"-kernel={kernel_folder} -routine={routine_folder}-{filename}",
        f"{benchmark_folder}/{kernel_folder}/{source_file}"
    ]
    
    command = " ".join(commands)
    
    exec_command(command)
    pass
    
def exec_command(command):
    # print("COMMAND: ", command)
    process = subprocess.Popen(command, shell=True)
    process.communicate() 

if __name__ == "__main__":
    
    
    print("Arguments", sys.argv)
    
    if len(sys.argv) < 1:
        print("Usage: python patterns_extractor.py \{inputfile\}")
        sys.exit(1)
        
    mode = "1"
    
    if len(sys.argv)  > 2:
        mode = sys.argv[2]        
       
    
    modeStr="patterns"
    
    if mode == "0":
        modeStr="sizes"
    
    print("MODE: ", modeStr)
    
    
    input_file = sys.argv[1]
        

    with open(input_file, "r") as file:
        source_code_infos = [line.split(",") for line in file.read().splitlines()[1:]]
        
    llms = ['GPT4','CODELLAMA']
    prompt_approaches = ['SIP','INSTRUCTIONS',"COT"]
    
    
    #loops,#version,cpath,BENCH_FOLDER,KERNEL_FOLDER,routine_name,source_file
    
    for number_of_loops,number_of_versions, benchmark_name, c_path, benchmark_folder, kernel_folder, routine_folder,source_file in source_code_infos:
        code_versions = list(range(1, int(number_of_versions) + 1))
        loop_ids = list(range(1, int(number_of_loops) + 1))
        
        if mode == "0":
            extract_patterns(["SERIAL"],  mode, "SERIAL", c_path, True, benchmark_name, benchmark_folder,kernel_folder,routine_folder,source_file)
            continue
            
            
        for llm in llms:
            for prompt_approach in prompt_approaches:
                for code_version in code_versions:
                    first_process = True            
                    full_version_flag = "_".join([llm, prompt_approach, str(
                                code_version), "FULL"])
                    extract_patterns([full_version_flag], mode,  f"{llm}-{prompt_approach}-{code_version}-FULL", c_path, True, benchmark_name, benchmark_folder,kernel_folder,routine_folder,source_file)
                    # first_process=False
                    for loop_id in loop_ids:
                        try:
                            flags = [llm,prompt_approach,str(code_version),"LOOP",str(loop_id)]
                            comp_flag = "_".join(flags)
                            extract_patterns(["SERIAL",comp_flag], mode, f"{llm}-{prompt_approach}-{code_version}", c_path, first_process, benchmark_name, benchmark_folder,kernel_folder,routine_folder,source_file)
                            first_process=False
                        except Exception as e:
                            print("ERROR")
                            print(e)
                    
            
            