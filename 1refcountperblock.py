# -*- coding: utf-8 -*-

import argparse
parser = argparse.ArgumentParser(description="plot reference count per each block")
parser.add_argument("--input", "-i", metavar='I', type=str, nargs='?', default='input.txt',
                    help='input file')
parser.add_argument("--output", "-o", metavar='O', type=str, nargs='?', default='output.txt',
                    help='output file')
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
'''
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
'''

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

#only read
df1['readcount'] = df1['count']
df1.loc[(df1.type=='write'), 'readcount'] = 0
#only write
df1['writecount'] = df1['count']
df1.loc[(df1.type!='write'), 'writecount'] = 0
#read and write
df1_rw = df1.groupby(by=['blockaddress'], as_index=False).sum()

print(len(df1), len(df1_rw))
#print(df1, df1_rw)

save_csv(df1, args.output, 0)
save_csv(df1_rw, args.output[:-4]+'_rw.csv', 0)

"""**memdf1 graph**
> Specify the axis range (manual margin adjustment required)
"""

memdf1 = pd.read_csv(args.output, sep=',', header=0, index_col=0, on_bad_lines='skip')
memdf1_rw = pd.read_csv(args.output[:-4]+'_rw.csv', sep=',', header=0, index_col=0, on_bad_lines='skip')

"""
#plt.style.use('default')
plt.rcParams['figure.figsize'] = (24, 20)
#plt.rcParams['font.size'] = 12

# scatter
x = memdf1['blockaddress']
y1 = memdf1['readcount']
y2 = memdf1['writecount']
print(x.min(), x.max())
print(y1.max(), y2.max())
plt.axis([0-1e6, memdf1['blockaddress'].max()+1e6, 0-2, max(y1.max(), y2.max())+10]) # [xmin, xmax, ymin, ymax]

plt.scatter(x, y1, color='blue', label='read', s=5) #aquamarine
plt.scatter(x, y2, color='red', label='write', s=5) #salmon

# legend
plt.xlabel('(virtual) memory block address')
plt.ylabel('memory block access count')
plt.legend(loc='upper right', ncol=1) #loc = 'best'
#plt.margins(x=5)

plt.show()
"""
"""
plt.figure(figsize = (12, 10))

# scatter
x = memdf1['blockaddress']
x3 = memdf1_rw['blockaddress']
y1 = memdf1['readcount']
y2 = memdf1['writecount']
y3 = memdf1_rw['count']
print(x.min(), x.max())
print(y1.max(), y2.max(), y3.max())
plt.axis([0-1e6, memdf1['blockaddress'].max()+1e6, 0-2, max(y1.max(), y2.max(), y3.max())+10]) # [xmin, xmax, ymin, ymax]

plt.scatter(x, y1, color='blue', label='read', s=5)
plt.scatter(x, y2, color='red', label='write', s=5)
plt.scatter(x3, y3, color='green', label='read+write', s=5)

# legend
plt.xlabel('(virtual) memory block address')
plt.ylabel('memory block access count')
plt.legend(loc='upper right', ncol=1) #loc = 'best'
#plt.margins(x=5)

plt.show()
"""

'''#fig, ax = plt.subplots()
fig = plt.figure()
ax = fig.add_axes([0, 0, 1, 1])'''

fig, ax = plt.subplots(2, constrained_layout=True, sharex=True, sharey=True) # sharex=True

# scatter
x = memdf1['blockaddress']
y1 = memdf1['readcount']
y2 = memdf1['writecount']
print(x.min(), x.max())
print(y1.max(), y2.max())
#plt.axis([0-1e6, memdf1['blockaddress'].max()+1e6, 0-2, max(y1.max(), y2.max())+10]) # [xmin, xmax, ymin, ymax]

# read graph
ax[0].scatter(x, y1, color='blue', label='read', s=5)
# legend
ax[0].set_xlabel('(virtual) memory block address')
ax[0].set_ylabel('memory block access count')
ax[0].legend(loc='upper right', ncol=1) #loc = 'best'

# write graph
ax[1].scatter(x, y2, color='red', label='write', s=5)
# legend
ax[1].set_xlabel('(virtual) memory block address')
ax[1].set_ylabel('memory block access count')
ax[1].legend(loc='upper right', ncol=1) #loc = 'best'

#plt.show()
plt.savefig(args.output[:-4]+'.png', dpi=300)

"""
#plt.figure(figsize = (20, 24))
fig, ax = plt.subplots(3, figsize=(12,10), constrained_layout=True, sharex=True, sharey=True) # sharex=True, sharey=True

# scatter
x = memdf1['blockaddress']
x3 = memdf1_rw['blockaddress']
y1 = memdf1['readcount']
y2 = memdf1['writecount']
y3 = memdf1_rw['count']
print(x.min(), x.max())
print(y1.max(), y2.max(), y3.max())
plt.axis([0-1e6, memdf1['blockaddress'].max()+1e6, 0-2, max(y1.max(), y2.max(), y3.max())+10]) # [xmin, xmax, ymin, ymax]

# read graph
ax[0].scatter(x, y1, color='blue', label='read', s=5) #aquamarine
# legend
#ax[0].set_xlabel('(virtual) memory block address')
ax[0].set_ylabel('memory block access count')
ax[0].legend(loc='upper right', ncol=1) #loc = 'best'

# write graph
ax[1].scatter(x, y2, color='red', label='write', s=5) #salmon
# legend
#ax[1].set_xlabel('(virtual) memory block address')
ax[1].set_ylabel('memory block access count')
ax[1].legend(loc='upper right', ncol=1) #loc = 'best'

# read+write graph
ax[2].scatter(x3, y3, color='green', label='read+write', s=5)
# legend
ax[2].set_xlabel('(virtual) memory block address')
ax[2].set_ylabel('memory block access count')
ax[2].legend(loc='upper right', ncol=1) #loc = 'best'

plt.show()
"""
