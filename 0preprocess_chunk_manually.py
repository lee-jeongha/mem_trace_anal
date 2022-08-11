# -*- coding: utf-8 -*-

import argparse
import pandas as pd
import os
from load_and_save import save_csv

"""##**preprocess**"""

def read_logfile_chunk(input_filename, output_filename, chunksize=1000000):
    f = open(input_filename, 'r')
    #memdata = f.readlines() # read all lines from file
    line_num = 0
    fw = open(output_filename+'_chunk0.txt', 'w')
    while True:
        line = f.readline()

        if not (line.startswith('read') or line.startswith('write')):
            if line=='':
                print("End Of File, line =", line_num)
                break
            else:
                continue
        else:
            line_num += 1
            fw.write(line)

        if line_num % chunksize == 0:
            fw.close()
            fw = open(output_filename+'_chunk'+str(line_num // chunksize)+'.txt', 'w')
            print("line_num:",line_num)
    f.close()
    fw.close()

def chunk_preprocess(df):
    invalid_idx = df[ (df['type'].str.contains('==')) ].index
    df.drop(invalid_idx, inplace = True)

    df['blockaddress'] = [ int(i,16) >> 12 for i in df["address"] ]

    #df = df.replace('readi', 'read')
    #df = df.replace('readd', 'read')

    return df

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="for preprocess log file")
    parser.add_argument("--input", "-i", metavar='I', type=str, nargs='?', default='input.txt',
                        help='input file')
    parser.add_argument("--output", "-o", metavar='O', type=str, nargs='?', default='output.txt',
                        help='output file')
    parser.add_argument("--chunksize", "-c", metavar='C', type=int, nargs='?', default=1000000,
                        help='the number of rows in each chunk groups')
    args = parser.parse_args()

    path = args.output[:args.output.rfind('/')]
    if not os.path.exists(path):    # FileNotFoundError: [Errno2] No such file or directory: '~'
        os.makedirs(path)

    read_logfile_chunk(args.input, args.output, chunksize=args.chunksize)

    i = 0
    while True:
        try:
            chunk = pd.read_csv(args.output+'_chunk'+str(i)+'.txt', names=['type', 'address', 'size'], delim_whitespace=True, lineterminator="\n", header=None, on_bad_lines='skip')
            #chunk = pd.read_csv(args.output+'_chunk'+str(i)+'.txt', names=['type', 'address', 'size'], delim_whitespace=True, escapechar="\n", lineterminator="\r", header=None, on_bad_lines='skip')
        except FileNotFoundError:
            print("no file named:", args.output+'_chunk'+str(i)+'.txt')
            break

        chunk = chunk_preprocess(chunk)

        #save_csv(chunk, args.output+'.csv', i)
        save_csv(chunk, args.output+'_'+str(i)+'.csv', 0)
        os.remove(args.output+'_chunk'+str(i)+'.txt')
        
        print("chunk", i)
        i += 1
