import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("-i", type=str, nargs="?")
args = parser.parse_args()

df = pd.read_csv(args.i, header=0, index_col=0)
print(df)

#---
"""read = df[['blockaddress','type_rank']][(df['type']=='read')]
read_l = len(read) #// 5
read = read.sort_values(by='type_rank', ascending=True)[:read_l]

write = df[['blockaddress','type_rank']][(df['type']=='write')]
write_l = len(write) #// 5
write = write.sort_values(by='type_rank', ascending=True)[:write_l]

rw = df[['blockaddress','type_rank']][(df['type']=='read&write')]
rw_l = len(rw) #// 5
rw = rw.sort_values(by='type_rank', ascending=True)[:rw_l]"""
#---
read = df[['blockaddress','type_pcnt_rank']][(df['type']=='read')]
read_l = len(read) #// 10
read = read.sort_values(by='type_pcnt_rank', ascending=True)[:read_l]

write = df[['blockaddress','type_pcnt_rank']][(df['type']=='write')]
write_l = len(write) #// 10
write = write.sort_values(by='type_pcnt_rank', ascending=True)[:write_l]

rw = df[['blockaddress','type_pcnt_rank']][(df['type']=='read&write')]
rw_l = len(rw) #// 10
rw = rw.sort_values(by='type_pcnt_rank', ascending=True)[:rw_l]
#---

rw_merge = pd.merge(read, write, left_on='blockaddress', right_on='blockaddress', how='outer', suffixes = ['_read', '_write'])#, lsuffix='_read', rsuffix='_write')
print(rw_merge)

#---
#only_read = rw_merge[rw_merge['type_rank_write'].isnull()]
#only_write = rw_merge[rw_merge['type_rank_read'].isnull()]
#---
only_read = rw_merge[rw_merge['type_pcnt_rank_write'].isnull()]
only_write = rw_merge[rw_merge['type_pcnt_rank_read'].isnull()]
#---
print("only_read percentage",len(only_read)/len(rw_merge), "only_write percentage",len(only_write)/len(rw_merge))
rw_merge = rw_merge.dropna()
print("rw_merge\n",rw_merge, "only_read\n",only_read, "only_write\n",only_write)

#---
#rw_merge['type_rank_read'] = rw_merge['type_rank_read'].fillna(value=read_l)
#rw_merge['type_rank_write'] = rw_merge['type_rank_write'].fillna(value=write_l)
#---
"""rw_merge['type_pcnt_rank_read'] = rw_merge['type_pcnt_rank_read'].fillna(value=1)
rw_merge['type_pcnt_rank_write'] = rw_merge['type_pcnt_rank_write'].fillna(value=1)"""
#---
#print(rw_merge)

print(rw_merge.corr())

import matplotlib.pyplot as plt
#plt.scatter(rw_merge['type_rank_read'], rw_merge['type_rank_write'])
plt.scatter(rw_merge['type_pcnt_rank_read'], rw_merge['type_pcnt_rank_write'])
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