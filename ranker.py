import pandas as pd
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from functools import reduce
import scipy.optimize as sco
import itertools

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
	annual_sr = np.mean(daily_ret)/np.std(daily_ret)*np.sqrt(252)
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
	ax.scatter(var_ret, mean_ret)
	ax.annotate(asset_name, (var_ret, mean_ret))
plt.xlabel("Variance")
plt.ylabel("Return")
plt.title("Daily Mean-Variance by Asset")
plt.show()

df_from_each_file = []
file_names = list(glob.iglob('*.csv'))
num_assets = len(file_names)
for file_name in file_names:
	df = pd.read_csv(file_name)
	asset_name = file_name[:-4]
	df = df.rename({'Adj Close': asset_name}, axis=1)
	df_from_each_file.append(df)
df_full = reduce(lambda x, y: pd.merge(x, y, on = 'Date'), df_from_each_file)
df_full = df_full.set_index('Date')
df_full = df_full.pct_change().dropna()

def neg_sharpe_ratio(weights, mean_returns, cov_matrix):
	return -np.dot(weights, mean_returns)/np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

def plot_portfolios(num_in_set, num_assets, df_full):
	all_sets = list(itertools.combinations(range(num_assets), num_in_set))
	max_sr = -1.
	max_sr_ind = []
	max_sr_weights = []
	max_sr_plt_index = []
	opt_vars = []
	opt_rets = []
	for idx, ind_set in enumerate(all_sets):
		df_set = df_full[df_full.columns[list(ind_set)]]
		mean_returns = df_set.mean()
		cov_matrix = df_set.cov()
		args = (mean_returns, cov_matrix)
		constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
		bound = (0.0,1.0)
		bounds = tuple(bound for asset in range(num_in_set))
		result = sco.minimize(neg_sharpe_ratio, num_in_set*[1./num_in_set,], args=args,
			method='SLSQP', bounds=bounds, constraints=constraints)

		opt_weights = result.x
		portfolio_var = np.dot(opt_weights.T, np.dot(cov_matrix, opt_weights))
		portfolio_ret = np.dot(opt_weights, mean_returns)
		annual_sr = portfolio_ret/np.sqrt(portfolio_var)*np.sqrt(252)
		opt_vars.append(portfolio_var)
		opt_rets.append(portfolio_ret)
		if annual_sr > max_sr:
			max_sr = annual_sr
			max_sr_ind = list(ind_set)
			max_sr_weights = opt_weights
			max_sr_plt_index = idx

	highlight_x = opt_vars[max_sr_plt_index]
	highlight_y = opt_rets[max_sr_plt_index]
	highlight_names_str = ", ".join(df_full.columns[max_sr_ind].values)
	max_sr_weights_str = ", ".join([f'{elem:.3%}' for elem in max_sr_weights])
	print()
	print(f"{num_in_set}-Asset Portfolio with Maximum Sharpe Ratio")
	print(f"Asset Names:\t{highlight_names_str}".expandtabs(25))
	print(f"Weights:\t{max_sr_weights_str}".expandtabs(25))
	print(f"Daily Variance:\t{highlight_x:.3e}".expandtabs(25))
	print(f"Daily Return:\t{highlight_y:.3e}".expandtabs(25))
	print(f"Annual Sharpe Ratio:\t{round(max_sr,3)}".expandtabs(25))
	
	if num_in_set < num_assets:
		plt.scatter(opt_vars, opt_rets)
		plt.plot(highlight_x, highlight_y, 'ro')
		plt.xlabel("Variance")
		plt.ylabel("Return")
		plt.title(f"Best Sharpe Ratio {num_in_set}-Asset Portfolios")
		plt.show()

num_in_set = 2
plot_portfolios(num_in_set, num_assets, df_full)
num_in_set = 3
plot_portfolios(num_in_set, num_assets, df_full)
num_in_set = 5
plot_portfolios(num_in_set, num_assets, df_full)
num_in_set = num_assets
plot_portfolios(num_in_set, num_assets, df_full)