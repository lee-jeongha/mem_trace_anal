def overall_rank_simulation(df, block_rank, read_cnt, write_cnt):
    for index, row in df.iterrows():  ### one by one
        ### Increase read_cnt/write_cnt by matching 'type' and block_rank
        acc_rank = block_rank.reference(row['blockaddress'])
        if acc_rank == -1:
            continue
        else:
            if (row['type'] == 'readi' or row['type'] == 'readd'):  ### if the 'type' is 'read'
                try:
                    read_cnt[acc_rank] += 1  # Increase [acc_rank]th element of read_cnt by 1
                except IndexError:  # ***list index out of range
                    for i in range(len(read_cnt), acc_rank + 1):
                        read_cnt.insert(i, 0)
                    read_cnt[acc_rank] += 1

            else:   ### if the 'type' is 'write'
                try:
                    write_cnt[acc_rank] += 1 # Increase [acc_rank]th element of write_cnt by 1
                except IndexError:
                    for i in range(len(write_cnt), acc_rank + 1):
                        write_cnt.insert(i, 0)
                    write_cnt[acc_rank] += 1

    return block_rank, read_cnt, write_cnt

def separately_rank_simulation(df, read_block_rank, read_cnt, write_block_rank, write_cnt):
    for index, row in df.iterrows():  ### one by one
        ### Increase read_cnt/write_cnt by matching 'type' and block_rank
        if (row['type'] == 'readi' or row['type'] == 'readd'):  ### if the 'type' is 'read'
            acc_rank = read_block_rank.reference(row['blockaddress'])
            if acc_rank == -1:
                continue
            try:
                read_cnt[acc_rank] += 1  # Increase [acc_rank]th element of read_cnt by 1
            except IndexError:  # ***list index out of range
                for i in range(len(read_cnt), acc_rank + 1):
                    read_cnt.insert(i, 0)
                read_cnt[acc_rank] += 1

        else:   ### if the 'type' is 'write'
            acc_rank = write_block_rank.reference(row['blockaddress'])
            if acc_rank == -1:
                continue
            try:
                write_cnt[acc_rank] += 1 # Increase [acc_rank]th element of write_cnt by 1
            except IndexError:
                for i in range(len(write_cnt), acc_rank + 1):
                    write_cnt.insert(i, 0)
                write_cnt[acc_rank] += 1

    return read_block_rank, read_cnt, write_block_rank, write_cnt
