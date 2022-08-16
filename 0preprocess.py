# -*- coding: utf-8 -*-

import argparse
import pandas as pd
from load_and_save import save_csv

"""##**preprocess**"""

def read_logfile_chunk(filename, chunksize):
    # 1. find start line
    f = open(filename, 'r')
    #memdata = f.readlines() # read all lines from file
    startline = 0
    while True:
        line = f.readline()
        startline += 1
        if (line.startswith('read') or line.startswith('write')):
            break
    f.close()
    print("startline:",startline)

    # 2. read csv file
    chunk = pd.read_csv(filename, names=['type', 'address', 'size'], delim_whitespace=True, lineterminator="\n", skiprows=startline-1, chunksize=chunksize, header=None, on_bad_lines='skip')
    #chunk = pd.read_csv(filename, names=['type', 'address', 'size'], delim_whitespace=True, escapechar="\n", lineterminator="\r", skiprows=startline-1, chunksize=chunksize, header=None, on_bad_lines='skip')
    chunk = list(chunk)
  
    return chunk

def chunk_preprocess(df):
    invalid_idx = df[ (df['type'].str.contains('==')) ].index
    df.drop(invalid_idx, inplace = True)

    df['blockaddress'] = [ int(i,16) >> 12 for i in df["address"] ]
    
    #df = df.replace('readi', 'read')
    #df = df.replace('readd', 'read')

    return df

#-----
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="for preprocess log file")
    parser.add_argument("--input", "-i", metavar='I', type=str, nargs='?', default='input.txt',
                        help='input file')
    parser.add_argument("--output", "-o", metavar='O', type=str, nargs='?', default='output.txt',
                        help='output file')
    parser.add_argument("--chunksize", "-c", metavar='C', type=int, nargs='?', default=1000000,
                        help='the number of rows in each chunk groups')
    args = parser.parse_args()

    chunk = read_logfile_chunk(filename=args.input, chunksize=args.chunksize)
    for i in range(len(chunk)):
        chunk[i] = chunk_preprocess(chunk[i])
        #save_csv(chunk[i], args.output+'.csv', i)
        save_csv(chunk[i], args.output+'_'+str(i)+'.csv', 0)
        print(i)
    print('done!!')
