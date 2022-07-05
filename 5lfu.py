class FreqNode(object):
    def __init__(self, freq, ref_block, pre, nxt):
        self.freq = freq
        self.ref_block = ref_block
        self.pre = pre  # previous FreqNode
        self.nxt = nxt  # next FreqNode

    def count_blocks(self):
        return len(self.ref_block)

    def remove(self):
        if self.pre is not None:
            self.pre.nxt = self.nxt
        if self.nxt is not None:
            self.nxt.pre = self.pre

        pre = self.pre
        nxt = self.nxt
        self.pre = self.nxt = None

        return (pre, nxt)

    def remove_block(self, ref_address): # remove ref_address from ref_block within freq_node
        ref_block_list = self.ref_block
        
        ref_address_idx = ref_block_list.index(ref_address)
        _ = ref_block_list.pop(ref_address_idx)

        self.ref_block = ref_block_list

        return ref_address_idx

    def insert_ref_block(self, ref_address):
        self.ref_block.insert(0, ref_address)

    def append_ref_block(self, ref_address):
        self.ref_block.append(ref_address)

    def insert_after_me(self, freq_node):
        freq_node.pre = self
        freq_node.nxt = self.nxt

        if self.nxt is not None:
            self.nxt.pre = freq_node
        else:
            self.nxt = None

        self.nxt = freq_node

    def insert_before_me(self, freq_node):
        if self.pre is not None:
            self.pre.nxt = freq_node

        freq_node.pre = self.pre
        freq_node.nxt = self
        self.pre = freq_node


class LFUCache(object):

    def __init__(self):
        self.cache = {}  # {addr: freq_node}
        self.freq_link_head = None

    def get(self):
        ref_table = {}  # {freq: [ref_block]}
        current = self.freq_link_head

        while current != None:
            freq = current.freq
            ref_block = current.ref_block
            ref_table[freq] = ref_block
            current = current.nxt

        return ref_table

    def set(self, ref_table):
        freqs = list(ref_table.keys())
        freqs.sort()

        prev_freq_node = None
        for freq in freqs:
            ref_block = ref_table[freq]
            target_freq_node = FreqNode(freq, ref_block, None, None)

            if prev_freq_node == None:
                self.freq_link_head = target_freq_node
            else:
                target_freq_node.pre = prev_freq_node
                prev_freq_node.nxt = target_freq_node

            for ref_addr in ref_block:
                self.cache[ref_addr] = target_freq_node

            prev_freq_node = target_freq_node

    def reference(self, ref_address):
        if ref_address in self.cache:
            freq = self.cache[ref_address]
            new_freq = self.move_next_to(ref_address, freq)
            rank = self.get_freqs_rank(new_freq)

            self.cache[ref_address] = new_freq

            return rank
        
        else:
            freq = self.create_freq_node(ref_address)
            self.cache[ref_address] = freq
            
            return -1

    def move_next_to(self, ref_address, freq_node): # for each access
        if freq_node.nxt is None or freq_node.nxt.freq != freq_node.freq + 1:
            target_freq_node = FreqNode(freq_node.freq + 1, list(), None, None)
            target_empty = True
        
        else:
            target_freq_node = freq_node.nxt
            target_empty = False

        target_freq_node.insert_ref_block(ref_address)

        if target_empty:
            freq_node.insert_after_me(target_freq_node)

        _ = freq_node.remove_block(ref_address)

        if freq_node.count_blocks() == 0: # if there is nothing left in freq_node
            if self.freq_link_head == freq_node:
                self.freq_link_head = target_freq_node

            freq_node.remove()
        
        return target_freq_node

    def create_freq_node(self, ref_address):
        ref_block = [ref_address]

        if self.freq_link_head is None or self.freq_link_head.freq != 1:
            new_freq_node = FreqNode(1, ref_block, None, None)
            self.cache[ref_address] = new_freq_node

            if self.freq_link_head is not None: # LFU has freq_link_head but frequency is not 1
                self.freq_link_head.insert_before_me(new_freq_node)

            self.freq_link_head = new_freq_node
            
            return new_freq_node

        else: # if LFU has freq_link_head which frequency value is 1
            self.freq_link_head.append_ref_block(ref_address)
        
            return self.freq_link_head
    
    def get_freqs_rank(self, freq_node):
        current = freq_node.nxt
        rank = 1

        while current != None:
            rank += current.count_blocks()
            current = current.nxt

        return rank


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
                    writecnt[acc_rank] += 1 # writecnt의 acc_rank번째 요소를 1 증가
                except IndexError:
                    for i in range(len(writecnt), acc_rank + 1):
                        writecnt.insert(i, 0)
                    writecnt[acc_rank] += 1

    return block_rank, readcnt, writecnt

def save_json(block_rank, readcnt, writecnt, i):
    filename = args.output[:-4] + "_checkpoint" + str(i) + ".json"
    path = filename[:filename.rfind('/')]

    if not os.path.exists(path):    # FileNotFoundError: [Errno2] No such file or directory: '~'
        os.makedirs(path)

    save = {'block_rank': block_rank,
            'readcnt': readcnt,
            'writecnt': writecnt}

    with open(filename, 'w', encoding='utf-8') as f:
        # indent=2 is not needed but makes the file human-readable
        # if the data is nested
        json.dump(save, f, indent=2)

def load_json(i):
    filename = args.output[:-4] + "_checkpoint" + str(i) + ".json"

    with open(filename, 'r') as f:
        load = json.load(f)

    block_rank = load['block_rank']
    readcnt = load['readcnt']
    writecnt = load['writecnt']

    return block_rank, readcnt, writecnt

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
def lfu_simulation(startpoint, endpoint):  # , Subsequent=False):
    ref_block = LFUCache()
    block_rank = dict()
    readcnt = list()
    writecnt = list()

    if (startpoint > 0):
        block_rank, readcnt, writecnt = load_json(startpoint - 1)
        block_rank = {int(k): v for k, v in block_rank.items()}
        ref_block.set(block_rank)
        # print(block_rank, readcnt, writecnt)

    for i in range(startpoint, endpoint):
        memdf = pd.read_csv(args.input + '_' + str(i) + '.csv', sep=',', header=0, index_col=0, on_bad_lines='skip')
        ref_block, readcnt, writecnt = simulation(memdf, ref_block, readcnt, writecnt)
        block_rank = ref_block.get()
        save_json(block_rank, readcnt, writecnt, i)

lfu_simulation(0, args.chunk_group)  # , Subsequent=False)

"""##**memdf5 graph**"""

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
ax[0].set_xlabel('rank(temporal frequency)')
ax[0].set_ylabel('reference count')
ax[0].legend(loc=(1.0,0.8), ncol=1) #loc = 'best', 'upper right'

# write graph
ax[1].scatter(x2, y2, color='red', label='write', s=5)
ax[1].set_xscale('log')
ax[1].set_yscale('log')
#ax[1].set_ylim([0.5, 1e7])
# legend
ax[1].set_xlabel('rank(temporal frequency)')
ax[1].set_ylabel('reference count')
ax[1].legend(loc=(1.0,0.8), ncol=1) #loc = 'best'

#plt.show()
plt.savefig(args.output[:-4]+'.png', dpi=300)