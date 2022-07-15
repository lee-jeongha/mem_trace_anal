# -*- coding: utf-8 -*-

import argparse
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from load_and_save import save_csv
from plot_graph import plot_frame
import math


"""##**memdf1 = access count**
* x axis : (virtual) memory block address
* y axis : memory block access count
"""
def ref_cnt(inputdf, concat=False):
    if (concat) :
        df = inputdf.groupby(by=['blockaddress', 'type'], as_index=False).sum()
        #print(df)
    else :
        inputdf = inputdf.replace('readi', 'read')
        inputdf = inputdf.replace('readd', 'read')

        df = inputdf.groupby(['blockaddress', 'type'])['blockaddress'].count().reset_index(name='count') # Count rows based on 'blockaddress' & 'type', And name as 'count'

    return df

def ref_cnt_per_block(input_filename, chunks=100):
    ## 1. use list of chunk
    """
    memdf = pd.read_csv(input_filename+'.csv', sep=',', chunksize=1000000, header=0, index_col=0, error_bad_lines=False)
    memdf = list(memdf)
    #---
    df1 = pd.DataFrame()
    for i in range(len(memdf)):
        memdf = pd.read_csv(memdf[i], sep=',', header=0, index_col=0, error_bad_lines=False)
        df = address_ref(memdf, concat=False)
        df1 = pd.concat([df1, df])
    """

    ## 2. load separate .csv file
    memdf1 = pd.DataFrame()
    for i in range(chunks): 
        filename = input_filename+'_'+str(i)+'.csv'
        try:
            df = pd.read_csv(filename, sep=',', header=0, index_col=0, on_bad_lines='skip')
            memdf1_chunk = ref_cnt(df, concat=False)
            memdf1 = pd.concat([memdf1, memdf1_chunk])
        except FileNotFoundError:
            print("No file named: ", filename)
            break

    memdf1 = ref_cnt(memdf1, concat=True)

    # both read and write
    memdf1_rw = memdf1.groupby(by=['blockaddress'], as_index=False).sum()
    memdf1_rw['type'] = 'read&write'

    memdf1 = pd.concat([memdf1, memdf1_rw], sort=True)

    return memdf1

"""**memdf1 graph**
> Specify the axis range (manual margin adjustment required)
"""
def digit_length(n):
    return int(math.log10(n)) + 1 if n else 0

def hist_label(subplot, counts, bars, round_range=0):
    if round_range:
        counts = np.round(counts, round_range)
    else:
        counts = [int(i) for i in counts]
    for idx,rect in enumerate(bars):
        height = rect.get_height()
        subplot.text(rect.get_x() + rect.get_width()/3.25, 0.4*height,
                counts[idx], fontsize=15,
                ha='center', va='bottom', rotation=90)

"""memdf1.1 graph"""
def ref_cnt_graph(df, title, filename):
    x1 = df['blockaddress'][(df['type']=='read')]
    x2 = df['blockaddress'][(df['type']=='write')]
    y1 = df['count'][(df['type']=='read')]
    y2 = df['count'][(df['type']=='write')]

    fig, ax = plot_frame(2, 1, title=title, xlabel='(virtual) memory block address', ylabel='memory block reference count')

    print(x1.max(), x2.max())
    print(y1.min(), y1.max(), digit_length(y1.max()))
    print(y2.min(), y2.max(), digit_length(y2.max()))

    # read graph
    ax[0].scatter(x1, y1, color='blue', label='read', s=3)
    ax[0].legend(loc='upper right', ncol=1, fontsize=20, markerscale=3) #loc = (1.0,0.8)

    # write graph
    ax[1].scatter(x2, y2, color='red', label='write', s=3)
    ax[1].legend(loc='upper right', ncol=1, fontsize=20, markerscale=3) #loc = (1.0,0.8)

    #plt.show()
    plt.savefig(filename+'.png', dpi=300)

"""memdf1.2 graph"""
def ref_cnt_distribute_graph(df, title, filename):
    y1 = df['count'][(df['type']=='read')]
    y2 = df['count'][(df['type']=='write')]

    fig, ax = plot_frame(2, 2, title=title, xlabel='reference count', ylabel='# of memory block', share_yaxis='col')
    plt.xscale('log')

    bin_list = [1]
    if(y1.max() > y2.max()):
        bin_list.extend([ 10**i + 1 for i in range(digit_length(y1.max()) + 1) ])
    else:
        bin_list.extend([ 10**i + 1 for i in range(digit_length(y2.max()) + 1) ])

    # read graph
    counts, edges, bars = ax[0][0].hist(y1, bins=bin_list, density=False, rwidth=3, color='blue', edgecolor='black', label='read')
    ax[0][0].legend(loc='upper right', ncol=1, fontsize=20)
    hist_label(ax[0][0], counts, bars)

    # write graph
    counts, edges, bars = ax[1][0].hist(y2, bins=bin_list, density=False, rwidth=3, color='red', edgecolor='black', label='write')
    ax[1][0].legend(loc='upper right', ncol=1, fontsize=20)
    hist_label(ax[1][0], counts, bars)

    """normalized graph"""
    # read graph
    counts, edges, bars = ax[0][1].hist(y1, bins=bin_list, density=True, rwidth=3, color='blue', edgecolor='black', label='read')
    ax[0][1].legend(loc='upper right', ncol=1, fontsize=20)
    hist_label(ax[0][1], counts, bars, 5)

    # write graph
    counts, edges, bars = ax[1][1].hist(y2, bins=bin_list, density=True, rwidth=3, color='red', edgecolor='black', label='write')
    ax[1][1].legend(loc='upper right', ncol=1, fontsize=20)
    hist_label(ax[1][1], counts, bars, 5)

    #plt.show()
    plt.savefig(filename+'_hist.png', dpi=300)

#-----
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="plot reference count per each block")
    parser.add_argument("--input", "-i", metavar='I', type=str, nargs='?', default='input.txt',
                        help='input file')
    parser.add_argument("--output", "-o", metavar='O', type=str, nargs='?', default='output.txt',
                        help='output file')
    parser.add_argument("--chunk_group", "-c", metavar='S', type=int, nargs='?', default=100,
                        help='# of chunk group')
    parser.add_argument("--distribution", "-d", action='store_true',
                        help='plot histogram bound by reference count')
    parser.add_argument("--title", "-t", metavar='T', type=str, nargs='?', default='',
                        help='title of a graph')
    args = parser.parse_args()

    memdf1 = ref_cnt_per_block(input_filename=args.input, chunks=args.chunk_group)
    save_csv(memdf1, args.output+'.csv', 0)

    #memdf1 = pd.read_csv(args.output+'.csv', sep=',', header=0, index_col=0, on_bad_lines='skip')
    ref_cnt_graph(memdf1, title=args.title, filename=args.output)

    if (args.distribution):
        plt.clf() # Clear the current figure
        ref_cnt_distribute_graph(memdf1, title=args.title, filename=args.output)
