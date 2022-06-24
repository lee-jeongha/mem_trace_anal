class FreqNode(object):
    def __init__(self, freq, ref_block, pre, nxt):
        self.freq = freq
        self.ref_block = ref_block
        self.pre = pre  # previous FreqNode
        self.nxt = nxt  # next FreqNode

    def count_blocks(self):
        return len(self.ref_block)

    def remove(self):
        if self.pre is not None:
            self.pre.nxt = self.nxt
        if self.nxt is not None:
            self.nxt.pre = self.pre

        pre = self.pre
        nxt = self.nxt
        self.pre = self.nxt = None

        return (pre, nxt)

    def remove_block(self, ref_address): # remove ref_address from ref_block within freq_node
        ref_block_list = self.ref_block
        
        ref_address_idx = ref_block_list.index(ref_address)
        _ = ref_block_list.pop(ref_address_idx)

        self.ref_block = ref_block_list

        return ref_address_idx

    def insert_ref_block(self, ref_address):
        self.ref_block.insert(0, ref_address)

    def append_ref_block(self, ref_address):
        self.ref_block.append(ref_address)

    def insert_after_me(self, freq_node):
        freq_node.pre = self
        freq_node.nxt = self.nxt

        if self.nxt is not None:
            self.nxt.pre = freq_node
        else:
            self.nxt = None

        self.nxt = freq_node

    def insert_before_me(self, freq_node):
        if self.pre is not None:
            self.pre.nxt = freq_node

        freq_node.pre = self.pre
        freq_node.nxt = self
        self.pre = freq_node


class LFUCache(object):

    def __init__(self):
        self.cache = {}  # {addr: freq_node}
        self.freq_link_head = None

    def reference(self, ref_address):
        if ref_address in self.cache:
            freq = self.cache[i]
            new_freq = self.move_next_to(i, freq)
            rank = self.get_freqs_rank(new_freq)

            self.cache[i] = new_freq

            return rank
        
        else:
            freq = self.create_freq_node(i)
            self.cache[i] = freq
            
            return -1

    def move_next_to(self, ref_address, freq_node): # for each access
        if freq_node.nxt is None or freq_node.nxt.freq != freq_node.freq + 1:
            target_freq_node = FreqNode(freq_node.freq + 1, list(), None, None)
            target_empty = True
        
        else:
            target_freq_node = freq_node.nxt
            target_empty = False

        target_freq_node.insert_ref_block(ref_address)

        if target_empty:
            freq_node.insert_after_me(target_freq_node)

        _ = freq_node.remove_block(ref_address)

        if freq_node.count_blocks() == 0: # if there is nothing left in freq_node
            if self.freq_link_head == freq_node:
                self.freq_link_head = target_freq_node

            freq_node.remove()
        
        return target_freq_node

    def create_freq_node(self, ref_address):
        ref_block = [ref_address]

        if self.freq_link_head is None or self.freq_link_head.freq != 1:
            new_freq_node = FreqNode(1, ref_block, None, None)
            self.cache[ref_address] = new_freq_node

            if self.freq_link_head is not None: # LFU has freq_link_head but frequency is not 1
                self.freq_link_head.insert_before_me(new_freq_node)

            self.freq_link_head = new_freq_node
            
            return new_freq_node

        else: # if LFU has freq_link_head which frequency value is 1
            self.freq_link_head.append_ref_block(ref_address)
        
            return self.freq_link_head
    
    def get_freqs_rank(self, freq_node):
        
        current_freq_node = freq_node.nxt
        rank = 1

        while current_freq_node != None:
            rank += current_freq_node.count_blocks()
            current_freq_node = current_freq_node.nxt

        return rank

lfu = LFUCache()

address = [2,3,1,2,3,2,2,2,2,3,2,7,7,3,7,7,1]
for i in address:
    rank = lfu.reference(i)
    print(i, lfu.cache[i].freq, rank)
