import pandas as pd
import os
import glob
import numpy as np
import matplotlib.pyplot as plt

data_path = os.getcwd()+"/data"
if os.path.exists(data_path) :   
    os.chdir(data_path)
else:
    print(f"can't move to {data_path}")
    exit()

daily_ret_map = {}
daily_lret_map = {}
asset_names = []
print("Reading asset prices...")
for file_name in glob.iglob('*.csv'):
	asset_name = file_name[:-4]
	asset_names.append(asset_name)
	n_csv = pd.read_csv(file_name, parse_dates=['Date'])
	n_prices = n_csv['Adj Close'].values
	daily_ret_map[asset_name] = n_prices[1:]/n_prices[:-1]-1.
	daily_lret_map[asset_name] = np.log(n_prices[1:]/n_prices[:-1])
	print(f'{file_name}\trows: {len(n_csv.index)}'.expandtabs(25))
print()

sr_map = {}
# risk-free rate assumed to be zero
for asset_name in asset_names:
	daily_ret = daily_ret_map[asset_name]
	annual_sr = np.mean(daily_ret)/np.std(daily_ret)*(252**.5)
	sr_map[asset_name] = annual_sr

print("Assets ranked by Sharpe Ratio from lowest to highest")
sorted_by_sr = dict(sorted(sr_map.items(), key=lambda item: item[1]))
for asset_name in sorted_by_sr:
	print(f'{asset_name}\tsharpe ratio: {round(sorted_by_sr[asset_name],3)}'.expandtabs(25))

fig, ax = plt.subplots()
for asset_name in asset_names:
	daily_ret = daily_ret_map[asset_name]
	mean_ret = np.mean(daily_ret)
	var_ret = np.var(daily_ret)
	ax.scatter(mean_ret, var_ret)
	ax.annotate(asset_name, (mean_ret, var_ret))
plt.xlabel("Variance")
plt.ylabel("Return")
plt.title("Daily Mean-Variance by Asset")
plt.show()