# -*- coding: utf-8 -*-

import argparse
import matplotlib.pyplot as plt
import pandas as pd
from multiprocessing import Process

from load_and_save import save_json, load_json
from plot_graph import plot_frame
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
def lru_simulation(startpoint, endpoint, input_filename, output_filename, type='all'):
    ref_block = LRUCache()
    block_rank = list()
    ref_cnt = list()
    
    if (startpoint > 0):
        filename = output_filename + "-" + type + "_checkpoint" + str(startpoint - 1) + ".json"
        saving_list = ['block_rank', 'ref_cnt']

        block_rank, ref_cnt = load_json(saving_list, filename)
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

"""##**memdf4 graph**"""
def lru_graph(read_cnt, write_cnt, title, filname):
    fig, ax = plot_frame(2, 1, title=title, xlabel='rank(temporal locality)', ylabel='reference count', log_scale=True)

    #read
    x1 = range(1,len(read_cnt)+1)
    y1 = read_cnt

    #write
    x2 = range(1,len(write_cnt)+1)
    y2 = write_cnt

    # read graph
    ax[0].scatter(x1, y1, color='blue', label='read', s=5)
    ax[0].legend(loc='lower left', ncol=1, fontsize=20, markerscale=3)

    # write graph
    ax[1].scatter(x2, y2, color='red', label='write', s=5)
    ax[1].legend(loc='lower left', ncol=1, fontsize=20, markerscale=3)

    #plt.show()
    plt.savefig(filname+'.png', dpi=300)

#-----
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="plot lru graph from log file")
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

    p1 = Process(target=lru_simulation, args=(args.start_chunk, args.end_chunk, args.input, args.output, 'read'))
    p2 = Process(target=lru_simulation, args=(args.start_chunk, args.end_chunk, args.input, args.output, 'write'))
 
    p1.start()
    p2.start()

    p1.join()
    p2.join()

    saving_list = ['block_rank', 'ref_cnt']
    filename = args.output + "-read_checkpoint" + str(args.end_chunk-1) + ".json"
    _, read_cnt = load_json(saving_list, filename)
    filename = args.output + "-write_checkpoint" + str(args.end_chunk-1) + ".json"
    _, write_cnt = load_json(saving_list, filename)
    lru_graph(read_cnt, write_cnt, title=args.title, filname=args.output)
