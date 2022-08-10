import argparse
import matplotlib.pyplot as plt
import pandas as pd

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

def lru_lfu_graph(figures : tuple, fig_col_num, title, label_list, filename, xlim : list = None, ylim : list = None):
    fig, ax = plot_frame((fig_col_num, 1), title=title, xlabel='rank(temporal locality)', ylabel='reference count', log_scale=True)

    if xlim:
        plt.setp(ax, xlim=xlim)
    if ylim:
        plt.setp(ax, ylim=ylim)

    color_dict = {'readi':'c', 'readd':'dodgerblue', 'read':'blue', 'write':'red', 'read&write':'green'}
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

#-----
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="plot lru/lfu graph from log file")
    parser.add_argument("--filename", "-f", metavar='F', type=str, nargs='?', default='filename.txt',
                        help='file name')
    parser.add_argument("--end_chunk", "-e", metavar='E', type=int, nargs='?', default=100,
                        help='end chunk index')
    parser.add_argument("--fig_num", "-n", metavar='T', type=int, nargs='?', default=2,
                        help='# of figures in subplot')
    parser.add_argument("--title", "-t", metavar='T', type=str, nargs='?', default='',
                        help='title of a graph')
    args = parser.parse_args()

    # Save All Checkpoints to Single '.csv' File
    df = json_to_csv(filename=args.filename, ckpt=('readi', 'readd', 'read', 'write'), endpoint=args.end_chunk)
    #df = json_to_csv(filename=args.filename, ckpt=('readi', 'readd', 'rw_by_type'), endpoint=args.end_chunk)
    #df = json_to_csv(filename=args.filename, ckpt=('overall_rank'), endpoint=args.end_chunk)
    #df = json_to_csv(filename=args.filename, ckpt=('rw_by_type', 'overall_rank'), endpoint=args.end_chunk, rw_column=True)

    # Plot LRU/LFU Graph
    df = pd.read_csv(args.filename+'.csv')
    
    if args.fig_num == 1:
        figure_tuple = ([df['readi_cnt'], df['readd_cnt'], df['write_cnt']])
    else:
        figure_tuple = ([df['readi_cnt'], df['readd_cnt']], [df['write_cnt']])
    label_list = ['readi', 'readd', 'write']
    lru_lfu_graph(figures=figure_tuple, fig_col_num=args.fig_num, title=args.title, label_list=label_list, filename=args.filename)