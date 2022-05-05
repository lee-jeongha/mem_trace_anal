# -*- coding: utf-8 -*-

import argparse
parser = argparse.ArgumentParser(description="use only accessed memory area")
parser.add_argument('input', metavar='I', type=str, nargs='?', default='input.txt',
                    help='input file')
parser.add_argument('output', metavar='O', type=str, nargs='?', default='output.txt',
                    help='output file')
args = parser.parse_args()


import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import json

"""##**memaccess**"""

def read_logfile_chunk(filename):
  # 1. read csv file
  chunk = pd.read_csv(filename, names=['type', 'address', 'size', 'blockaddress'], skiprows=startline-1, chunksize=100000)
  chunk = list(chunk)
  for i in range(len(chunk)):
    chunk[i] = chunk[i].drop(['address','size'], axis=1)
  
  return chunk

def read_write(df):
  df['acc_blk'] = df['blockaddress'].rank(moethod='dense')
  for i in range(len(df['acc_blk'])):
    if df['type'][i]=='readi':
      df['blk_readi'][i] = df['acc_blk'][i]
    elif df['type'][i]=='readd':
      df['blk_readd'][i] = df['acc_blk'][i]
    elif df['type'][i]=='write':
      df['blk_write'][i] = df['acc_blk'][i]


def save_csv(df, filename, index=0):
  #if not os.path.exists('memdf.csv'):
  if index==0:
    df.to_csv(filename, index=True, header=True, mode='w') # encoding='utf-8-sig'
  else: #append mode
    df.to_csv(filename, index=True, header=False, mode='a') # encoding='utf-8-sig'

chunk = read_logfile_chunk(filename=args.input)
for i in range(len(chunk)):
  chunk[i] = chunk_preprocess(chunk[i])
  save_csv(chunk[i], args.output, i)
  save_csv(chunk[i], args.output[-4:]+'_str(i).csv', 0)
  print(i)
print('done!!')
