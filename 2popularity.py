# -*- coding: utf-8 -*-

import argparse
parser = argparse.ArgumentParser(description="plot popularity graph")
parser.add_argument("--input", "-i", metavar='I', type=str, nargs='?', default='input.txt',
                    help='input file')
parser.add_argument("--output", "-o", metavar='O', type=str, nargs='?', default='output.txt',
                    help='output file')
parser.add_argument("--zipf", "-z", action='store_true',
                    help='calculate zipf parameter')
parser.add_argument("--title", "-t", metavar='T', type=str, nargs='?', default='',
                    help='title of a graph')
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
    os.makedirs(path)
    #---
    if index==0:
      df.to_csv(filename, index=True, header=True, mode='w') # encoding='utf-8-sig'
    else: #append mode
      df.to_csv(filename, index=True, header=False, mode='a') # encoding='utf-8-sig'

"""##**memdf2 = tendency of memory block access**"""
memdf2 = pd.read_csv(args.input, sep=',', header=0, index_col=0, on_bad_lines='skip')

"""memdf2.1
* x axis : ranking by references count
* y axis : reference count
"""
# ranking
read_rank = memdf2['count'][(memdf2['type']=='read')].rank(ascending=False)
memdf2.loc[(memdf2['type']=='read'), ['type_rank']] = read_rank

write_rank = memdf2['count'][(memdf2['type']=='write')].rank(ascending=False)
memdf2.loc[(memdf2['type']=='write'), ['type_rank']] = write_rank

rw_rank = memdf2['count'][(memdf2['type']=='read&write')].rank(ascending=False)
memdf2.loc[(memdf2['type']=='read&write'), ['type_rank']] = rw_rank

"""memdf2.2
* x axis : ranking by % of reference count (in percentile form)
* y axis : % of reference count
"""
total_read = memdf2['count'][(memdf2['type']=='read')].sum()
total_write = memdf2['count'][(memdf2['type']=='write')].sum()
total_rw = memdf2['count'][(memdf2['type']=='read&write')].sum()

# percentage
memdf2['type_pcnt'] = memdf2['count']
memdf2.loc[(memdf2['type']=='read'), ['type_pcnt']] /= total_read
memdf2.loc[(memdf2['type']=='write'), ['type_pcnt']] /= total_write
memdf2.loc[(memdf2['type']=='read&write'), ['type_pcnt']] /= total_rw

# ranking in percentile form
read_rank = memdf2['type_pcnt'][(memdf2['type']=='read')].rank(ascending=False, pct=True)
memdf2.loc[(memdf2['type']=='read'), ['type_pcnt_rank']] = read_rank

write_rank = memdf2['type_pcnt'][(memdf2['type']=='write')].rank(ascending=False, pct=True)
memdf2.loc[(memdf2['type']=='write'), ['type_pcnt_rank']] = write_rank

rw_rank = memdf2['type_pcnt'][(memdf2['type']=='read&write')].rank(ascending=False, pct=True)
memdf2.loc[(memdf2['type']=='read&write'), ['type_pcnt_rank']] = rw_rank

save_csv(memdf2, args.output, 0)

"""zipf"""

if args.zipf:
  def func_powerlaw(x, m, c):
    return x ** m * c

  def zipf_param(freqs):
    from scipy.optimize import curve_fit

    target_func = func_powerlaw

    freqs = freqs[freqs != 0]
    y = freqs.sort_values(ascending=False).to_numpy()
    x = np.array(range(1, len(y) + 1))

    popt, pcov = curve_fit(target_func, x, y, maxfev=2000)
    #print(popt)

    return popt

"""memdf2.1 graph"""

#memdf2 = pd.read_csv(args.output, sep=',', header=0, index_col=0, on_bad_lines='skip')

#read
x1 = memdf2['type_rank'][(memdf2['type']=='read')]
y1 = memdf2['count'][(memdf2['type']=='read')]
#write
x2 = memdf2['type_rank'][(memdf2['type']=='write')]
y2 = memdf2['count'][(memdf2['type']=='write')]
#read&write
x3 = memdf2['type_rank'][(memdf2['type']=='read&write')]
y3 = memdf2['count'][(memdf2['type']=='read&write')]

"""
plt.figure(figsize=(12,10))
plt.rcParams.update({'font.size': 17})

#scatter
plt.scatter(x1, y1, color='blue', label='read', s=7)
plt.scatter(x2, y2, color='red', label='write', s=7)
plt.scatter(x3, y3, color='green', label='read&write', s=7)
plt.xscale('log')
plt.yscale('log')
plt.ylim([0.5,1e5])

if args.zipf:
  s_best1 = zipf_param(y1)
  s_best2 = zipf_param(y2)
  s_best3 = zipf_param(y3)
  plt.plot(x1, func_powerlaw(x1, *s_best1), color="skyblue", lw=2, label="curve_fitting: read")
  plt.plot(x2, func_powerlaw(x2, *s_best2), color="salmon", lw=2, label="curve_fitting: write")
  plt.plot(x3, func_powerlaw(x3, *s_best3), color="limegreen", lw=2, label="curve_fitting: read&write")
  
  plt.annotate(str(round(s_best1[0],5)), xy=(10, func_powerlaw(10, *s_best1)), xycoords='data',
               xytext=(-10.0, -70.0), textcoords="offset points", color="steelblue", size=13,
               arrowprops=dict(arrowstyle="->", ls="--", color="steelblue", connectionstyle="arc3,rad=-0.2"))
  plt.annotate(str(round(s_best2[0],5)), xy=(80, func_powerlaw(80, *s_best2)), xycoords='data',
               xytext=(-80.0, -30.0), textcoords="offset points", color="indianred", size=13,  # xytext=(-30.0, -50.0)
               arrowprops=dict(arrowstyle="->", ls="--", color="indianred", connectionstyle="arc3,rad=-0.2"))
  plt.annotate(str(round(s_best3[0],5)), xy=(100, func_powerlaw(100, *s_best3)), xycoords='data',
               xytext=(-10.0, -50.0), textcoords="offset points", color="olivedrab", size=13,  # xytext=(-80.0, -50.0)
               arrowprops=dict(arrowstyle="->", ls="--", color="olivedrab", connectionstyle="arc3,rad=-0.2"))
               
# legend
plt.xlabel('ranking')
plt.ylabel('memory block access count')
plt.legend(loc='lower left', ncol=1)

if args.title != '':
  plt.title(args.title, fontsize=25)

# plt.show()
plt.savefig(args.output[:-4]+'.png', dpi=300)
"""

fig, ax = plt.subplots(2, figsize=(7,8), constrained_layout=True, sharex=True, sharey=True) # sharex=True: share x axis
# figsize=(11,10), 

font_size=20
parameters = {'axes.labelsize': font_size, 'axes.titlesize': font_size, 'xtick.labelsize': font_size, 'ytick.labelsize': font_size}
plt.rcParams.update(parameters)

if args.title != '':
  plt.suptitle(args.title, fontsize=17)
plt.ylim([0.5,1e5])
plt.xscale('log')
plt.yscale('log')

# read/write graph
ax[0].scatter(x1, y1, color='blue', label='read', s=5)
ax[0].scatter(x2, y2, color='red', label='write', s=5)
if args.zipf:
  s_best1 = zipf_param(y1)
  s_best2 = zipf_param(y2)
  ax[0].plot(x1, func_powerlaw(x1, *s_best1), color="skyblue", lw=2, label="curve_fitting: read")
  ax[0].plot(x2, func_powerlaw(x2, *s_best2), color="salmon", lw=2, label="curve_fitting: write")
ax[0].legend(loc='lower left', ncol=1) #loc = 'best', 'upper right', (1.0,0.8)

# read+write graph
ax[1].scatter(x3, y3, color='green', label='read&write', s=5)
if args.zipf:
  s_best3 = zipf_param(y3)
  ax[1].plot(x3, func_powerlaw(x3, *s_best3), color="limegreen", lw=2, label = "curve_fitting: read&write")
ax[1].legend(loc='lower left', ncol=1) #loc = 'best', 'upper right', (1.0,0.8)

print(s_best1, s_best2, s_best3)

fig.supxlabel('rank', fontsize=17)
fig.supylabel('memory block reference count', fontsize=17)

#plt.show()
plt.savefig(args.output[:-4]+'.png', dpi=300)


"""memdf2.2 graph"""

"""
#plt.figure(figsize=(12,10))

#read
x1 = memdf2['type_pcnt_rank'][(memdf2['type']=='read')]
y1 = memdf2['type_pcnt'][(memdf2['type']=='read')]
#write
x2 = memdf2['type_pcnt_rank'][(memdf2['type']=='write')]
y2 = memdf2['type_pcnt'][(memdf2['type']=='write')]
#read&write
x3 = memdf2['type_pcnt_rank'][(memdf2['type']=='read&write')]
y3 = memdf2['type_pcnt'][(memdf2['type']=='read&write')]

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
