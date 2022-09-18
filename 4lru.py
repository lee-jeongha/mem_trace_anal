# -*- coding: utf-8 -*-

import argparse
import matplotlib.pyplot as plt
import pandas as pd
from load_and_save import save_json, load_json
from plot_graph import plot_frame
from simulation import simulation


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

        ref_block, read_cnt, write_cnt = simulation(memdf, ref_block, read_cnt, write_cnt)
        block_rank = ref_block.get()

        savings = {'block_rank': block_rank,
                'read_cnt': read_cnt,
                'write_cnt': write_cnt}
        filename = output_filename + "_checkpoint" + str(i) + ".json"
        save_json(savings, filename)

"""##**memdf4 graph**"""
def lru_graph(read_cnt, write_cnt, title, filename, xlim : list = None, ylim : list = None):
    fig, ax = plot_frame((2, 1), title=title, xlabel='page ranking', ylabel='# of references', log_scale=True)
    
    if xlim:
        plt.setp(ax, xlim=xlim)
    if ylim:
        plt.setp(ax, ylim=ylim)

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
    plt.savefig(filename+'.png', dpi=300)

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

    lru_simulation(args.start_chunk, args.end_chunk + 1, input_filename=args.input, output_filename=args.output)
    
    filename = args.output + "_checkpoint" + str(args.end_chunk) + ".json"
    saving_list = ['block_rank', 'read_cnt', 'write_cnt']
    _, read_cnt, write_cnt = load_json(saving_list, filename)
    lru_graph(read_cnt, write_cnt, title=args.title, filename=args.output)
