# -*- coding: utf-8 -*-

import argparse
import matplotlib.pyplot as plt
import pandas as pd
from multiprocessing import Process

from load_and_save import save_json, load_json
from simulation import overall_rank_simulation, separately_rank_simulation


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
def lfu_simulation(startpoint, endpoint, input_filename, output_filename):
    ref_block = LFUCache()
    block_rank = dict()
    read_cnt = list()
    write_cnt = list()

    if (startpoint > 0):
        filename = output_filename + "_checkpoint" + str(startpoint - 1) + ".json"
        saving_list = ['block_rank', 'read_cnt', 'write_cnt']

        block_rank, read_cnt, write_cnt = load_json(saving_list, filename)
        block_rank = {int(k): v for k, v in block_rank.items()}
        ref_block.set(block_rank)
        # print(block_rank, read_cnt, write_cnt)

    for i in range(startpoint, endpoint):
        try:
            memdf = pd.read_csv(input_filename + '_' + str(i) + '.csv', sep=',', header=0, index_col=0, on_bad_lines='skip')
        except FileNotFoundError:
            print("no file named:", input_filename + '_' + str(i) + '.csv')
            break
        
        ref_block, read_cnt, write_cnt = overall_rank_simulation(memdf, ref_block, read_cnt, write_cnt)
        block_rank = ref_block.get()

        savings = {'block_rank': block_rank,
                'read_cnt': read_cnt,
                'write_cnt': write_cnt}
        filename = output_filename + "_checkpoint" + str(i) + ".json"
        save_json(savings, filename)

def lfu_simulation_by_type(startpoint, endpoint, input_filename, output_filename):
    read_ref_block = LFUCache()
    read_block_rank = dict()
    read_cnt = list()
    
    write_ref_block = LFUCache()
    write_block_rank = dict()
    write_cnt = list()

    if (startpoint > 0):
        filename = output_filename + "-by-type_checkpoint" + str(startpoint - 1) + ".json"
        saving_list = ['read_block_rank', 'read_cnt', 'write_block_rank', 'write_cnt']
        read_block_rank, read_cnt, write_block_rank, write_cnt = load_json(saving_list, filename)

        read_block_rank = {int(k): v for k, v in read_block_rank.items()}
        read_ref_block.set(read_block_rank)
        write_block_rank = {int(k): v for k, v in write_block_rank.items()}
        write_ref_block.set(write_block_rank)
        # print(block_rank, read_cnt, write_cnt)

    for i in range(startpoint, endpoint):
        try:
            memdf = pd.read_csv(input_filename + '_' + str(i) + '.csv', sep=',', header=0, index_col=0, on_bad_lines='skip')
        except FileNotFoundError:
            print("no file named:", input_filename + '_' + str(i) + '.csv')
            break

        read_ref_block, read_cnt, write_ref_block, write_cnt = separately_rank_simulation(memdf, read_ref_block, read_cnt, write_ref_block, write_cnt)

        read_block_rank = read_ref_block.get()
        write_block_rank = write_ref_block.get()
        savings = {'read_block_rank': read_block_rank, 'read_cnt': read_cnt, 'write_block_rank': write_block_rank, 'write_cnt': write_cnt}
        
        filename = output_filename + "-by-type_checkpoint" + str(i) + ".json"
        save_json(savings, filename)

#-----
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="plot lfu graph from log file")
    parser.add_argument("--input", "-i", metavar='I', type=str, nargs='?', default='input.txt',
                        help='input file')
    parser.add_argument("--output", "-o", metavar='O', type=str, nargs='?', default='output.txt',
                        help='output file')
    parser.add_argument("--start_chunk", "-s", metavar='S', type=int, nargs='?', default=0,
                        help='start chunk index')
    parser.add_argument("--end_chunk", "-e", metavar='E', type=int, nargs='?', default=100,
                        help='end chunk index')
    parser.add_argument("--title", "-t", metavar='T', type=str, nargs='?', default='',
                        help='title of a graph')
    args = parser.parse_args()

    p1 = Process(target=lfu_simulation, args=(args.start_chunk, args.end_chunk + 1, args.input, args.output))
    p2 = Process(target=lfu_simulation_by_type, args=(args.start_chunk, args.end_chunk + 1, args.input, args.output))
 
    p1.start()
    p2.start()

    p1.join()
    p2.join()
