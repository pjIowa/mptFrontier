import pandas as pd
import os
import glob

data_path = os.getcwd()+"/data"
if os.path.exists(data_path) :   
    os.chdir(data_path)
else:
    print(f"can't move to {data_path}")
    exit()

file_name_to_csv = {}
for file_name in glob.iglob('*.csv'):
	n_csv = pd.read_csv(file_name, parse_dates=['Date'])
	file_name_to_csv[file_name] = n_csv
	print(f'{file_name} {len(n_csv.index)}')

# spy = spy_csv['Adj Close'].values