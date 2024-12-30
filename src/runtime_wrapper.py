import subprocess
from datetime import datetime
from typing import Dict, Any
from argparse import Namespace
import argparse
from repository.mongo import save_to_mongodb, load_mongo_client
from utils.profile_extractor import collect_profiled_features, ALL_LOOPS_PROFILE_FLAG


def run_program(executable: str, args: Namespace) -> Dict[str, Any]:
    """
    Run the specified program with given arguments and return execution details
    """
    times=[]
    profiled_features = []
    program_args = args.program_args

    profile_option = ALL_LOOPS_PROFILE_FLAG
    if args.profile_loops:
        profile_option = args.profile_loops
    

    for i in range(10):
        start_time = datetime.now()
        # Run the program and capture output
        process = subprocess.run(
            [executable, *program_args],
            capture_output=True,
            text=True,
            check=True
        )

        end_time = datetime.now()
        global_execution_time = (end_time - start_time).total_seconds()
        times.append(global_execution_time)
        output = process.stdout
        process_profiled_features = collect_profiled_features(output, profile_option)
        profiled_features.extend(process_profiled_features)


    



def main():
    parser = argparse.ArgumentParser(
        description='Run an executable and store its output in MongoDB'
    )
    parser.add_argument('executable', help='Path to the executable to run')
    parser.add_argument('-pargs','--program_args', type=str, help='Arguments to pass to the program')
    
    # create to mutually exclusive group for profile options, one for profile by loop and one for full profile
    profile_group = parser.add_mutually_exclusive_group(required=True)
    profile_group.add_argument('-pfull', '--profile-full', action='store_true', help='Profile Full')
    profile_group.add_argument('-ploops', '--profile-loops', type=int, help='Profile the program')

    args = parser.parse_args()
    
    # Run the program and get results
    result = run_program(args.executable, args)
    
    # Save results to MongoDB
    save_to_mongodb(
        result,
        load_mongo_client(),
        collection_name="executions"
    )
    
    # Print status to console
    print(f"Execution {'successful' if result['status'] == 'success' else 'failed'}")
    print(f"Return code: {result['return_code']}")
    if result['status'] == 'error':
        print(f"Error: {result['error_message']}")

if __name__ == "__main__":
    main()
