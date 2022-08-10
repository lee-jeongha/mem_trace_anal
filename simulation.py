def simulation(df, block_rank, readcnt, writecnt):
    for index, row in df.iterrows():  ### one by one
        ### Increase readcnt/writecnt by matching 'type' and block_rank
        acc_rank = block_rank.reference(row['blockaddress'])
        if acc_rank == -1:
            continue
        else:
            if (row['type'] == 'readi' or row['type'] == 'readd'):  ### if the 'type' is 'read'
                try:
                    readcnt[acc_rank] += 1  # Increase [acc_rank]th element of readcnt by 1
                except IndexError:  # ***list index out of range
                    for i in range(len(readcnt), acc_rank + 1):
                        readcnt.insert(i, 0)
                    readcnt[acc_rank] += 1

            else:   ### if the 'type' is 'write'
                try:
                    writecnt[acc_rank] += 1 # Increase [acc_rank]th element of writecnt by 1
                except IndexError:
                    for i in range(len(writecnt), acc_rank + 1):
                        writecnt.insert(i, 0)
                    writecnt[acc_rank] += 1

    return block_rank, readcnt, writecnt