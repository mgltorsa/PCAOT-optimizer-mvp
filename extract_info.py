import os
import pandas as pd
import re

# Function to extract information from results file

def extract_infoCompilationLog(path):
      if "GPT4_COT_1_LOOP_3" in path:
          print("here")
      with open(path, 'r') as file:
        lines = file.readlines()
        error_lines = []
        for i in range(len(lines)):
            if "error:" in lines[i]:
                error_lines.append(lines[i].strip())
                if i + 1 < len(lines):
                    error_lines.append(lines[i + 1].strip())
      return error_lines


def extract_info(results_file,idLoop,folder_path, nameApproach):
    compilation_path = os.path.join(folder_path, "compilation_info_CLASS_LARGE_DATASET.txt")
   # compilation_path = os.path.join(folder_path, "compilation_info_CLASS_B.txt")
   
    with open(results_file, 'r') as file:
        content = file.read()
        # Extract experiment status
        experiment_status = ""
        logCompilation = ""
        

        if "UNSUCCESSFUL" in content: 
            experiment_status = "Incorrect"

        elif "SUCCESSFUL"  in content:
            experiment_status = "Success"    

        elif "VERIFICATION FAILED" in content: 
            experiment_status = "Incorrect" 

        elif "verification failed" in content: 
            experiment_status = "Incorrect"         
        
        else:
             with open(compilation_path, 'r') as fileConten:
                    contentCompilationFile = fileConten.read()
                    if "error: " in contentCompilationFile:
                         experiment_status = "Compilation Error"                     
                         logCompilation = extract_infoCompilationLog(compilation_path)
                    else:
                         experiment_status = "Execution Error"    
                         ## FAIL FOR POLY. POLYBENCH VERIFICATION IS DONE IN FILES
                
        # Extract time
        pattern = r"TimeInstrument_"+nameApproach + idLoop + r" = (\d+\.\d+)"
        time_match = re.search(pattern, content)
        time = float(time_match.group(1)) if time_match else None
    return experiment_status, time, logCompilation


def extract_loop_ids(file_path, approachName):
    loop_ids = set()  # Using a set to avoid duplicate loop IDs
    with open(file_path, 'r') as file:
        for line in file:
            pattern = "TimeInstrument_"+approachName
            if pattern in line:
                # Extract loop ID using regular expression
                match = re.search(r"TimeInstrument_"+approachName+"LOOP_(\d+)", line)
                if match:
                    loop_ids.add(int(match.group(1)))  # Add extracted loop ID to the set
    return sorted(loop_ids)  # Convert set to sorted list and return 

""" def extract_info_cetus(): """

# Initialize DataFrame to store extracted data
data = {
    'function': [],
    'subroutine': [],
    'code_version': [],
    'approach': [],
    'optimizer': [],
    'loopId': [],
    'experiment_status': [],
    'time-1': [],
    'time-2': [],
    'time-3': [],
    'Cause': []
}

# Directory containing folders

root_dir = "/work/parot/LLM_RESULTS/NPB3.3-SER-C/bin/Poly"
#root_dir = "/work/parot/LLM_RESULTS/NPB3.3-SER-C/bin/NASA"
# Loop through each function folder
for function_folder in os.listdir(root_dir):
 
    
    function = function_folder
    function_path = os.path.join(root_dir, function_folder)
    # Loop through each subroutine folder
    for subroutine_folder in os.listdir(function_path):
        subroutine = subroutine_folder
        subroutine_path = os.path.join(function_path, subroutine_folder)
        print(function_folder, subroutine_folder)
        if subroutine_folder == "norm2u3":
            print("norm2u3")
            
        # Loop through each optimizer_approach_codeVersion_loopId folder
        for folder in os.listdir(subroutine_path):
            
           
            if folder == "CETUS" or folder =="OPT" or folder == "SERIAL" or folder == "PLUTO" or folder == "ROSE" or folder == "CODELLAMA_COT_1_FULL" or folder =="CODELLAMA_COT_2_FULL" or folder =="CODELLAMA_COT_3_FULL" or folder =="CODELLAMA_INSTRUCTIONS_1_FULL"  or folder == "CODELLAMA_INSTRUCTIONS_2_FULL"  or folder == "CODELLAMA_INSTRUCTIONS_3_FULL"  or folder == "GPT4_INSTRUCTIONS_1_FULL" or folder =="GPT4_INSTRUCTIONS_2_FULL" or folder =="GPT4_INSTRUCTIONS_3_FULL" or folder =="GPT4_COT_1_FULL" or folder =="GPT4_COT_2_FULL" or folder =="GPT4_COT_3_FULL" or folder =="GPT4_SIP_1_FULL" or folder =="GPT4_SIP_2_FULL" or folder =="GPT4_SIP_3_FULL" or folder =="CODELLAMA_SIP_1_FULL" or folder =="CODELLAMA_SIP_2_FULL" or folder =="CODELLAMA_SIP_3_FULL":


                folder_path =  os.path.join(subroutine_path, folder)
                file_loops =  os.path.join(folder_path, "results_1.txt")
                loops_ids=""

                if folder == "CETUS":
                    approach = "default"
                    optimizer = "cetus"
                    loops_ids =extract_loop_ids(file_loops,folder+"_")
                if folder == "PLUTO":
                    approach = "default"
                    optimizer = "pluto"
                    loops_ids =extract_loop_ids(file_loops,folder+"_")
                if folder == "ROSE":
                    approach = "default"
                    optimizer = "rose"
                    loops_ids =extract_loop_ids(file_loops,folder+"_")        
                if folder == "SERIAL" :
                    approach = "baseline"
                    optimizer = "serial"
                    loops_ids=extract_loop_ids(file_loops,"")  
                # Commented temporarily
                # if folder == "OPT" or folder == "CODELLAMA_COT_1_FULL" or folder =="CODELLAMA_COT_2_FULL" or folder =="CODELLAMA_COT_3_FULL" or folder =="CODELLAMA_INSTRUCTIONS_1_FULL"  or folder == "CODELLAMA_INSTRUCTIONS_2_FULL"  or folder == "CODELLAMA_INSTRUCTIONS_3_FULL"  or folder == "GPT4_INSTRUCTIONS_1_FULL" or folder =="GPT4_INSTRUCTIONS_2_FULL" or folder =="GPT4_INSTRUCTIONS_3_FULL" or folder =="GPT4_COT_1_FULL" or folder =="GPT4_COT_2_FULL" or folder =="GPT4_COT_3_FULL":
                #     approach = "hand"
                #     optimizer = "hand" 
                #     newPath = os.path.join(subroutine_path, "SERIAL")
                #     file_loops =  os.path.join(newPath, "results_1.txt")
                #     loops_ids=extract_loop_ids(file_loops,"") 
                
                
   
                for loopId in loops_ids:
                    time_1, time_2, time_3 = None, None, None
                    
                    for i in range(1, 4):                    
                        results_file = os.path.join(folder_path, f"results_{i}.txt")
                        if os.path.exists(results_file):
                            experiment_status = ""
                            time  = ""
                            logCompilation = ""
                            if folder == "SERIAL":
                                experiment_status, time , logCompilation = extract_info(results_file,"LOOP_"+str(loopId), folder_path, "" )
                            elif folder =="CODELLAMA_COT_1_FULL" or folder =="CODELLAMA_COT_2_FULL" or folder =="CODELLAMA_COT_3_FULL" or folder =="CODELLAMA_INSTRUCTIONS_1_FULL"  or folder == "CODELLAMA_INSTRUCTIONS_2_FULL"  or folder == "CODELLAMA_INSTRUCTIONS_3_FULL"  or folder == "GPT4_INSTRUCTIONS_1_FULL" or folder =="GPT4_INSTRUCTIONS_2_FULL" or folder =="GPT4_INSTRUCTIONS_3_FULL" or folder =="GPT4_COT_1_FULL" or folder =="GPT4_COT_2_FULL" or folder =="GPT4_COT_3_FULL"or folder =="GPT4_SIP_1_FULL" or folder =="GPT4_SIP_2_FULL" or folder =="GPT4_SIP_3_FULL" or folder =="CODELLAMA_SIP_1_FULL" or folder =="CODELLAMA_SIP_2_FULL" or folder =="CODELLAMA_SIP_3_FULL":
                                experiment_status, time , logCompilation = extract_info(results_file,"LOOP_"+str(loopId), folder_path, "" )
                            else:
                                experiment_status, time , logCompilation = extract_info(results_file,"LOOP_"+str(loopId), folder_path, folder+"_" ) 
                            
                            if i == 1:
                                time_1 = time
                            elif i == 2:
                                time_2 = time
                            elif i == 3:
                                time_3 = time

                    if  folder =="CODELLAMA_COT_1_FULL" or folder =="CODELLAMA_COT_2_FULL" or folder =="CODELLAMA_COT_3_FULL" or folder =="CODELLAMA_INSTRUCTIONS_1_FULL"  or folder == "CODELLAMA_INSTRUCTIONS_2_FULL"  or folder == "CODELLAMA_INSTRUCTIONS_3_FULL"  or folder == "GPT4_INSTRUCTIONS_1_FULL" or folder =="GPT4_INSTRUCTIONS_2_FULL" or folder =="GPT4_INSTRUCTIONS_3_FULL" or folder =="GPT4_COT_1_FULL" or folder =="GPT4_COT_2_FULL" or folder =="GPT4_COT_3_FULL" or folder =="GPT4_SIP_1_FULL" or folder =="GPT4_SIP_2_FULL" or folder =="GPT4_SIP_3_FULL" or folder =="CODELLAMA_SIP_1_FULL" or folder =="CODELLAMA_SIP_2_FULL" or folder =="CODELLAMA_SIP_3_FULL":
                        optimizer, approach, code_version, optmizerAdition = folder.split("_")
                        data['optimizer'].append(optimizer+"_"+optmizerAdition)
                        data['code_version'].append(code_version)
                    else:
                        data['optimizer'].append(optimizer)
                        data['code_version'].append(1)
                        

                    data['function'].append(function)
                    data['subroutine'].append(subroutine)
               
                    data['approach'].append(approach)
                    data['loopId'].append("LOOP_"+str(loopId))
                    data['experiment_status'].append(experiment_status)
                    data['time-1'].append(time_1)
                    data['time-2'].append(time_2)
                    data['time-3'].append(time_3)
                    data['Cause'].append(logCompilation)             

            else:
            
                if folder == "CODELLAMA_COT_1_LOOP_1":
                    print("entro")

                print("folder: "+folder)
                
                optimizer, approach, code_version, loopName, loopId = folder.split("_")


                folder_path = os.path.join(subroutine_path, folder)
                # Initialize variables for time
                time_1, time_2, time_3 = None, None, None
                # Loop through each results file
                for i in range(1, 4):
                    results_file = os.path.join(folder_path, f"results_{i}.txt")
                    if os.path.exists(results_file):
                        print("hello"+folder_path)
                        experiment_status, time, logCompilation = extract_info(results_file,loopName+"_"+loopId,folder_path,"")
                        if i == 1:
                            time_1 = time
                        elif i == 2:
                            time_2 = time
                        elif i == 3:
                            time_3 = time
                # Append data to DataFrame


                data['function'].append(function)
                data['subroutine'].append(subroutine)
                data['code_version'].append(code_version)
                data['approach'].append(approach)
                data['optimizer'].append(optimizer)
                data['loopId'].append("LOOP_"+str(loopId))
                data['experiment_status'].append(experiment_status)
                data['time-1'].append(time_1)
                data['time-2'].append(time_2)
                data['time-3'].append(time_3)
                data['Cause'].append(logCompilation)   

# Create DataFrame
df = pd.DataFrame(data)

# Save DataFrame to Excel
df.to_excel("experiment_data.xlsx", index=False)
