class LRUCache(object):

    def __init__(self):
        self.cache = []

    def get(self):
        ref_table = self.cache
        return ref_table

    def set(self, ref_table):
        self.cache = ref_table

    def reference(self, ref_address):
        if ref_address in self.cache:
            rank = self.cache.index(ref_address)
            if rank == 0:
                return rank
            else:
                _ = self.cache.pop(rank)
                self.cache.insert(0, ref_address)
                return rank

        else:
            self.cache.insert(0, ref_address)
            return -1

# -*- coding: utf-8 -*-

import argparse
parser = argparse.ArgumentParser(description="plot lru graph from log file")
parser.add_argument("--input", "-i", metavar='I', type=str, nargs='?', default='input.txt',
                    help='input file')
parser.add_argument("--output", "-o", metavar='O', type=str, nargs='?', default='output.txt',
                    help='output file')
parser.add_argument("--chunk_group", "-c", metavar='S', type=int, nargs='?', default=10,
                    help='# of chunk group')
parser.add_argument("--title", "-t", metavar='T', type=str, nargs='?', default='',
                    help='title of a graph')
args = parser.parse_args()


import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import json

"""##**memdf3 = tendency toward temporal locality**
* x axis : rank(temporal locality)
* y axis : memory block access count
"""

def simulation(df, block_rank, readcnt, writecnt):
    for index, row in df.iterrows():  ### one by one
        ### type과 rank 맞춰서 readcnt/writecnt 수정
        acc_rank = block_rank.reference(row['blockaddress'])
        if acc_rank == -1:
            continue
        else:
            if (row['type'] == 'readi' or row['type'] == 'readd'):  ###read이면
                try:
                    readcnt[acc_rank] += 1  # readcnt의 acc_rank번째 요소를 1 증가
                except IndexError:  # ***list index out of range
                    for i in range(len(readcnt), acc_rank + 1):
                        readcnt.insert(i, 0)
                    readcnt[acc_rank] += 1

            else:  ###write면
                try:
                    writecnt[acc_rank] += 1  # writecnt의 acc_rank번째 요소를 1 증가
                except IndexError:
                    for i in range(len(writecnt), acc_rank + 1):
                        writecnt.insert(i, 0)
                    writecnt[acc_rank] += 1

    return block_rank, readcnt, writecnt

def save_json(block_rank, readcnt, writecnt, i):
    filename = args.output[:-4] + "_checkpoint" + str(i) + ".json"
    path = filename[:filename.rfind('/')]

    if not os.path.exists(path):  # FileNotFoundError: [Errno2] No such file or directory: '~'
        os.makedirs(path)

    save = {'block_rank': block_rank,
            'readcnt': readcnt,
            'writecnt': writecnt}

    with open(filename, 'w', encoding='utf-8') as f:
        # indent=2 is not needed but makes the file human-readable
        # if the data is nested
        json.dump(save, f, indent=2)

def load_json(i):
    with open(args.output[:-4]+"_checkpoint"+str(i)+".json", 'r') as f:
        load = json.load(f)
  
    block_rank = load['block_rank']
    readcnt = load['readcnt']
    writecnt = load['writecnt']
    #print(load)

    return block_rank, readcnt, writecnt#, dupl_block

## 1. use list of chunk
"""
memdf = pd.read_csv('memdf.csv', sep=',', chunksize=1000000, header=0, index_col=0, error_bad_lines=False)
memdf = list(memdf)
print(memdf[-1].head)
print(memdf[0].head)

for i in range(len(memdf)):
    memdf[i]['time'] = memdf[i].index
    if(i>0):
        block_rank, readcnt, writecnt = load_json(i-1)
        print(block_rank, readcnt, writecnt)
    block_rank, readcnt, writecnt = temp_local(memdf[i], block_rank, readcnt, writecnt)
    save_json(block_rank, readcnt, writecnt, i)
"""

## 2. load separate .csv file
def lru_simulation(startpoint, endpoint):
    ref_block = LRUCache()
    block_rank = list()
    readcnt = list()
    writecnt = list()

    if (startpoint > 0):
        block_rank, readcnt, writecnt = load_json(startpoint - 1)
        ref_block.set(block_rank)
        # print(block_rank, readcnt, writecnt)

    for i in range(startpoint, endpoint):
        memdf = pd.read_csv(args.input + '_' + str(i) + '.csv', sep=',', header=0, index_col=0, on_bad_lines='skip')
        ref_block, readcnt, writecnt = simulation(memdf, ref_block, readcnt, writecnt)
        block_rank = ref_block.get()
        save_json(block_rank, readcnt, writecnt, i)
        print(i)

lru_simulation(0, args.chunk_group)

"""##**memdf3 graph**"""

block_rank, readcnt, writecnt = load_json(args.chunk_group-1)

#--
fig, ax = plt.subplots(2, figsize=(10,10), constrained_layout=True, sharex=True, sharey=True) # sharex=True: share x axis

font_size=25
parameters = {'axes.labelsize': font_size, 'axes.titlesize': font_size, 'xtick.labelsize': font_size, 'ytick.labelsize': font_size}
plt.rcParams.update(parameters)

if args.title != '':
  plt.suptitle(args.title, fontsize=25)

#read
x1 = range(1,len(readcnt)+1)
y1 = readcnt

#write
x2 = range(1,len(writecnt)+1)
y2 = writecnt

# read graph
ax[0].scatter(x1, y1, color='blue', label='read', s=5)
ax[0].set_xscale('log')
ax[0].set_yscale('log')
# legend
ax[0].set_xlabel('rank(temporal locality)')
ax[0].set_ylabel('reference count')
ax[0].legend(loc=(1.0,0.8), ncol=1) #loc = 'best', 'upper right'

# write graph
ax[1].scatter(x2, y2, color='red', label='write', s=5)
ax[1].set_xscale('log')
ax[1].set_yscale('log')
#ax[1].set_ylim([0.5, 1e7])
# legend
ax[1].set_xlabel('rank(temporal locality)')
ax[1].set_ylabel('reference count')
ax[1].legend(loc=(1.0,0.8), ncol=1) #loc = 'best'

#plt.show()
plt.savefig(args.output[:-4]+'.png', dpi=300)
