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


lfu = LFUCache()
lfu1 = LFUCache()

address = [2,3,1,2,3,2,2,2,2,3,2,7,7,3,7,7,1]
for i in address:
    rank = lfu.reference(i)

cache = lfu.get()
lfu1.set(cache)

rank1 = lfu.reference(4)
rank2 = lfu.reference(5)
cache = lfu.get()
print(cache, rank1, rank2)

rank3 = lfu1.reference(3)
rank4 = lfu1.reference(8)
cache1 = lfu1.get()
print(cache1, rank3, rank4)