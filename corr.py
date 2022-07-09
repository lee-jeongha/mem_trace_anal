import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("-i", type=str, nargs="?")
args = parser.parse_args()

df = pd.read_csv(args.i, header=0, index_col=0)
print(df)

col_type = 'type_pcnt_rank' # 'type_rank'

#---
read = df[['blockaddress',col_type]][(df['type']=='read')]
read_l = len(read) #// 10
read = read.sort_values(by=col_type, ascending=True)[:read_l]

write = df[['blockaddress',col_type]][(df['type']=='write')]
write_l = len(write) #// 10
write = write.sort_values(by=col_type, ascending=True)[:write_l]

rw = df[['blockaddress',col_type]][(df['type']=='read&write')]
rw_l = len(rw) #// 10
rw = rw.sort_values(by=col_type, ascending=True)[:rw_l]
#---

rw_merge = pd.merge(read, write, left_on='blockaddress', right_on='blockaddress', how='outer', suffixes = ['_read', '_write'])#, lsuffix='_read', rsuffix='_write')
print(rw_merge)

#---
only_read = rw_merge[rw_merge[col_type + '_write'].isnull()]
only_write = rw_merge[rw_merge[col_type + '_read'].isnull()]
#---
print("only_read percentage",len(only_read)/len(rw_merge), "only_write percentage",len(only_write)/len(rw_merge))
rw_merge = rw_merge.dropna()
print("\nrw_merge\n",rw_merge, "\nonly_read\n",only_read, "\nonly_write\n",only_write)

#---
"""rw_merge[col_type + '_read'] = rw_merge[col_type + '_read'].fillna(value=1)
rw_merge[col_type + '_write'] = rw_merge[col_type + '_write'].fillna(value=1)"""
#print(rw_merge)
#---

print(rw_merge.corr())

#---
import matplotlib.pyplot as plt

plt.scatter(rw_merge[col_type + '_read'], rw_merge[col_type + '_write'])
plt.show()

#---
import seaborn as sns

sns.jointplot(rw_merge[col_type + '_read'], rw_merge[col_type + '_write'])
sns.jointplot(rw_merge[col_type + '_read'], rw_merge[col_type + '_write'], kind="hex", color="#4CB391")
sns.jointplot(rw_merge[col_type + '_read'], rw_merge[col_type + '_write'], kind="hist", color="#4CB391")
sns.jointplot(rw_merge[col_type + '_read'], rw_merge[col_type + '_write'], kind="kde", color="#4CB391")
#---

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