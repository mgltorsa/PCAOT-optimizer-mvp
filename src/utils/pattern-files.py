import csv
import os
import glob
from collections import defaultdict

def process_csv_files(input_directory, output_file):
    all_data = defaultdict(set)

    # Read all CSV files in the directory
    filenames = glob.glob(os.path.join(input_directory, '**', '*.csv'), recursive=True)
    for filename in filenames:
        with open(filename, 'r') as file:
            reader = csv.reader(file, delimiter=';')
            for row in reader:
                if len(row) < 4:  # Skip rows with insufficient data
                    continue
                key = tuple(row[:4])  # benchmark, function, subroutine-optimizer-approach-code_version, loopId
                patterns = row[4] if len(row) > 4 else ''
                if(patterns.strip() == ''):
                    continue
                all_data[key].update(patterns.split(','))

    # Process the collected data
    output_data = []
    for key, patterns in all_data.items():
        patterns = [p.strip() for p in patterns if p.strip()]
        print(patterns)
        if patterns:  # Only keep rows with patterns
            benchmark, function, subroutine_approach, loop_id = key[:4]
            
            # Split the subroutine-optimizer-approach-code_version field
            parts = subroutine_approach.split('-')
            
            # Handle the case where 'FULL' might be present
            if parts[-1] == 'FULL':
                subroutine, optimizer, approach, code_version = parts[0], parts[1] + '_FULL', parts[2], parts[3]
            else:
                subroutine, optimizer, approach, code_version = parts[:-3], parts[-3], parts[-2], parts[-1]
            
            # Join subroutine parts if there were more than expected
            subroutine = ''.join(subroutine)

            output_data.append([
                benchmark, function, subroutine, optimizer, approach, code_version,
                loop_id, ','.join(patterns)
            ])

    # Write to output CSV file
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['benchmark', 'function', 'subroutine', 'optimizer', 'approach', 'code_version', 'loopId', 'patterns'])
        writer.writerows(output_data)

# Usage
input_directory = '/work/parot/mgltorsa/CoExperts-UseCases/llm-optimizer/patterns'
output_file = '/work/parot/mgltorsa/CoExperts-UseCases/llm-optimizer/patterns-output.csv'
process_csv_files(input_directory, output_file)