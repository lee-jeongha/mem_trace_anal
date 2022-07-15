# -*- coding: utf-8 -*-

import argparse
import pandas as pd
import numpy as np
from load_and_save import save_csv

"""##**memaccess**"""

def read_logfile_chunk(filename):
    # 1. read csv file
    chunk = pd.read_csv(filename, names=['type', 'address', 'size', 'blockaddress'], header=0, chunksize=1000000)
    chunk = list(chunk)
    for i in range(len(chunk)):
        chunk[i] = chunk[i].drop(['address','size'], axis=1)  
    return chunk

def read_write(df):
    df['acc_blk'] = df['blockaddress'].rank(method='dense')
    df['blk_readi'] = df['acc_blk']
    df['blk_readd'] = df['acc_blk']
    df['blk_write'] = df['acc_blk']

    df.loc[(df.type!='readi'), 'blk_readi'] = np.NaN
    df.loc[(df.type!='readd'), 'blk_readd'] = np.NaN
    df.loc[(df.type!='write'), 'blk_write'] = np.NaN

    return df

#-----
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="assign unique number to accessed memory area")
    parser.add_argument("--input", "-i", metavar='I', type=str, nargs='?', default='input.txt',
                        help='input file')
    parser.add_argument("--output", "-o", metavar='O', type=str, nargs='?', default='output.txt',
                        help='output file')
    args = parser.parse_args()

    chunk = read_logfile_chunk(filename=args.input+'.csv')
    for i in range(len(chunk)):
        chunk[i] = read_write(chunk[i])
        save_csv(chunk[i], args.output, i)
        save_csv(chunk[i], args.output+'_'+str(i)+'.csv', 0)
        print(i)
    print('done!!')
