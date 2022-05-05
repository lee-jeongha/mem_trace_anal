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
import os

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


def save_csv(df, filename, index=0):
  try:
    if index==0:
      df.to_csv(filename, index=True, header=True, mode='w') # encoding='utf-8-sig'
    else: #append mode
      df.to_csv(filename, index=True, header=False, mode='a') # encoding='utf-8-sig'
  except OSError:	# OSError: Cannot save file into a non-existent directory: '~'
    #if not os.path.exists(path):
    target_dir = filename.rfind('/')
    path = filename[:target_dir]
    os.mkdir(path)
    #---
    if index==0:
      df.to_csv(filename, index=True, header=True, mode='w') # encoding='utf-8-sig'
    else: #append mode
      df.to_csv(filename, index=True, header=False, mode='a') # encoding='utf-8-sig'

#-----
chunk = read_logfile_chunk(filename=args.input)
for i in range(len(chunk)):
  chunk[i] = read_write(chunk[i])
  save_csv(chunk[i], args.output, i)
  save_csv(chunk[i], args.output[:-4]+'4_'+str(i)+'.csv', 0)
  print(i)
print('done!!')
