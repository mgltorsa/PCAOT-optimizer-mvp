import os
import glob
import pandas as pd

def process_csv_files(input_directory, output_file):

    # Read all CSV files in the directory
    filenames = glob.glob(os.path.join(input_directory, '**', '*.csv'), recursive=True)
    all_sizes = pd.DataFrame()
    for filename in filenames:
        sizes_df = pd.read_csv(filename, sep=';', names=['benchmark', 'function', 'subroutine', 'loopId', 'size'])
        all_sizes = pd.concat([all_sizes, sizes_df])

    all_sizes.to_csv(output_file, index=False, sep=';')

# Usage
input_directory = '/work/parot/mgltorsa/CoExperts-UseCases/llm-optimizer/sizes'
output_file = '/work/parot/mgltorsa/CoExperts-UseCases/llm-optimizer/sizes-output.csv'
process_csv_files(input_directory, output_file)