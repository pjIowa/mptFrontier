import pandas as pd
import os
import glob
import numpy as np

data_path = os.getcwd()+"/data"
if os.path.exists(data_path) :   
    os.chdir(data_path)
else:
    print(f"can't move to {data_path}")
    exit()

asset_name_to_ret = {}
asset_names = []
print("Reading asset prices...")
for file_name in glob.iglob('*.csv'):
	n_csv = pd.read_csv(file_name, parse_dates=['Date'])
	n_prices = n_csv['Adj Close'].values
	n_returns = n_prices[1:]/n_prices[:-1]-1.
	asset_name = file_name[:-4]
	asset_names.append(asset_name)
	asset_name_to_ret[asset_name] = n_returns
	print(f'{file_name}\trows: {len(n_csv.index)}'.expandtabs(25))
print()

asset_name_to_mean_ret = {}
asset_name_to_stdev = {}
for asset_name in asset_names:
	a_ret = asset_name_to_ret[asset_name]
	asset_name_to_mean_ret[asset_name] = np.mean(a_ret)
	asset_name_to_stdev[asset_name] = np.std(a_ret)

asset_name_to_sr = {}
for asset_name in asset_names:
	a_sr = asset_name_to_mean_ret[asset_name]/asset_name_to_stdev[asset_name]
	asset_name_to_sr[asset_name] = a_sr

sorted_by_sr = dict(sorted(asset_name_to_sr.items(), key=lambda item: item[1]))
print("Assets ranked by Sharpe Ratio from lowest to highest")
for asset_name in sorted_by_sr:
	print(f'{asset_name}\tsharpe ratio: {round(sorted_by_sr[asset_name],3)}'.expandtabs(25))
