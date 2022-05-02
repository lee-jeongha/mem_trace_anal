# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def save_csv(df, filename="output.csv", index=0):
  #if not os.path.exists('memdf.csv'):
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

memdf2 = pd.read_csv('memdf1.csv', sep=',', header=0, index_col=0, error_bad_lines=False)
memdf2_rw = pd.read_csv('memdf1_rw.csv', sep=',', header=0, index_col=0, error_bad_lines=False)

# ranking
memdf2['read_rank'] = memdf2['readcount'].rank(ascending=False)
memdf2['write_rank'] = memdf2['writecount'].rank(ascending=False)
memdf2_rw['rw_rank'] = memdf2_rw['count'].rank(ascending=False)

print(memdf2)
print(memdf2_rw)
#memdf2.to_csv("./memdf2.csv")
#memdf2_rw.to_csv("./memdf2_rw.csv")

"""memdf2.2"""

total_read = memdf2['readcount'].sum()
total_write = memdf2['writecount'].sum()
total_rw = memdf2_rw['count'].sum()
print(total_read, total_write, total_rw)

# percentage
memdf2['readpcnt'] = (memdf2['readcount'] / total_read)
memdf2['writepcnt'] = (memdf2['writecount'] / total_write)
memdf2_rw['rwpcnt'] = (memdf2_rw['count'] / total_rw)

# ranking in percentile form
memdf2['read_rank_pcnt'] = memdf2['readpcnt'].rank(ascending=False, pct=True)
memdf2['write_rank_pcnt'] = memdf2['writepcnt'].rank(ascending=False, pct=True)
memdf2_rw['rw_rank_pcnt'] = memdf2_rw['rwpcnt'].rank(ascending=False, pct=True)

print(memdf2)
print(memdf2_rw)
#memdf2.to_csv("./memdf2.csv")
#memdf2_rw.to_csv("./memdf2_rw.csv")

"""memdf2.1 graph"""

#plt.figure(figsize=(12,10))

#read
x1 = memdf2['read_rank']
y1 = memdf2['readcount']
#write
x2 = memdf2['write_rank']
y2 = memdf2['writecount']

#scatter
plt.scatter(x1, y1, color='blue', label='read', s=5)
plt.scatter(x2, y2, color='red', label='write', s=5)

#plt.xscale('log')

# legend
plt.xlabel('ranking')
plt.ylabel('memory block access count')
plt.legend(loc='upper right', ncol=1)

plt.show()

#plt.figure(figsize=(12,10))

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
plt.scatter(x1, y1, color='blue', label='read', s=5)
plt.scatter(x2, y2, color='red', label='write', s=5)
#plt.scatter(x3, y3, color='green', label='read+write', s=5)
plt.xscale('log')
plt.yscale('log')
plt.ylim([0.5,1e5])

# legend
plt.xlabel('ranking')
plt.ylabel('memory block access count')
plt.legend(loc='upper right', ncol=1)

plt.show()

#plt.figure(figsize=(12,10))

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
plt.scatter(x1, y1, color='blue', label='read', s=5)
plt.scatter(x2, y2, color='red', label='write', s=5)
plt.scatter(x3, y3, color='green', label='read+write', s=5)

# legend
plt.xlabel('ranking')
plt.ylabel('memory block access count')
plt.legend(loc='upper right', ncol=1)

plt.show()

#plt.figure(figsize=(12,10))

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
plt.scatter(x1, y1, color='blue', label='read', s=5)
plt.scatter(x2, y2, color='red', label='write', s=5)
plt.scatter(x3, y3, color='green', label='read+write', s=5)
plt.xscale('log')
plt.yscale('log')

# legend
plt.xlabel('ranking')
plt.ylabel('memory block access count')
plt.legend(loc='upper right', ncol=1)

plt.show()

fig, ax = plt.subplots(2, figsize=(11,10), constrained_layout=True, sharex=True, sharey=True) # sharex=True: share x axis

#read
x1 = memdf2['read_rank']
y1 = memdf2['readcount']
#write
x2 = memdf2['write_rank']
y2 = memdf2['writecount']
#read+write
x3 = memdf2_rw['rw_rank']
y3 = memdf2_rw['count']


# read graph
ax[0].scatter(x1, y1, color='blue', label='read', s=5)
ax[0].scatter(x2, y2, color='red', label='write', s=5)
#ax[0].set_xscale('log')
#ax[0].set_yscale('log')

# legend
ax[0].set_xlabel('ranking')
ax[0].set_ylabel('memory block access count')
ax[0].legend(loc=(1.0,0.8), ncol=1) #loc = 'best', 'upper right'

# write graph
ax[1].scatter(x3, y3, color='green', label='read/write', s=5)
ax[1].set_ylim([0.5,1e5])
ax[1].set_xscale('log')
ax[1].set_yscale('log')
# legend
ax[1].set_xlabel('ranking')
ax[1].set_ylabel('memory block access count')
ax[1].legend(loc=(1.0,0.8), ncol=1) #loc = 'best'


plt.show()
#plt.savefig('cachegrind-v3.5.3.png', dpi=300)

"""memdf2.2 graph"""

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
#plt.savefig('cachegrind-v3.4.png', dpi=300)
