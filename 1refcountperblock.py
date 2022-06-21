# -*- coding: utf-8 -*-

import argparse
parser = argparse.ArgumentParser(description="plot reference count per each block")
parser.add_argument("--input", "-i", metavar='I', type=str, nargs='?', default='input.txt',
                    help='input file')
parser.add_argument("--output", "-o", metavar='O', type=str, nargs='?', default='output.txt',
                    help='output file')
parser.add_argument("--histogram", "-h", action='store_true',
                    help='plot histogram bound by reference count')
parser.add_argument("--title", "-t", metavar='T', type=str, nargs='?', default='',
                    help='title of a graph')
args = parser.parse_args()


import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import math

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

"""##**memdf1 = access count**
* x axis : (virtual) memory block address
* y axis : memory block access count
"""

def address_ref(inputdf, concat=False):
  if (concat) :
    df = inputdf.groupby(by=['blockaddress', 'type'], as_index=False).sum()
    #print(df)
  else :
    inputdf = inputdf.replace('readi', 'read')
    inputdf = inputdf.replace('readd', 'read')

    df = inputdf.groupby(['blockaddress', 'type'])['blockaddress'].count().reset_index(name='count') # 'blockaddress'와 'type'을 기준으로 묶어서 세고, 이 이름은 'count'로

  return df

## 1. use list of chunk
"""
memdf = pd.read_csv('memdf.csv', sep=',', chunksize=1000000, header=0, index_col=0, error_bad_lines=False)
memdf = list(memdf)
print(memdf[-1].head)
print(memdf[0].head)
#---
df1 = pd.DataFrame()
df1_rw = pd.DataFrame()
for i in range(len(memdf)):
  memdf = pd.read_csv(memdf[i], sep=',', header=0, index_col=0, error_bad_lines=False)
  df = address_ref(memdf, concat=False)
  df1 = pd.concat([df1, df])
"""

## 2. load separate .csv file
df1 = pd.DataFrame()
df1_rw = pd.DataFrame()
for i in range(100): #under 
  filename = args.input+'_'+str(i)+'.csv'
  try:
    memdf = pd.read_csv(filename, sep=',', header=0, index_col=0, on_bad_lines='skip')
    df = address_ref(memdf, concat=False)
    df1 = pd.concat([df1, df])
  except FileNotFoundError:
    print("No file named: ", filename)
    break

df1 = address_ref(df1, concat=True)

#both read and write
df1_rw = df1.groupby(by=['blockaddress'], as_index=False).sum()
df1_rw['type'] = 'read&write'

df1 = pd.concat([df1, df1_rw], sort=True)
save_csv(df1, args.output, 0)

"""**memdf1 graph**
> Specify the axis range (manual margin adjustment required)
"""

memdf1 = pd.read_csv(args.output, sep=',', header=0, index_col=0, on_bad_lines='skip')

def digit_length(n):
    return int(math.log10(n)) + 1 if n else 0

x1 = memdf1['blockaddress'][(memdf1['type']=='read')]
x2 = memdf1['blockaddress'][(memdf1['type']=='write')]
x3 = memdf1['blockaddress'][(memdf1['type']=='read&write')]
y1 = memdf1['count'][(memdf1['type']=='read')]
y2 = memdf1['count'][(memdf1['type']=='write')]
y3 = memdf1['count'][(memdf1['type']=='read&write')]

"""
#plt.style.use('default')
plt.rcParams['figure.figsize'] = (24, 20)
#plt.rcParams['font.size'] = 12

# scatter
print(x1.max(), x2.max())
print(y1.max(), y2.max())
#plt.axis([0-1e6, memdf1['blockaddress'].max()+1e6, 0-2, max(y1.max(), y2.max())+10]) # [xmin, xmax, ymin, ymax]

plt.scatter(x1, y1, color='blue', label='read', s=5) #aquamarine
plt.scatter(x2, y2, color='red', label='write', s=5) #salmon

# legend
plt.xlabel('(virtual) memory block address')
plt.ylabel('memory block reference count')
plt.legend(loc='upper right', ncol=1) #loc = 'best'
#plt.margins(x=5)

plt.show()
"""
"""
plt.figure(figsize = (12, 10))

# scatter
print(x1.max(), x2.max(), x3.max())
print(y1.max(), y2.max(), y3.max())
#plt.axis([0-1e6, memdf1['blockaddress'].max()+1e6, 0-2, max(y1.max(), y2.max(), y3.max())+10]) # [xmin, xmax, ymin, ymax]

plt.scatter(x1, y1, color='blue', label='read', s=5)
plt.scatter(x2, y2, color='red', label='write', s=5)
plt.scatter(x3, y3, color='green', label='read&write', s=5)

# legend
plt.xlabel('(virtual) memory block address')
plt.ylabel('memory block reference count')
plt.legend(loc='upper right', ncol=1) #loc = 'best'
#plt.margins(x=5)

plt.show()
"""
fig, ax = plt.subplots(2, figsize=(6,6), constrained_layout=True, sharex=True, sharey=True)

font_size=17
parameters = {'axes.labelsize': font_size, 'axes.titlesize': font_size, 'xtick.labelsize': font_size, 'ytick.labelsize': font_size}
plt.rcParams.update(parameters)
#plt.axis([0-1e6, memdf1['blockaddress'].max()+1e6, 0-2, max(y1.max(), y2.max())+10]) # [xmin, xmax, ymin, ymax]

if args.title != '':
  plt.suptitle(args.title, fontsize=17)

print(x1.max(), x2.max())
print(y1.min(), y1.max(), digit_length(y1.max()))
print(y2.min(), y2.max(), digit_length(y2.max()))

# read graph
ax[0].scatter(x1, y1, color='blue', label='read', s=5)
ax[0].legend(loc='upper right', ncol=1) #loc = 'best'

# write graph
ax[1].scatter(x2, y2, color='red', label='write', s=5)
ax[1].legend(loc='upper right', ncol=1) #loc = 'best'

fig.supxlabel('(virtual) memory block address', fontsize=17)
fig.supylabel('memory block reference count', fontsize=17)

#plt.show()
plt.savefig(args.output[:-4]+'.png', dpi=300)

if (args.histogram):
  plt.clf() # Clear the current figure

  fig, ax = plt.subplots(2, figsize=(6,6), constrained_layout=True, sharex=True, sharey=True)
  plt.xscale('log')

  if args.title != '':
    plt.suptitle(args.title, fontsize=17)

  if(y1.max() < y2.max()):
    bin_list = [0]
    bin_list.extend([ 10**i for i in range(digit_length(y1.max()) + 1) ])
  else:
    bin_list = [0]
    bin_list.extend([ 10**i for i in range(digit_length(y2.max()) + 1) ])

  # read graph
  height1, _, _ = ax[0].hist(y1, color='blue', edgecolor='black', label='read', bins=bin_list, cumulative=False, density=False)
  print(height1)
  ax[0].legend(loc='upper right', ncol=1) #loc = 'best'

  # write graph
  height2, _, _ = ax[1].hist(y2, color='red', edgecolor='black', label='write', bins=bin_list, cumulative=False, density=False)
  print(height2)
  ax[1].legend(loc='upper right', ncol=1) #loc = 'best'

  fig.supxlabel('reference count', fontsize=17 )
  fig.supylabel('# of memory block', fontsize=17)

  #plt.show()
  plt.savefig(args.output[:-4]+'_hist.png', dpi=300)