# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import json

"""##**memdf3 = tendency toward temporal locality**
* x axis : rank(temporal locality)
* y axis : memory block access count
"""

def temp_local(df, block_rank, readcnt, writecnt):
  '''#각 blockaddress가 이전 행에서 나왔던 것인지를 확인하기 위함
  dupli = df.duplicated(subset=['blockaddress'])
  print(dupli)'''

  #---

  '''block_rank = list()
  #readcnt = list()
  readcnt = [0 for i in range(len(df))] #list index out of range를 피하기 위해 여기서는 우선 df 길이만큼 선언
  writecnt = [0 for i in range(len(df))]'''

  #---
  
  for index, row in df.iterrows(): ### one by one
    ###1. block_rank에 있는지 확인
    #---if ( (dupli[index]) or (row['blockaddress'] in dupl_block) ): #***(index번째 순서가 duplicate 상태인지 확인) or (이전 chunk에서 방문했던 block인지 확인)
    try:   ###2-1. 있으면 block_rank 순서 바꿈, type과 rank 맞춰서 readcnt/writecnt 수정
      acc_rank = block_rank.index(row['blockaddress']) #이번에 읽어온 'blockaddress'의 위치를 acc_rank에 담음
      _ = block_rank.pop(acc_rank) #acc_rank번째 요소를 돌려주고 삭제
      block_rank.insert(0, row['blockaddress']) #block_rank의 0번째에 이번에 읽어온 'blockaddress'를 삽입

      if (row['type']=='readi' or row['type']=='readd'): ###read이면
        try:
          readcnt[acc_rank] += 1 #readcnt의 acc_rank번째 요소를 1 증가
        except IndexError: #***list index out of range
          for i in range(len(readcnt),acc_rank+1):
            readcnt.insert(i,0)
          readcnt[acc_rank] += 1

      else:                  ###write면
        #writecnt[acc_rank] += 1 #writecnt의 acc_rank번째 요소를 1 증가
        try:
          writecnt[acc_rank] += 1
        except IndexError:
          for i in range(len(writecnt),acc_rank+1):
            writecnt.insert(i,0)
          writecnt[acc_rank] += 1

    #---else: "ValueError: 4 is not in list"
    except ValueError:   ###2-2. 없으면 block_rank 맨 앞에 삽입, readcnt/writecnt는 건드리지 않음
      block_rank.insert(0, row['blockaddress']) #block_rank의 0번째에 이번에 읽어온 'blockaddress'를 삽입

  return block_rank, readcnt, writecnt

def save_json(block_rank, readcnt, writecnt, i):
  save = {'block_rank': block_rank,
          'readcnt': readcnt,
          'writecnt': writecnt}
          #,'dupl_block': list(dupl_block)}

  with open("./checkpoint/checkpoint"+str(i)+".json", 'w', encoding='utf-8') as f:
      # indent=2 is not needed but makes the file human-readable 
      # if the data is nested
      json.dump(save, f, indent=2)

def load_json(i):
  with open("./checkpoint/checkpoint"+str(i)+".json", 'r') as f:
      load = json.load(f)
  
  block_rank = load['block_rank']
  readcnt = load['readcnt']
  writecnt = load['writecnt']
  #dupl_block = set(load['dupl_block'])
  print(load)

  return block_rank, readcnt, writecnt#, dupl_block

block_rank = list()
readcnt = list()
writecnt = list()
#dupl_block = set()

## 1. use list of chunk
'''
memdf = pd.read_csv('memdf.csv', sep=',', chunksize=1000000, header=0, index_col=0, error_bad_lines=False)
memdf = list(memdf)
print(memdf[-1].head)
print(memdf[0].head)

for i in range(len(memdf)):
  memdf[i]['time'] = memdf[i].index
  if(i>0):
    block_rank, readcnt, writecnt = load_json(i-1)
    print(block_rank, readcnt, writecnt)
  block_rank, readcnt, writecnt = temp_local(memdf[i], block_rank, readcnt, writecnt)
  save_json(block_rank, readcnt, writecnt, i)
'''

## 2. load separate .csv file
def cal_temp_local(startpoint, endpoint):#, Subsequent=False):
  block_rank = list()
  readcnt = list()
  writecnt = list()
  if(startpoint>0):
    block_rank, readcnt, writecnt = load_json(startpoint-1)
    print(block_rank, readcnt, writecnt)
  for i in range(startpoint, endpoint+1):
    memdf = pd.read_csv('./memdf/memdf0_'+str(i)+'.csv', sep=',', header=0, index_col=0, error_bad_lines=False)
    block_rank, readcnt, writecnt = temp_local(memdf, block_rank, readcnt, writecnt)
    save_json(block_rank, readcnt, writecnt, i)

cal_temp_local(0, 72)#, Subsequent=False)

"""##**memdf3 graph**"""

def load_json(i):
  with open("./checkpoint/checkpoint"+str(i)+".json", 'r') as f:
      load = json.load(f)
  
  block_rank = load['block_rank']
  readcnt = load['readcnt']
  writecnt = load['writecnt']
  #dupl_block = set(load['dupl_block'])
  print(load)

  return block_rank, readcnt, writecnt#, dupl_block

block_rank, readcnt, writecnt = load_json(71)

#--
fig, ax = plt.subplots(2, figsize=(24,20), constrained_layout=True, sharex=True, sharey=True) # sharex=True: share x axis

#read
x1 = range(1,len(readcnt)+1)
y1 = readcnt

#write
x2 = range(1,len(writecnt)+1)
y2 = writecnt


# read graph
ax[0].scatter(x1, y1, color='blue', label='read', s=5)
ax[0].set_xscale('log')
ax[0].set_yscale('log')
# legend
ax[0].set_xlabel('rank(temporal locality)')
ax[0].set_ylabel('access count')
ax[0].legend(loc=(1.0,0.8), ncol=1) #loc = 'best', 'upper right'

# write graph
ax[1].scatter(x2, y2, color='red', label='write', s=5)
ax[1].set_xscale('log')
ax[1].set_yscale('log')
ax[1].set_ylim([0.5, 1e7])
# legend
ax[1].set_xlabel('rank(temporal locality)')
ax[1].set_ylabel('access count')
ax[1].legend(loc=(1.0,0.8), ncol=1) #loc = 'best'


#plt.show()
plt.savefig('callgrind-mnist-v3.3.final.png', dpi=300)
