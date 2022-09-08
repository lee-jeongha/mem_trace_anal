# -*- coding: utf-8 -*-

import argparse
import matplotlib.pyplot as plt
import pandas as pd
from multiprocessing import Process

from load_and_save import save_json, load_json
from simulation import simulation_regardless_of_type


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
def lru_simulation(startpoint, input_filename, output_filename, type='all'):
    ref_block = LRUCache()
    block_rank = list()
    ref_cnt = list()
    
    if (startpoint > 0):
        filename = output_filename + "-" + type + "_checkpoint" + str(startpoint - 1) + ".json"
        saving_list = ['block_rank', 'ref_cnt']

        block_rank, ref_cnt = load_json(saving_list, filename)
        ref_block.set(block_rank)
        # print(block_rank, ref_cnt)

    i = startpoint
    while True:
        try:
            memdf = pd.read_csv(input_filename + '_' + str(i) + '.csv', sep=',', header=0, index_col=0, on_bad_lines='skip')
        except FileNotFoundError:
            print("no file named:", input_filename + '_' + str(i) + '.csv')
            break

        if type == 'readi':
            memdf = memdf[memdf['type'] == 'readi']
        elif type == 'readd':
            memdf = memdf[memdf['type'] == 'readd']
        elif type == 'read':
            memdf = memdf[memdf['type'] != 'write']    
        elif type == 'write':
            memdf = memdf[memdf['type'] == 'write']
        else:
            print("choose type 'readi', 'readd', 'read' or 'write'")
            return

        ref_block, ref_cnt = simulation_regardless_of_type(memdf, ref_block, ref_cnt)
        block_rank = ref_block.get()

        savings = {'block_rank': block_rank, 'ref_cnt': ref_cnt}
        filename = output_filename + "-" + type + "_checkpoint" + str(i) + ".json"
        save_json(savings, filename)
        i += 1

#-----
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="plot lru graph from log file")
    parser.add_argument("--input", "-i", metavar='I', type=str, nargs='?', default='input.txt',
                        help='input file')
    parser.add_argument("--output", "-o", metavar='O', type=str, nargs='?', default='output.txt',
                        help='output file')
    parser.add_argument("--start_chunk", "-s", metavar='S', type=int, nargs='?', default=0,
                        help='start chunk index')
    args = parser.parse_args()

    p1 = Process(target=lru_simulation, args=(args.start_chunk, args.input, args.output, 'readi'))
    p2 = Process(target=lru_simulation, args=(args.start_chunk, args.input, args.output, 'readd'))
    p3 = Process(target=lru_simulation, args=(args.start_chunk, args.input, args.output, 'write'))
    #p4 = Process(target=lru_simulation, args=(args.start_chunk, args.input, args.output, 'read'))
 
    p1.start()
    p2.start()
    p3.start()
    #p4.start()

    p1.join()
    p2.join()
    p3.join()
    #p4.join()
