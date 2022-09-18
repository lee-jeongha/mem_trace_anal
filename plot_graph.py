import argparse
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import ticker

from load_and_save import json_to_csv

def plot_frame(subplot_matrix : tuple = (1, 1), subplot_figsize : tuple = (7, 7), title = '', xlabel = '', ylabel = '', font_size = 20, log_scale = False, share_xaxis : str or bool = True, share_yaxis : str or bool = True):
    subplot_rows = subplot_matrix[0]
    subplot_cols = subplot_matrix[1]
    subplot_row_size = subplot_matrix[1] * subplot_figsize[0]
    subplot_col_size = subplot_matrix[0] * subplot_figsize[1]

    font_size = font_size
    plt.rc('font', size=font_size)

    fig, ax = plt.subplots(subplot_rows, subplot_cols, figsize=(subplot_row_size, subplot_col_size), constrained_layout=True, sharex=share_xaxis, sharey=share_yaxis)

    if title != '':
        plt.suptitle(title, fontsize = font_size + 10)

    if log_scale:
        plt.xscale('log')
        plt.yscale('log')

    if xlabel != '':
        fig.supxlabel(xlabel, fontsize = font_size + 5)
    if ylabel != '':
        fig.supylabel(ylabel, fontsize = font_size + 5)

    return fig, ax

def lru_lfu_graph(figures : tuple, graph_type, fig_col_num, title, label_list, filename, xlim : list = None, ylim : list = None):
    if graph_type=='lru':
        fig, ax = plot_frame((fig_col_num, 1), title=title, xlabel='page ranking', ylabel='# of references', log_scale=True)
    elif graph_type=='lfu':
        fig, ax = plot_frame((fig_col_num, 1), title=title, xlabel='page ranking', ylabel='# of references', log_scale=True)


    if xlim:
        plt.setp(ax, xlim=xlim)
    if ylim:
        plt.setp(ax, ylim=ylim)

    color_dict = {'inst. read':'c', 'data read':'dodgerblue', 'read':'blue', 'data write':'red', 'total':'green'}
    label_num = 0
    if fig_col_num == 1:
        for cnt_list_num in range(len(figures)):
            cnt_list = figures[cnt_list_num]

            ax.scatter(range(1, len(cnt_list)+1), cnt_list, color=color_dict[label_list[label_num]], label=label_list[label_num], s=5)
            ax.legend(loc='upper right', ncol=1, fontsize=20, markerscale=3)
            label_num += 1
    else:
        for fig_num in range(fig_col_num):
            for cnt_list_num in range(len(figures[fig_num])):
                cnt_list = figures[fig_num][cnt_list_num]

                ax[fig_num].scatter(range(1, len(cnt_list)+1), cnt_list, color=color_dict[label_list[label_num]], label=label_list[label_num], s=5)
                ax[fig_num].legend(loc='upper right', ncol=1, fontsize=20, markerscale=3)
                label_num += 1
    
    #plt.show()
    plt.savefig(filename+'.png', dpi=300)

def lru_and_lfu_by_type_graph(lru_df, lfu_df, column_list, title, filename, xlim : list = None, ylim : list = None):
    for col in column_list:
        fig, ax = plot_frame((1, 1), title=title+' ('+col+')', xlabel='page ranking', ylabel='# of references', log_scale=True)
    
        if xlim:
            plt.setp(ax, xlim=xlim)
        if ylim:
            plt.setp(ax, ylim=ylim)

        x1 = range(1,len(lru_df[col+'_cnt'])+1)
        y1 = lru_df[col+'_cnt']
        x2 = range(1,len(lfu_df[col+'_cnt'])+1)
        y2 = lfu_df[col+'_cnt']
        plt.scatter(x1, y1, color='red', label='LRU', s=5)
        plt.scatter(x2, y2, color='blue', label='LFU', s=5)
        plt.legend(loc='upper right', ncol=1, fontsize=20, markerscale=3)
        ax.xaxis.set_major_locator(ticker.LogLocator(numticks=8))
        ax.yaxis.set_major_locator(ticker.LogLocator(numticks=8))
        plt.savefig(filename+'_'+col+'.png', dpi=300)
        plt.clf()

#-----
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="plot lru/lfu graph from log file")
    parser.add_argument("--output", "-o", metavar='F', type=str, nargs='?', default='output.txt',
                        help='output file name')
    parser.add_argument("--lru", "-r", metavar='R', type=str, nargs='?', help='lru reference count file')
    parser.add_argument("--lfu", "-f", metavar='F', type=str, nargs='?', help='lfu reference count file')
    parser.add_argument("--end_chunk", "-e", metavar='E', type=int, nargs='?', default=100,
                        help='end chunk index')
    parser.add_argument("--fig_num", "-n", metavar='T', type=int, nargs='?', default=2,
                        help='# of figures in subplot')
    parser.add_argument("--title", "-t", metavar='T', type=str, nargs='?', default='',
                        help='title of a graph')
    args = parser.parse_args()

    if args.lru and args.lfu:
        # Save All Checkpoints to Single '.csv' File
        lru_df = json_to_csv(filename=args.lru, ckpt=('readi', 'readd', 'read', 'write'), endpoint=args.end_chunk)
        lfu_df = json_to_csv(filename=args.lfu, ckpt=('readi', 'readd', 'read', 'write'), endpoint=args.end_chunk)

        # Plot LRU/LFU Graph
        if args.fig_num == 1:
            lru_figure_tuple = ([lru_df['readi_cnt'], lru_df['readd_cnt'], lru_df['write_cnt']])
            lfu_figure_tuple = ([lfu_df['readi_cnt'], lfu_df['readd_cnt'], lfu_df['write_cnt']])
        else:
            lru_figure_tuple = ([lru_df['readi_cnt'], lru_df['readd_cnt']], [lru_df['write_cnt']])
            lfu_figure_tuple = ([lfu_df['readi_cnt'], lfu_df['readd_cnt']], [lfu_df['write_cnt']])
        label_list = ['inst. read', 'data read', 'data write']
        lru_lfu_graph(figures=lru_figure_tuple, graph_type='lru', fig_col_num=args.fig_num, title=args.title, label_list=label_list, filename=args.lru, xlim=[0, 1e6], ylim=[0,1e6])
        lru_lfu_graph(figures=lfu_figure_tuple, graph_type='lfu', fig_col_num=args.fig_num, title=args.title, label_list=label_list, filename=args.lfu, xlim=[0, 1e6], ylim=[0,1e6])

        lru_and_lfu_by_type_graph(lru_df=lru_df, lfu_df=lfu_df, column_list=['readi', 'readd', 'write'], title=args.title, filename=args.output, xlim=[0, 1e6], ylim=[0,1e6])

    elif args.lru or args.lfu:
        if args.lru:
            ckpt_file = args.lru
        elif args.lfu:
            ckpt_file = args.lfu
        
        # Save All Checkpoints to Single '.csv' File
        df = json_to_csv(filename=ckpt_file, ckpt=('readi', 'readd', 'read', 'write'), endpoint=args.end_chunk)
        #df = json_to_csv(filename=ckpt_file, ckpt=('readi', 'readd', 'rw_by_type'), endpoint=args.end_chunk)
        #df = json_to_csv(filename=ckpt_file, ckpt=('overall_rank'), endpoint=args.end_chunk)
        #df = json_to_csv(filename=ckpt_file, ckpt=('rw_by_type', 'overall_rank'), endpoint=args.end_chunk, rw_column=True)

        # Plot LRU/LFU Graph
        if args.fig_num == 1:
            figure_tuple = ([df['readi_cnt'], df['readd_cnt'], df['write_cnt']])
        else:
            figure_tuple = ([df['readi_cnt'], df['readd_cnt']], [df['write_cnt']])
        label_list = ['inst. read', 'data read', 'data write']

        if args.lru:
            lru_lfu_graph(figures=figure_tuple, graph_type='lru', fig_col_num=args.fig_num, title=args.title, label_list=label_list, filename=ckpt_file, xlim=[0, 1e6], ylim=[0,1e6])
        elif args.lfu:
            lru_lfu_graph(figures=figure_tuple, graph_type='lfu', fig_col_num=args.fig_num, title=args.title, label_list=label_list, filename=ckpt_file, xlim=[0, 1e6], ylim=[0,1e6])