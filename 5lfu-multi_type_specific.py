# -*- coding: utf-8 -*-

import argparse
import matplotlib.pyplot as plt
import pandas as pd
from multiprocessing import Process

from load_and_save import save_json, load_json
from plot_graph import plot_frame
from simulation import simulation_regardless_of_type


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
        ref_address_idx = self.ref_block.index(ref_address)
        _ = self.ref_block.pop(ref_address_idx)

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
            freq_node = self.cache[ref_address]
            rank = self.get_freqs_rank(freq_node)
            #rank += freq_node.ref_block.index(ref_address)

            new_freq_node = self.move_next_to(ref_address, freq_node)
            self.cache[ref_address] = new_freq_node

            return rank
        
        else:
            new_freq_node = self.create_freq_node(ref_address)
            self.cache[ref_address] = new_freq_node
            
            return -1

    def move_next_to(self, ref_address, freq_node):  # for each access
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


"""##**memdf5 = tendency toward temporal frequency**
* x axis : rank(temporal frequency)
* y axis : access count per block
"""

## load separate .csv file
def lfu_simulation(startpoint, endpoint, input_filename, output_filename, type='all'):
    ref_block = LFUCache()
    block_rank = dict()
    ref_cnt = list()

    if (startpoint > 0):
        filename = output_filename + "-" + type + "_checkpoint" + str(startpoint - 1) + ".json"
        saving_list = ['block_rank', 'ref_cnt']

        block_rank, ref_cnt = load_json(saving_list, filename)
        block_rank = {int(k): v for k, v in block_rank.items()}
        ref_block.set(block_rank)
        # print(block_rank, ref_cnt)

    for i in range(startpoint, endpoint):
        memdf = pd.read_csv(input_filename + '_' + str(i) + '.csv', sep=',', header=0, index_col=0, on_bad_lines='skip')
        if type == 'read':
            memdf = memdf[memdf['type'] != 'write']
        elif type == 'write':
            memdf = memdf[memdf['type'] == 'write']
        else:
            print("choose type 'read' or 'write'")
            return

        ref_block, ref_cnt = simulation_regardless_of_type(memdf, ref_block, ref_cnt)
        block_rank = ref_block.get()

        savings = {'block_rank': block_rank, 'ref_cnt': ref_cnt}
        filename = output_filename + "-" + type + "_checkpoint" + str(i) + ".json"
        save_json(savings, filename)

"""##**memdf5 graph**"""
def lfu_graph(read_cnt, write_cnt, title, filename):
    fig, ax = plot_frame(2, 1, title=title, xlabel='rank(temporal frequency)', ylabel='reference count', log_scale=True)

    #read
    x1 = range(1,len(read_cnt)+1)
    y1 = read_cnt

    #write
    x2 = range(1,len(write_cnt)+1)
    y2 = write_cnt

    # read graph
    ax[0].scatter(x1, y1, color='blue', label='read', s=3)
    ax[0].legend(loc='lower left', ncol=1, fontsize=20, markerscale=3)

    # write graph
    ax[1].scatter(x2, y2, color='red', label='write', s=3)
    ax[1].legend(loc='lower left', ncol=1, fontsize=20, markerscale=3)

    #plt.show()
    plt.savefig(filename+'.png', dpi=300)

#-----
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="plot lfu graph from log file")
    parser.add_argument("--input", "-i", metavar='I', type=str, nargs='?', default='input.txt',
                        help='input file')
    parser.add_argument("--output", "-o", metavar='O', type=str, nargs='?', default='output.txt',
                        help='output file')
    parser.add_argument("--start_chunk", "-s", metavar='S', type=int, nargs='?', default=0,
                        help='# of start chunk')
    parser.add_argument("--end_chunk", "-e", metavar='E', type=int, nargs='?', default=100,
                        help='# of end chunk')
    parser.add_argument("--title", "-t", metavar='T', type=str, nargs='?', default='',
                        help='title of a graph')
    args = parser.parse_args()

    p1 = Process(target=lfu_simulation, args=(args.start_chunk, args.end_chunk, args.input, args.output, 'read'))
    p2 = Process(target=lfu_simulation, args=(args.start_chunk, args.end_chunk, args.input, args.output, 'write'))
 
    p1.start()
    p2.start()

    p1.join()
    p2.join()

    saving_list = ['block_rank', 'ref_cnt']
    filename = args.output + "-read_checkpoint" + str(args.end_chunk-1) + ".json"
    _, read_cnt = load_json(saving_list, filename)
    filename = args.output + "-write_checkpoint" + str(args.end_chunk-1) + ".json"
    _, write_cnt = load_json(saving_list, filename)
    lfu_graph(read_cnt, write_cnt, title=args.title, filename=args.output)