# -*- coding: utf-8 -*-

import argparse
parser = argparse.ArgumentParser(description="for preprocess log file")
parser.add_argument('input', metavar='I', type=str, nargs='?', default='input.txt',
                    help='input file')
parser.add_argument('output', metavar='O', type=str, nargs='?', default='output.txt',
                    help='output file')
args = parser.parse_args()


import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

"""##**preprocess**"""

def read_logfile_chunk(filename):
  
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
  #chunk = pd.read_csv(filename, names=['type', 'address', 'size'], delim_whitespace=True, lineterminator="\n", skiprows=startline-1, chunksize=1000000, header=None, on_bad_lines='skip')
  chunk = pd.read_csv(filename, names=['type', 'address', 'size'], delim_whitespace=True, escapechar="\n", lineterminator="\r", skiprows=startline-1, chunksize=1000000, header=None, on_bad_lines='skip')
  chunk = list(chunk)
  #print(chunk[-1])
  
  return chunk

def chunk_preprocess(df):
  invalid_idx = df[ (df['type'].str.contains('==')) ].index
  df.drop(invalid_idx, inplace = True)

  df['blockaddress'] = [ int(i,16) >> 12 for i in df["address"] ]
  #df['blockaddress'] = df['address'].str.slice(stop=-3) # 맨 뒤자리 3개 없앰 (4KB 단위로 묶음)
  #df['blockaddress_int'] = df['blockaddress'].apply(int, base=16)
  
  #df = df.replace('readi', 'read')
  #df = df.replace('readd', 'read')

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

chunk = read_logfile_chunk(filename=args.input)
for i in range(len(chunk)):
  chunk[i] = chunk_preprocess(chunk[i])
  save_csv(chunk[i], args.output, i)
  save_csv(chunk[i], args.output[:-4]+'_'+str(i)+'.csv', 0)
  print(i)
print('done!!')
