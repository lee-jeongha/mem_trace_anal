import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("-i", type=str, nargs="?")
args = parser.parse_args()

df = pd.read_csv(args.i, header=0, index_col=0)
print(df)

read = df[['blockaddress','type_rank']][(df['type']=='read')]
read_l = len(read)

write = df[['blockaddress','type_rank']][(df['type']=='write')]
write_l = len(write)

rw = df[['blockaddress','type_rank']][(df['type']=='read&write')]
rw_l = len(rw)

rw_join = read.join(write.set_index('blockaddress'), on='blockaddress', lsuffix='_read', rsuffix='_write')
#print(rw_join)

rw_join['type_rank_read'] = rw_join['type_rank_read'].fillna(value=read_l)
rw_join['type_rank_write'] = rw_join['type_rank_write'].fillna(value=write_l)
#print(rw_join)

rw_join[:1000]

print(rw_join.corr())

import matplotlib.pyplot as plt
plt.scatter(rw_join['type_rank_read'][:1000], rw_join['type_rank_write'][:1000])
plt.show()
"""
from scipy.optimize import curve_fit
import numpy as np

def func_powerlaw(x, m, c):
    return x ** m * c

def func_log(x,n):
    return n ** x

def zipf_param(freqs):

    target_func = func_log

    freqs = freqs[freqs != 0]
    #y = freqs.sort_values(ascending=False).to_numpy()
    #x = np.array(range(1, len(y) + 1))
    y = freqs.sort_values(ascending=False).cumsum().to_numpy()
    x = np.arange(len(y))
    x = (x / len(y))

    popt, pcov = curve_fit(target_func, y, x, maxfev=2000)
    print(popt)

    return popt

param=df['type_pcnt'][(df['type']=='read')].sort_values(ascending=False)
p = zipf_param(param)

param_x = np.arange(len(param))
param_x = (param_x / len(param))

plt.scatter(param_x, param.cumsum())
plt.plot(func_log(param.cumsum(), p), param.cumsum())
plt.show()

#np.polyfit(np.log(param_x), param.cumsum(), 1)
"""