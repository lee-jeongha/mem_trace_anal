import os
import json
import numpy as np
import pandas as pd

def save_csv(df, filename, index=0):
    path = filename[:filename.rfind('/')]

    if not os.path.exists(path):    # FileNotFoundError: [Errno2] No such file or directory: '~'
        os.makedirs(path)

    if index==0:
        df.to_csv(filename, index=True, header=True, mode='w') # encoding='utf-8-sig'
    else: #append mode
        df.to_csv(filename, index=True, header=False, mode='a') # encoding='utf-8-sig'

def save_json(savings, filename):
    path = filename[:filename.rfind('/')]

    if not os.path.exists(path):    # FileNotFoundError: [Errno2] No such file or directory: '~'
        os.makedirs(path)

    with open(filename, 'w', encoding='utf-8') as f:
        # indent=2 is not needed but makes the file human-readable
        json.dump(savings, f, indent=2)

def load_json(saving_list, filename):
    with open(filename, 'r') as f:
        load = json.load(f)

    savings = []

    for i in saving_list:
        savings.append(load[i])

    return tuple(savings)

def json_to_csv(filename, ckpt:tuple, endpoint, rw_column=False):
    ckpt_filename = {
        'readi' : filename + "-readi_checkpoint" + str(endpoint) + ".json", 
        'readd' : filename + "-readd_checkpoint" + str(endpoint) + ".json", 
        'read' : filename + "-read_checkpoint" + str(endpoint) + ".json", 
        'write' : filename + "-write_checkpoint" + str(endpoint) + ".json", 
        'rw_by_type' : filename + "-by-type_checkpoint" + str(endpoint) + ".json", 
        'overall_rank' : filename + "_checkpoint" + str(endpoint) + ".json"
    }

    saving_list1 = ['block_rank', 'ref_cnt']
    saving_list2 = ['read_block_rank', 'read_cnt', 'write_block_rank', 'write_cnt']
    saving_list3 = ['block_rank', 'read_cnt', 'write_cnt']

    ref_cnt_dict = {}
    for i in range(len(ckpt)):
        if ckpt[i] == 'rw_by_type':
            _, read_cnt, _, write_cnt = load_json(saving_list2, ckpt_filename[ckpt[i]])
            ref_cnt_dict['read_cnt'] = read_cnt
            ref_cnt_dict['write_cnt'] = write_cnt
        elif ckpt[i] == 'overall_rank':
            _, read_cnt, write_cnt = load_json(saving_list3, ckpt_filename[ckpt[i]])
            if not 'read_cnt' in ref_cnt_dict:
                ref_cnt_dict['read_cnt'] = read_cnt
            if not 'write_cnt' in ref_cnt_dict:
                ref_cnt_dict['write_cnt'] = write_cnt
            if rw_column:
                ref_cnt_dict['rw_cnt'] = np.array(read_cnt) + np.array(write_cnt)
        else:
            _, ref_cnt = load_json(saving_list1, ckpt_filename[ckpt[i]])
            ref_cnt_dict[ckpt[i]+'_cnt'] = ref_cnt
    lengths = [len(v) for v in ref_cnt_dict.values()]
    rows = max(lengths)

    df = pd.DataFrame(index=range(0,rows), columns=ref_cnt_dict.keys())
    for k, v in ref_cnt_dict.items():
        df[k] = pd.Series(v)
    df.to_csv(filename+'.csv')

    return df
