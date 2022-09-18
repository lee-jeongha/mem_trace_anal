# -*- coding: utf-8 -*-

import argparse
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import pandas as pd
import numpy as np
from load_and_save import save_csv
from plot_graph import plot_frame


"""memdf2.1
* x axis : ranking by references count
* y axis : reference count
"""
def ref_count_rank(df):
    # ranking
    readi_rank = df['count'][(df['type']=='readi')].rank(ascending=False)
    df.loc[(df['type']=='readi'), ['type_rank']] = readi_rank

    readd_rank = df['count'][(df['type']=='readd')].rank(ascending=False)
    df.loc[(df['type']=='readd'), ['type_rank']] = readd_rank

    read_rank = df['count'][(df['type']=='read')].rank(ascending=False)
    df.loc[(df['type']=='read'), ['type_rank']] = read_rank

    write_rank = df['count'][(df['type']=='write')].rank(ascending=False)
    df.loc[(df['type']=='write'), ['type_rank']] = write_rank

    rw_rank = df['count'][(df['type']=='read&write')].rank(ascending=False)
    df.loc[(df['type']=='read&write'), ['type_rank']] = rw_rank

    return df

"""memdf2.2
* x axis : ranking by % of reference count (in percentile form)
* y axis : % of reference count
"""
def ref_count_percentile_rank(df):
    total_readi = df['count'][(df['type']=='readi')].sum()
    total_readd = df['count'][(df['type']=='readd')].sum()
    total_read = df['count'][(df['type']=='read')].sum()
    total_write = df['count'][(df['type']=='write')].sum()
    total_rw = df['count'][(df['type']=='read&write')].sum()

    # percentage
    df['type_pcnt'] = df['count']
    df.loc[(df['type']=='readi'), ['type_pcnt']] /= total_readi
    df.loc[(df['type']=='readd'), ['type_pcnt']] /= total_readd
    df.loc[(df['type']=='read'), ['type_pcnt']] /= total_read
    df.loc[(df['type']=='write'), ['type_pcnt']] /= total_write
    df.loc[(df['type']=='read&write'), ['type_pcnt']] /= total_rw

    # ranking in percentile form
    readi_rank = df['type_pcnt'][(df['type']=='readi')].rank(ascending=False, pct=True)
    df.loc[(df['type']=='readi'), ['type_pcnt_rank']] = readi_rank

    readd_rank = df['type_pcnt'][(df['type']=='readd')].rank(ascending=False, pct=True)
    df.loc[(df['type']=='readd'), ['type_pcnt_rank']] = readd_rank

    read_rank = df['type_pcnt'][(df['type']=='read')].rank(ascending=False, pct=True)
    df.loc[(df['type']=='read'), ['type_pcnt_rank']] = read_rank

    write_rank = df['type_pcnt'][(df['type']=='write')].rank(ascending=False, pct=True)
    df.loc[(df['type']=='write'), ['type_pcnt_rank']] = write_rank

    rw_rank = df['type_pcnt'][(df['type']=='read&write')].rank(ascending=False, pct=True)
    df.loc[(df['type']=='read&write'), ['type_pcnt_rank']] = rw_rank

    return df

"""zipf"""
def func_powerlaw(x, m, c):
    return x ** m * c

def zipf_fitting(freqs):
    from scipy.optimize import curve_fit

    target_func = func_powerlaw

    freqs = freqs[freqs != 0]
    y = freqs.sort_values(ascending=False).to_numpy()
    x = np.array(range(1, len(y) + 1))

    popt, pcov = curve_fit(target_func, x, y, maxfev=2000)
    #print(popt)

    return popt

"""memdf2.1 graph"""
def popularity_graph(df, title, filname, xlim : list = None, ylim : list = None, zipf=False, verbose=False):
    #readi
    x1 = df['type_rank'][(df['type']=='readi')]
    y1 = df['count'][(df['type']=='readi')]
    #readd
    x2 = df['type_rank'][(df['type']=='readd')]
    y2 = df['count'][(df['type']=='readd')]
    #read
    x3 = df['type_rank'][(df['type']=='read')]
    y3 = df['count'][(df['type']=='read')]
    #write
    x4 = df['type_rank'][(df['type']=='write')]
    y4 = df['count'][(df['type']=='write')]
    #read&write
    x = df['type_rank'][(df['type']=='read&write')]
    y = df['count'][(df['type']=='read&write')]

    if zipf:
        fig, ax = plot_frame((1, 1), title=title, xlabel='page ranking', ylabel='# of references', log_scale=True)

        if xlim:
            plt.setp(ax, xlim=xlim)
        if ylim:
            plt.setp(ax, ylim=ylim)

        x_list = [x, x1, x2, x3, x4]
        y_list = [y, y1, y2, y3, y4]
        colors = ['green', 'c', 'dodgerblue', 'blue', 'red']
        labels = ['total', 'inst. read', 'data read', 'read', 'data write']

        #scatter
        for i in [1,2,4,0]: #[1,2,3,4,0]:
            ax.scatter(x_list[i], y_list[i], color=colors[i], label=labels[i], s=3)

        #curve fitting
        zipf_colors = ['limegreen', 'skyblue', 'royalblue', 'darkblue', 'salmon']
        annotate_xy = [10, 30, 100, 500, 1000]
        annotate_xytext = [(-10.0, 30.0), (-50.0, -30.0), (-10.0, -50.0), (20.0, 30.0), (30.0, 10.0)]
        s_best = []
        for i in [0,1,2,3,4]:
            s_best.append(zipf_fitting(y_list[i]))
        print("========zipf", labels, "========")
        print([zipf[0] for zipf in s_best])
        
        for i in [1,2,4,0]: #[1,2,3,4,0]:
            ax.plot(x_list[i], func_powerlaw(x_list[i], *s_best[i]), color=zipf_colors[i], lw=2, label="curve_fitting: "+labels[i])
            if verbose:
                ax.annotate(str(round(s_best[i][0],5)), xy=(annotate_xy[i], func_powerlaw(annotate_xy[i], *s_best[i])), xycoords='data',
                         xytext=annotate_xytext[i], textcoords="offset points", color=zipf_colors[i], size=13,
                         arrowprops=dict(arrowstyle="->", ls="--", color=zipf_colors[i], connectionstyle="arc3,rad=-0.2"))

        # legend
        ax.legend(loc='lower left', ncol=1, fontsize=15, markerscale=3)

    else:
        fig, ax = plot_frame((1, 1), title=title, xlabel='page ranking', ylabel='# of references', log_scale=True)

        if xlim:
            plt.setp(ax, xlim=xlim)
        if ylim:
            plt.setp(ax, ylim=ylim)

        #scatter
        ax.scatter(x1, y1, color='c', label='inst. read', s=3)
        ax.scatter(x2, y2, color='dodgerblue', label='data read', s=3)
        #ax.scatter(x3, y3, color='blue', label='read', s=3)
        ax.scatter(x4, y4, color='red', label='data write', s=3)
        #ax.scatter(x, y, color='green', label='total', s=3)
        ax.legend(loc='lower left', ncol=1, fontsize=20, markerscale=3)

    #plt.show()
    plt.savefig(filname+'.png', dpi=300)


"""memdf2.2 graph"""
def pareto_graph(df, title, filname):
    fig, ax = plot_frame((1, 1), title=title, xlabel='rank (in % form)', ylabel='% of reference count')
    ax.set_axisbelow(True)
    ax.grid(True, color='black', alpha=0.5, linestyle='--')

    #readi
    y1 = df['type_pcnt'][(df['type']=='readi')].sort_values(ascending=False).cumsum()
    x1 = np.arange(len(y1)) / len(y1)
    #readd
    y2 = df['type_pcnt'][(df['type']=='readd')].sort_values(ascending=False).cumsum()
    x2 = np.arange(len(y2)) / len(y2)
    #read
    y3 = df['type_pcnt'][(df['type']=='read')].sort_values(ascending=False).cumsum()
    x3 = np.arange(len(y3)) / len(y3)
    #write
    y4 = df['type_pcnt'][(df['type']=='write')].sort_values(ascending=False).cumsum()
    x4 = np.arange(len(y4)) / len(y4)
    #read&write
    y = df['type_pcnt'][(df['type']=='read&write')].sort_values(ascending=False).cumsum()
    x = np.arange(len(y)) / len(y)

    x_list = [x, x1, x2, x3, x4]
    y_list = [y, y1, y2, y3, y4]
    colors = ['green', 'c', 'dodgerblue', 'blue', 'red']
    labels = ['total', 'inst. read', 'data read', 'read', 'data write']

    top20s = []
    for ys in y_list:
        top20s.append(ys.values.tolist()[int(len(ys)*0.2)])
    print("========top20%", labels, "========")
    print(top20s)

    #scatter
    for i in [1,2,4]: #[1,2,3,4,0]:
        ax.scatter(x_list[i], y_list[i], color=colors[i], label=labels[i], s=3)

    # legend
    ax.legend(loc='lower right', ncol=1, fontsize=20, markerscale=3)
    
    ax.xaxis.set_major_locator(MaxNLocator(6)) 
    ax.yaxis.set_major_locator(MaxNLocator(6))

    #plt.show()
    plt.savefig(filname+'_pareto.png', dpi=300)

#-----
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="plot popularity graph")
    parser.add_argument("--input", "-i", metavar='I', type=str, nargs='?', default='input.txt',
                        help='input file')
    parser.add_argument("--output", "-o", metavar='O', type=str, nargs='?', default='output.txt',
                        help='output file')
    parser.add_argument("--zipf", "-z", action='store_true',
                        help='calculate zipf parameter')
    parser.add_argument("--plot_pareto", "-p", action='store_true',
                        help='plot pareto graph')
    parser.add_argument("--title", "-t", metavar='T', type=str, nargs='?', default='',
                        help='title of a graph')
    args = parser.parse_args()

    """##**memdf2 = tendency of memory block access**"""
    memdf2 = pd.read_csv(args.input+'.csv', sep=',', header=0, index_col=0, on_bad_lines='skip')

    memdf2 = ref_count_rank(memdf2)
    memdf2 = ref_count_percentile_rank(memdf2)

    memdf2 = memdf2[['blockaddress', 'count', 'type', 'type_rank', 'type_pcnt', 'type_pcnt_rank']]
    save_csv(memdf2, args.output+'.csv', 0)

    popularity_graph(memdf2, title=args.title, filname=args.output, zipf=args.zipf, verbose=False)
    
    if (args.plot_pareto):
        plt.cla()
        pareto_graph(memdf2, title=args.title, filname=args.output)
