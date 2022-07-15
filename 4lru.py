# -*- coding: utf-8 -*-

import argparse
import matplotlib.pyplot as plt
import pandas as pd
from load_and_save import save_json, load_json
from plot_graph import plot_frame


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

def simulation(df, block_rank, readcnt, writecnt):
    for index, row in df.iterrows():  ### one by one
        ### Increase readcnt/writecnt by matching 'type' and block_rank
        acc_rank = block_rank.reference(row['blockaddress'])
        if acc_rank == -1:
            continue
        else:
            if (row['type'] == 'readi' or row['type'] == 'readd'):  ### if the 'type' is 'read'
                try:
                    readcnt[acc_rank] += 1  # Increase [acc_rank]th element of readcnt by 1
                except IndexError:  # ***list index out of range
                    for i in range(len(readcnt), acc_rank + 1):
                        readcnt.insert(i, 0)
                    readcnt[acc_rank] += 1

            else:   ### if the 'type' is 'write'
                try:
                    writecnt[acc_rank] += 1 # Increase [acc_rank]th element of writecnt by 1
                except IndexError:
                    for i in range(len(writecnt), acc_rank + 1):
                        writecnt.insert(i, 0)
                    writecnt[acc_rank] += 1

    return block_rank, readcnt, writecnt

## load separate .csv file
def lru_simulation(startpoint, endpoint, input_filename, output_filename):
    ref_block = LRUCache()
    block_rank = list()
    readcnt = list()
    writecnt = list()

    if (startpoint > 0):
        filename = output_filename + "_checkpoint" + str(startpoint - 1) + ".json"
        saving_list = ['block_rank', 'readcnt', 'writecnt']

        block_rank, readcnt, writecnt = load_json(saving_list, filename)
        ref_block.set(block_rank)
        # print(block_rank, readcnt, writecnt)

    for i in range(startpoint, endpoint):
        memdf = pd.read_csv(input_filename + '_' + str(i) + '.csv', sep=',', header=0, index_col=0, on_bad_lines='skip')
        ref_block, readcnt, writecnt = simulation(memdf, ref_block, readcnt, writecnt)
        block_rank = ref_block.get()

        savings = {'block_rank': block_rank,
                'readcnt': readcnt,
                'writecnt': writecnt}
        filename = output_filename + "_checkpoint" + str(i) + ".json"
        save_json(savings, filename)

"""##**memdf4 graph**"""
def lru_graph(readcnt, writecnt, title, filname):
    fig, ax = plot_frame(2, 1, title=title, xlabel='rank(temporal locality)', ylabel='reference count', log_scale=True)

    #read
    x1 = range(1,len(readcnt)+1)
    y1 = readcnt

    #write
    x2 = range(1,len(writecnt)+1)
    y2 = writecnt

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
    parser.add_argument("--chunk_group", "-c", metavar='S', type=int, nargs='?', default=100,
                        help='# of chunk group')
    parser.add_argument("--title", "-t", metavar='T', type=str, nargs='?', default='',
                        help='title of a graph')
    args = parser.parse_args()

    lru_simulation(0, args.chunk_group, input_filename=args.input, output_filename=args.output)
    
    filename = args.output + "_checkpoint" + str(args.chunk_group-1) + ".json"
    saving_list = ['block_rank', 'readcnt', 'writecnt']
    _, readcnt, writecnt = load_json(saving_list, filename)
    lru_graph(readcnt, writecnt, title=args.title, filname=args.output)
