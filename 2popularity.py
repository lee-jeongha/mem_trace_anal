# -*- coding: utf-8 -*-

import argparse
parser = argparse.ArgumentParser(description="plot popularity graph")
parser.add_argument("--input", "-i", metavar='I', type=str, nargs='?', default='input.txt',
                    help='input file')
parser.add_argument("--output", "-o", metavar='O', type=str, nargs='?', default='output.txt',
                    help='output file')
parser.add_argument("--zipf", "-z", action='store_true',
                    help='calculate zipf parameter')
args = parser.parse_args()


import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

def save_csv(df, filename, index=0):
  try:
    if index==0:
      df.to_csv(filename, index=True, header=True, mode='w') # encoding='utf-8-sig'
    else: #append mode
      df.to_csv(filename, index=True, header=False, mode='a') # encoding='utf-8-sig'
  except OSError:	# OSError: Cannot save file into a non-existent directory: '~'
    #if not os.path.exists(path):
    target_dir = filename.rfind('/')
    path = filename[:target_dir]
    os.mkdir(path)
    #---
    if index==0:
      df.to_csv(filename, index=True, header=True, mode='w') # encoding='utf-8-sig'
    else: #append mode
      df.to_csv(filename, index=True, header=False, mode='a') # encoding='utf-8-sig'

"""##**memdf2 = tendency of memory block access**
**memdf2.1**
* x axis : ranking by references count
* y axis : reference count

**memdf2.2**
* x axis : ranking by % of reference count (in percentile form)
* y axis : % of reference count
"""

"""memdf2.1"""

memdf2 = pd.read_csv(args.input, sep=',', header=0, index_col=0, on_bad_lines='skip')
memdf2_rw = pd.read_csv(args.input[:-4]+'_rw.csv', sep=',', header=0, index_col=0, on_bad_lines='skip')

# ranking
memdf2['read_rank'] = memdf2['readcount'].rank(ascending=False)
memdf2['write_rank'] = memdf2['writecount'].rank(ascending=False)
memdf2_rw['rw_rank'] = memdf2_rw['count'].rank(ascending=False)
#print(memdf2)
#print(memdf2_rw)

"""memdf2.2"""

total_read = memdf2['readcount'].sum()
total_write = memdf2['writecount'].sum()
total_rw = memdf2_rw['count'].sum()
#print(total_read, total_write, total_rw)

# percentage
memdf2['readpcnt'] = (memdf2['readcount'] / total_read)
memdf2['writepcnt'] = (memdf2['writecount'] / total_write)
memdf2_rw['rwpcnt'] = (memdf2_rw['count'] / total_rw)

# ranking in percentile form
memdf2['read_rank_pcnt'] = memdf2['readpcnt'].rank(ascending=False, pct=True)
memdf2['write_rank_pcnt'] = memdf2['writepcnt'].rank(ascending=False, pct=True)
memdf2_rw['rw_rank_pcnt'] = memdf2_rw['rwpcnt'].rank(ascending=False, pct=True)
#print(memdf2)
#print(memdf2_rw)
save_csv(memdf2, args.output, 0)
save_csv(memdf2_rw, args.output[:-4]+'_rw.csv', 0)

"""zipf"""

from scipy.optimize import minimize

if args.zipf:
  def loglik(b, x, freqs):  
    # Power law function
    Probabilities = x**(-b)

    # Normalized
    Probabilities = Probabilities/Probabilities.sum()

    # Log Likelihoood
    Lvector = np.log(Probabilities)

    # Multiply the vector by frequencies
    Lvector = np.log(Probabilities) * freqs

    # LL is the sum
    L = Lvector.sum()

    # We want to maximize LogLikelihood or minimize (-1)*LogLikelihood
    return(-L)

  def zipf_param(freqs):
    freqs = freqs[freqs != 0]
    y = freqs.sort_values(ascending=False).to_numpy()

    x = np.array(range(1,len(y)+1))

    s_best = minimize(loglik, [2], args=(x, y))
    return s_best


"""memdf2.1 graph"""

#memdf2 = pd.read_csv(args.output, sep=',', header=0, index_col=0, on_bad_lines='skip')
#memdf2_rw = pd.read_csv(args.output[:-4]+'_rw.csv', sep=',', header=0, index_col=0, on_bad_lines='skip')

"""
plt.figure(figsize=(12,10))
plt.rcParams.update({'font.size': 17})

#read
x1 = memdf2['read_rank']
y1 = memdf2['readcount']
#write
x2 = memdf2['write_rank']
y2 = memdf2['writecount']
#read+write
x3 = memdf2_rw['rw_rank']
y3 = memdf2_rw['count']

#scatter
plt.scatter(x1, y1, color='blue', label='read', s=7)
plt.scatter(x2, y2, color='red', label='write', s=7)
plt.scatter(x3, y3, color='green', label='read+write', s=7)
plt.xscale('log')
plt.yscale('log')
plt.ylim([0.5,1e5])

if args.zipf:
  s_best1 = zipf_param(x1, y1)
  s_best2 = zipf_param(x2, y2)
  s_best3 = zipf_param(x3, y3)
  plt.plot(x1, (2*y1.max())*x1**-s_best1.x, color="skyblue", lw=2, label = "fitted MLE"+str(-s_best1.x))
  plt.plot(x2, (2*y2.max())*x2**-s_best2.x, color="salmon", lw=2, label = "fitted MLE"+str(-s_best2.x))
  plt.plot(x3, (2*y3.max())*x3**-s_best3.x, color="limegreen", lw=2, label = "fitted MLE"+str(-s_best3.x))

# legend
plt.xlabel('ranking')
plt.ylabel('memory block access count')
plt.legend(loc='upper right', ncol=1)

# plt.show()
plt.savefig(args.output[:-4]+'.png', dpi=300)
"""

fig, ax = plt.subplots(2, figsize=(7,6), constrained_layout=True, sharex=True, sharey=True) # sharex=True: share x axis
# figsize=(11,10), 

font_size=20
parameters = {'axes.labelsize': font_size, 'axes.titlesize': font_size, 'xtick.labelsize': font_size, 'ytick.labelsize': font_size}
plt.rcParams.update(parameters)

#read
x1 = memdf2['read_rank']
y1 = memdf2['readcount']
#write
x2 = memdf2['write_rank']
y2 = memdf2['writecount']
#read+write
x3 = memdf2_rw['rw_rank']
y3 = memdf2_rw['count']

# read/write graph
ax[0].scatter(x1, y1, color='blue', label='read', s=5)
ax[0].scatter(x2, y2, color='red', label='write', s=5)

if args.zipf:
  s_best1 = zipf_param(y1)
  s_best2 = zipf_param(y2)
  ax[0].plot(x1, (2*y1.max())*x1**-s_best1.x, color="skyblue", lw=2, label = "fitted MLE"+str(-s_best1.x))
  ax[0].plot(x2, (2*y2.max())*x2**-s_best2.x, color="salmon", lw=2, label = "fitted MLE"+str(-s_best2.x))

# legend
ax[0].set_xlabel('ranking')
ax[0].set_ylabel('memory block access count')
ax[0].legend(loc=(1.0,0.8), ncol=1) #loc = 'best', 'upper right'

# read+write graph
ax[1].scatter(x3, y3, color='green', label='read&write', s=5)
ax[1].set_ylim([0.5,1e5])
ax[1].set_xscale('log')
ax[1].set_yscale('log')

if args.zipf:
  s_best3 = zipf_param(y3)
  ax[1].plot(x3, (2*y3.max())*x3**-s_best3.x, color="limegreen", lw=2, label = "fitted MLE"+str(-s_best3.x))

# legend
ax[1].set_xlabel('ranking')
ax[1].set_ylabel('memory block access count')
ax[1].legend(loc=(1.0,0.8), ncol=1) #loc = 'best'


#plt.show()
plt.savefig(args.output[:-4]+'.png', dpi=300)

"""memdf2.2 graph"""

"""
#plt.figure(figsize=(12,10))

#read
x1 = memdf2['read_rank_pcnt']
y1 = memdf2['readpcnt']
#write
x2 = memdf2['write_rank_pcnt']
y2 = memdf2['writepcnt']
#read+write
x3 = memdf2_rw['rw_rank_pcnt']
y3 = memdf2_rw['rwpcnt']

#scatter
plt.scatter(x1, y1, color='blue', label='read', s=5)
plt.scatter(x2, y2, color='red', label='write', s=5)
plt.scatter(x3, y3, color='green', label='read+write', s=5)

# legend
plt.xlabel('ranking (in % form)')
plt.ylabel('% of reference count')
plt.legend(loc='upper right', ncol=1)

plt.show()
#plt.savefig(args.output[:-4]+'.png', dpi=300)
"""
