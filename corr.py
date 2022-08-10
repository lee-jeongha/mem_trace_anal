import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def read_write_correlation(df, col_type):
    read = df[['blockaddress',col_type]][(df['type']=='read')]
    read_l = len(read) #// 10
    read = read.sort_values(by=col_type, ascending=True)[:read_l]

    write = df[['blockaddress',col_type]][(df['type']=='write')]
    write_l = len(write) #// 10
    write = write.sort_values(by=col_type, ascending=True)[:write_l]

    #---
    read_write_rank = pd.merge(read, write, left_on='blockaddress', right_on='blockaddress', how='outer', suffixes = ['_read', '_write'])

    #---
    only_read = read_write_rank[read_write_rank[col_type + '_write'].isnull()]
    only_write = read_write_rank[read_write_rank[col_type + '_read'].isnull()]
    print("only_read percentage",len(only_read)/len(read_write_rank), "only_write percentage",len(only_write)/len(read_write_rank))
    #---
    read_write_rank = read_write_rank.dropna()
    #print("\nread_write_rank\n",read_write_rank, "\nonly_read\n",only_read, "\nonly_write\n",only_write)

    #---
    """read_write_rank[col_type + '_read'] = read_write_rank[col_type + '_read'].fillna(value=1)
    read_write_rank[col_type + '_write'] = read_write_rank[col_type + '_write'].fillna(value=1)"""
    #print(read_write_rank)
    #---

    return read_write_rank

def read_write_correlation_graph(df, col_type, title, output_filename):
    font_size = 20
    plt.rc('font', size=font_size)

    sns.jointplot(data = df, x = col_type + '_read', y = col_type + '_write')
    plt.savefig(output_filename+'-1-1.png', dpi=300)

    sns.jointplot(data = df, x = col_type + '_read', y = col_type + '_write', kind="hex", color="#4CB391")
    plt.savefig(output_filename+'-1-2.png', dpi=300)

    sns.jointplot(data = df, x = col_type + '_read', y = col_type + '_write', kind="hist", color="#4CB391")
    plt.savefig(output_filename+'-1-3.png', dpi=300)

    sns.jointplot(data = df, x = col_type + '_read', y = col_type + '_write', kind="kde", color="#4CB391")
    plt.savefig(output_filename+'-1-4.png', dpi=300)

#------------#
def dense_ref_cnt_graph(df, title, output_filename):
    df['dense_blockaddress'] = df['blockaddress'].rank(ascending=False, method='dense')

    read = df[['dense_blockaddress', 'count']][(df['type']=='read')]
    write = df[['dense_blockaddress', 'count']][(df['type']=='write')]

    #---
    font_size = 22
    plt.rc('font', size=font_size)
    plt.suptitle(title, fontsize = font_size + 10)

    sns.kdeplot(read['dense_blockaddress'], weights=read['count'], legend='read', color='blue', bw_adjust=.001, shade=True)
    sns.kdeplot(write['dense_blockaddress'], weights=write['count'], legend='write', color='red', bw_adjust=.001, shade=True)
    #sns.kdeplot(rw['dense_blockaddress'], weights=rw['count'], legend='read&write', color='green', bw_adjust=.01, shade=True)
    plt.savefig(output_filename+'-2-1.png', dpi=300)

    #---
    x1 = read['dense_blockaddress']
    y1 = read['count']

    x2 = write['dense_blockaddress']
    y2 = write['count']

    fig, ax = plt.subplots(2, figsize=(10,8), sharex=True)
    plt.suptitle(title, fontsize = font_size + 10)

    ax[0].bar(x1, y1, color='blue', edgecolor='blue', label='read')
    ax[1].bar(x2, y2, color='red', edgecolor='red', label='write')

    if y1.max() > y2.max():
        y_range = ax[0].get_ylim()
        ax[1].set_ylim(y_range)
    else:
        y_range = ax[1].get_ylim()
        ax[0].set_ylim(y_range)

    ax[1].invert_yaxis()

    fig.tight_layout()
    fig.subplots_adjust(hspace=0.0) # wspace=0.0
    plt.savefig(output_filename+'-2-2.png', dpi=300)

if __name__ == "__main__" :
    parser = argparse.ArgumentParser()
    parser.add_argument("--cnt_input", "-c", type=str, nargs='?', default='memdf1')
    parser.add_argument("--rank_input", "-r", type=str, nargs='?', default='memdf2')
    parser.add_argument("--output", "-o", type=str, nargs='?', default='output')
    parser.add_argument("--title", "-t", type=str, nargs='?', default='')
    args = parser.parse_args()

    path = args.output[:args.output.rfind('/')]
    if not os.path.exists(path):    # FileNotFoundError: [Errno2] No such file or directory: '~'
        os.makedirs(path)

    df2 = pd.read_csv(args.rank_input+'.csv', header=0, index_col=0)
    col_type = 'type_pcnt_rank' # 'type_rank'
    read_write_rank = read_write_correlation(df2, col_type)
    print(read_write_rank.corr())

    read_write_correlation_graph(read_write_rank, col_type, args.title, args.output)

    plt.clf()
    df1 = pd.read_csv(args.cnt_input+'.csv', header=0, index_col=0)
    dense_ref_cnt_graph(df1, args.title, args.output)