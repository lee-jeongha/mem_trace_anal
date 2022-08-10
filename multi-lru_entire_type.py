# -*- coding: utf-8 -*-

import argparse
import matplotlib.pyplot as plt
import pandas as pd
from multiprocessing import Process
from load_and_save import save_json, load_json
from simulation import overall_rank_simulation, separately_rank_simulation


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


"""##**memdf4 = tendency toward temporal locality**
* x axis : rank(temporal locality)
* y axis : access count per block
"""

## load separate .csv file
def lru_simulation(startpoint, endpoint, input_filename, output_filename):
    ref_block = LRUCache()
    block_rank = list()
    read_cnt = list()
    write_cnt = list()

    if (startpoint > 0):
        filename = output_filename + "_checkpoint" + str(startpoint - 1) + ".json"
        saving_list = ['block_rank', 'read_cnt', 'write_cnt']

        block_rank, read_cnt, write_cnt = load_json(saving_list, filename)
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

def lru_simulation_by_type(startpoint, endpoint, input_filename, output_filename):
    read_ref_block = LRUCache()
    read_block_rank = list()
    read_cnt = list()
    
    write_ref_block = LRUCache()
    write_block_rank = list()
    write_cnt = list()

    if (startpoint > 0):
        filename = output_filename + "-by-type_checkpoint" + str(startpoint - 1) + ".json"
        saving_list = ['read_block_rank', 'read_cnt', 'write_block_rank', 'write_cnt']
        read_block_rank, read_cnt, write_block_rank, write_cnt = load_json(saving_list, filename)

        read_ref_block.set(read_block_rank)
        write_ref_block.set(write_block_rank)
        # print(block_rank, read_cnt, write_cnt)

    for i in range(startpoint, endpoint):
        memdf = pd.read_csv(input_filename + '_' + str(i) + '.csv', sep=',', header=0, index_col=0, on_bad_lines='skip')

        read_ref_block, read_cnt, write_ref_block, write_cnt = separately_rank_simulation(memdf, read_ref_block, read_cnt, write_ref_block, write_cnt)

        read_block_rank = read_ref_block.get()
        write_block_rank = write_ref_block.get()
        savings = {'read_block_rank': read_block_rank, 'read_cnt': read_cnt, 'write_block_rank': write_block_rank, 'write_cnt': write_cnt}
        
        filename = output_filename + "-by-type_checkpoint" + str(i) + ".json"
        save_json(savings, filename)

#-----
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="plot lru graph from log file")
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

    p1 = Process(target=lru_simulation, args=(args.start_chunk, args.end_chunk + 1, args.input, args.output))
    p2 = Process(target=lru_simulation_by_type, args=(args.start_chunk, args.end_chunk + 1, args.input, args.output))
 
    p1.start()
    p2.start()

    p1.join()
    p2.join()

