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
    if (concat):
        df = inputdf.groupby(by=['blockaddress', 'type'], as_index=False).sum()
        #print(df)
        return df

    else:
        #inputdf = inputdf.replace('readi', 'read')
        #inputdf = inputdf.replace('readd', 'read')

        df = inputdf.groupby(['blockaddress', 'type'])['blockaddress'].count().reset_index(name='count') # Count rows based on 'blockaddress' & 'type', And name as 'count'

        return df

def ref_cnt_per_block(input_filename):
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
    memdf = pd.DataFrame()

    i = 0
    while True: 
        filename = input_filename+'_'+str(i)+'.csv'

        try:
            df = pd.read_csv(filename, sep=',', header=0, index_col=0, on_bad_lines='skip')
            memdf_chunk = ref_cnt(df, concat=False)
            memdf = pd.concat([memdf, memdf_chunk])
        except FileNotFoundError:
            print("No file named: ", filename)
            break
        i += 1

    memdf = ref_cnt(memdf, concat=True)

    # create 'read' column readi and readd
    memdf_read = memdf[(memdf.type == 'readi') | (memdf.type == 'readd')]
    memdf_read = memdf_read.groupby(by=['blockaddress'], as_index=False).sum()
    memdf_read['type'] = 'read'

    # both read and write
    memdf_rw = memdf.groupby(by=['blockaddress'], as_index=False).sum()
    memdf_rw['type'] = 'read&write'

    memdf = pd.concat([memdf, memdf_read], sort=True)
    memdf = pd.concat([memdf, memdf_rw], sort=True)

    #instruction count
    type_cnt = memdf.groupby(by=['type'], as_index=False).sum()
    memdf['readi'] = pd.Series(type_cnt['count'].values[type_cnt['type']=='readi'])
    memdf['readd'] = pd.Series(type_cnt['count'].values[type_cnt['type']=='readd'])
    memdf['write'] = pd.Series(type_cnt['count'].values[type_cnt['type']=='write'])

    return memdf

"""**memdf1 graph**"""
def digit_length(n):
    return int(math.log10(n)) + 1 if n else 0

def hist_label(subplot, counts, bars, round_range=0, rotation=90):
    if round_range:
        counts = np.round(counts, round_range)
    else:
        counts = [int(i) for i in counts]
    for idx,rect in enumerate(bars):
        height = rect.get_height()
        subplot.text(rect.get_x() + rect.get_width()/2, 0.4*height,
                counts[idx], fontsize=15,
                ha='center', va='bottom', rotation=rotation)

"""memdf1.0 graph"""
def instruction_cnt_graph(title, filename, readi_cnt, readd_cnt, write_cnt):
    x = range(3)
    labels = ['readi', 'readd', 'write']
    values = [readi_cnt, readd_cnt, write_cnt]
    colors = ['c', 'dodgerblue', 'red']
    handles = [plt.Rectangle((0,0),1,1, color=colors[i]) for i in range(3)]

    cnt_sum = readi_cnt + readd_cnt + write_cnt
    percentile_values = np.divide(values, cnt_sum/100).round(3)

    fig, ax = plot_frame((1, 1), title=title, xlabel='instruction type', ylabel='instruction count', share_yaxis='col')
    
    rects = plt.bar(x, values, color=colors)
    plt.xticks(x, labels)
    plt.yticks([])
    #plt.bar_label(rects, fontsize=20, fmt='%,.0f')
    plt.bar_label(rects, [f'{i:}%' for i in percentile_values], fontsize=20)
    plt.legend(handles, [f'{i:,.0f}' for i in values], loc='upper left', fontsize=15)
    #plt.legend(handles, [str(i)+'%' for i in percentile_values], fontsize=15)

    #plt.show()
    plt.savefig(filename+'_instruction.png', dpi=300)

def mem_footprint_graph(df, title, filename):
    footprint = df['type'].value_counts()

    readi_footprint = footprint['readi']
    readd_footprint = footprint['readd']
    read_footprint = footprint['read']
    write_footprint = footprint['write']
    total_footprint = footprint['read&write']

    x = range(3)
    labels = ['total', 'readi', 'readd', 'write']
    values = [total_footprint, readi_footprint, readd_footprint, write_footprint]
    colors = ['lightgrey', 'c', 'dodgerblue', 'red']
    handles = [plt.Rectangle((0,0),1,1, color=colors[i]) for i in range(4)]
    percentile_values = np.divide(values[1:], total_footprint/100).round(3)

    fig, ax = plot_frame((1, 1), title=title, xlabel='instruction type', ylabel='Memory footprint (4KB)', share_yaxis='col')
    
    for i in x:
        plt.bar(i, values[0], color=colors[0])
    rects = plt.bar(x, values[1:], color=colors[1:])
    plt.xticks(x, labels[1:])
    plt.yticks([])
    plt.bar_label(rects, [f'{i:}%' for i in percentile_values], fontsize=20)
    plt.legend(handles, [f'{i:,}'+' (4KB)' for i in values], loc='upper left', fontsize=15)

    #plt.show()
    plt.savefig(filename+'_mem-footprint.png', dpi=300)

"""memdf1.1 graph"""
def ref_cnt_graph(df, title, filename, dense = False, ylim : list = None):
    if dense:
        df['blockaddress'] = df['blockaddress'].rank(ascending=True, method='dense')

    x1 = df['blockaddress'][(df['type']=='readi')]
    x2 = df['blockaddress'][(df['type']=='readd')]
    x3 = df['blockaddress'][(df['type']=='write')]
    x = df['blockaddress'][(df['type']=='read&write')]

    y1 = df['count'][(df['type']=='readi')]
    y2 = df['count'][(df['type']=='readd')]
    y3 = df['count'][(df['type']=='write')]
    y = df['count'][(df['type']=='read&write')]

    if dense:
        fig, ax = plot_frame((2, 1), (7, 4), title=title, xlabel='(virtual) memory block address', ylabel='memory block reference count', share_yaxis=False)
    else:
        fig, ax = plot_frame((3, 1), (7, 4), title=title, xlabel='(virtual) memory block address', ylabel='memory block reference count')

    if ylim:
        plt.setp(ax, ylim=ylim)

    #print("readi count[min,max]:", y1.min(), y1.max(), digit_length(y1.max()))
    #print("readd count[min,max]:", y2.min(), y2.max(), digit_length(y2.max()))
    #print("write count[min,max]:", y3.min(), y3.max(), digit_length(y3.max()))

    if dense:
        ax[0].bar(x1, y1, color='c', edgecolor='c', label='readi')
        ax[0].bar(x2, y2, color='dodgerblue', edgecolor='dodgerblue', label='readd')
        ax[0].legend(loc='upper right', ncol=1, fontsize=20)

        ax[1].bar(x3, y3, color='red', edgecolor='red', label='write')
        ax[1].legend(loc='lower right', ncol=1, fontsize=20)

        ax0_yrange = ax[0].get_ylim()
        ax1_yrange = ax[1].get_ylim()

        if ax0_yrange[1] > ax1_yrange[1]:
            ax[1].set_ylim(ax0_yrange)
        else:
            ax[0].set_ylim(ax1_yrange)
        ax[1].invert_yaxis()

        fig.tight_layout()
        fig.subplots_adjust(hspace=0.0) # wspace=0.0

    else:
        x_list = [x1, x2, x3]
        y_list = [y1, y2, y3]
        color = ['c', 'dodgerblue', 'red', 'green']
        label = ['readi', 'readd', 'write', 'read&write']
        
        for i in range(len(x_list)):
            ax[i].scatter(x_list[i], y_list[i], color=color[i], label=label[i], s=3)
            ax[i].legend(loc='upper right', ncol=1, fontsize=20, markerscale=3) #loc = (1.0,0.8)

    #plt.show()
    plt.savefig(filename+'.png', dpi=300)

"""memdf1.2 graph"""
def ref_cnt_distribute(ref_count, filename='output', log_scale=False):
    if log_scale:
        bin_list = [1]
        x_lim = ref_count.max()
        bin_list.extend([ 10**i + 1 for i in range(digit_length(x_lim) + 1) ])
    else:
        bin_list = ref_count.unique()
        bin_list = np.append(bin_list, bin_list.max()+1)
        bin_list = np.sort(bin_list)
  
    counts, edges = np.histogram(ref_count, bins=bin_list, density=False)
    relative_counts, edges = np.histogram(ref_count, bins=bin_list, density=True)
    
    df = pd.DataFrame()
    if log_scale:
        df['edges'] = [i - 1 for i in edges][1:]
    else:
        df['edges'] = edges[:-1]
    df['counts'] = counts
    df['multiply_counts'] = df['edges'] * df['counts']
    df['relative_counts'] = relative_counts

    counts_list = list(counts)
    print(edges[counts_list.index(counts.max())], counts.max())

    return df

def ref_cnt_distribute_graph(df, title, filename, log_xscale = True, cnt_ylim : list = None, dist_ylim : list = None):
    y1 = df['count'][(df['type']=='readi')]
    y2 = df['count'][(df['type']=='readd')]
    y3 = df['count'][(df['type']=='write')]
    y = df['count'][(df['type']=='read&write')]

    y_list = [y1, y2, y3, y]
    color = ['c', 'dodgerblue', 'red', 'green']
    label = ['readi', 'readd', 'write', 'read&write']
   
    if log_xscale:
        fig, ax = plot_frame((len(y_list), 2), title=title, xlabel='reference count', ylabel='# of memory block', font_size=40, share_yaxis='col')
        
        for i in range(len(y_list)):
            ref_cnt_df = ref_cnt_distribute(y_list[i], log_scale=True)
            edges, counts, multiply_counts, relative_counts = ref_cnt_df['edges'], ref_cnt_df['counts'], ref_cnt_df['multiply_counts'], ref_cnt_df['relative_counts']

            edges = ['$\mathregular{10^'+str(int(i))+'}$' if i >= 1 else str(1) for i in np.log10(edges)]

            """histogram"""
            bars = ax[i][0].bar(edges, counts, color=color[i], edgecolor=color[i], label=label[i])
            ax[i][0].legend(loc='upper right', ncol=1, fontsize=20)
            hist_label(ax[i][0], counts, bars)

            """normalized histogram"""
            bars = ax[i][1].bar(edges, relative_counts, color=color[i], edgecolor=color[i], label=label[i])    
            ax[i][1].legend(loc='upper right', ncol=1, fontsize=20)
            hist_label(ax[i][1], relative_counts, bars, 5)
    
    else:
        fig, ax = plot_frame((len(y_list), 3), title=title, xlabel='reference count', ylabel='# of memory block', font_size=50, share_yaxis='col')

        for i in range(len(y_list)):
            ref_cnt_df = ref_cnt_distribute(y_list[i], log_scale=False)
            edges, counts, multiply_counts, relative_counts = ref_cnt_df['edges'], ref_cnt_df['counts'], ref_cnt_df['multiply_counts'], ref_cnt_df['relative_counts']
            #ref_cnt_df.to_csv(filename+'_'+label[i]+'.csv')

            """histogram"""
            ax[i][0].bar(edges, counts, color=color[i], edgecolor=color[i], label=label[i])
            ax[i][0].legend(loc='upper right', ncol=1, fontsize=30)

            """normalized histogram"""
            ax[i][1].bar(edges, multiply_counts, color=color[i], edgecolor=color[i], label=label[i])
            ax[i][1].legend(loc='upper right', ncol=1, fontsize=30)
            
            """multiplied scale histogram"""
            ax[i][2].bar(edges, relative_counts, color=color[i], edgecolor=color[i], label=label[i])
            ax[i][2].legend(loc='upper right', ncol=1, fontsize=30)

    if cnt_ylim:
        ax[0][0].set_ylim(cnt_ylim)
    if dist_ylim:
        ax[0][1].set_ylim(dist_ylim)

    #plt.show()
    plt.savefig(filename+'_hist.png', dpi=300)

#-----
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="plot reference count per each block")
    parser.add_argument("--input", "-i", metavar='I', type=str, nargs='?', default='input.txt',
                        help='input file')
    parser.add_argument("--output", "-o", metavar='O', type=str, nargs='?', default='output.txt',
                        help='output file')
    parser.add_argument("--plot_rawcnt", "-r", action='store_true',
                        help='plot histogram of log file by instruction type')
    parser.add_argument("--plot_distribution", "-d", action='store_true',
                        help='plot histogram bound by reference count')
    parser.add_argument("--title", "-t", metavar='T', type=str, nargs='?', default='',
                        help='title of a graph')
    args = parser.parse_args()

    memdf1 = ref_cnt_per_block(input_filename=args.input)
    save_csv(memdf1, args.output+'.csv', 0)

    #memdf1 = pd.read_csv(args.output+'.csv', sep=',', header=0, index_col=0, on_bad_lines='skip')

    if (args.plot_rawcnt):
        instruction_cnt_graph(title=args.title, filename=args.output, readi_cnt=memdf1.iloc[0, 3], readd_cnt=memdf1.iloc[0, 4], write_cnt=memdf1.iloc[0, 5])
        mem_footprint_graph(df=memdf1, title=args.title, filename=args.output)

    ref_cnt_graph(memdf1, title=args.title, dense=False, filename=args.output)
    ref_cnt_graph(memdf1, title=args.title, dense=True, filename=args.output+'_dense')

    if (args.plot_distribution):
        plt.clf() # Clear the current figure
        ref_cnt_distribute_graph(memdf1, title=args.title, filename=args.output+'-1', log_xscale=True)
        ref_cnt_distribute_graph(memdf1, title=args.title, filename=args.output+'-2', log_xscale=False)
