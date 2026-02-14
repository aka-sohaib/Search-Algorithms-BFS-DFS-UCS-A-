"""
data_structures.py — Custom data structures used by the pathfinding algorithms.

Contains:
    - Stack    (LIFO — used by DFS)
    - Queue    (FIFO — used by BFS)
    - MinHeap  (Priority Queue — used by UCS)
"""


# ═══════════════════════════════════════════════════════════════════════════════
#  Stack — Last In, First Out (LIFO) — used by DFS
# ═══════════════════════════════════════════════════════════════════════════════

class stack:
    def __init__(self, size):
        self.nodes = [None]*size
        self.head=0

    def push(self, cell):
        self.nodes[self.head]=cell
        self.head += 1

    def pop(self):
        self.head -= 1
        tempCell = self.nodes[self.head]
        return tempCell
    def isEmpty(self):
        if(self.head==0):
            return True
        else:
            return False


# ═══════════════════════════════════════════════════════════════════════════════
#  Queue — First In, First Out (FIFO) — used by BFS
# ═══════════════════════════════════════════════════════════════════════════════

class queue:
    def __init__(self, size):
        self.nodes = [None]*size
        self.head=0
        self.tail=0

    def enqueue(self, cell):
        self.nodes[self.tail]=cell
        self.tail += 1

    def dequeue(self):
        tempCell = self.nodes[self.head]
        self.head += 1
        return tempCell
    def isEmpty(self):
        if(self.head==self.tail):
            return True
        else:
            return False


# ═══════════════════════════════════════════════════════════════════════════════
#  MinHeap (Priority Queue) — used by UCS
# ═══════════════════════════════════════════════════════════════════════════════

class MinHeap:
    def __init__(self, size, cols, rows):
        self.heap = [None]*size
        self.pos = [-1]*size
        self.cost = [float('inf')]*size

        self.size = 0

        self.cols = cols
        self.rows = rows

    def enqueue(self, row_number, col_number, cost):
        linear_index = self.pack(row_number, col_number)
        self.heap[self.size] = linear_index
        self.cost[self.size] = cost
        self.pos[linear_index] = self.size

        self.bubble_up(self.size)
        self.size += 1

    def pack(self, row_number, col_number):
        linear_index = (row_number*self.cols)+ col_number
        return linear_index

    def bubble_up(self, ind):
        curr_index = ind
        parent_index = (curr_index-1)//2

        while(curr_index != 0):
            if(self.cost[curr_index] < self.cost[parent_index]):

                self.pos[self.heap[curr_index]], self.pos[self.heap[parent_index]] = self.pos[self.heap[parent_index]], self.pos[self.heap[curr_index]]

                self.heap[curr_index], self.heap[parent_index] = self.heap[parent_index], self.heap[curr_index]

                self.cost[curr_index], self.cost[parent_index] = self.cost[parent_index], self.cost[curr_index]
            else:
                break

            curr_index= parent_index
            parent_index = (parent_index-1)//2

    def unpack(self, index):
            col_num = index%self.cols
            row_num = index//self.cols
            return row_num, col_num
    
    def dequeue(self):
        temp_heap_val = self.heap[0]
        temp_cost_val = self.cost[0]

        self.pos[self.heap[self.size-1]] = 0
        self.pos[temp_heap_val] = -1

        self.heap[0] = self.heap[self.size-1]
        self.cost[0] = self.cost[self.size-1]

        self.size -= 1
        self.bubble_down()
        row_number, col_number = self.unpack(temp_heap_val)

        return row_number, col_number, temp_cost_val

    def bubble_down(self):
        curr_index = 0
        left_child_ind = curr_index*2+1
        right_child_ind = curr_index*2+2

        while left_child_ind < self.size:
            smaller_index = curr_index
            if self.cost[smaller_index] > self.cost[left_child_ind]:
                smaller_index = left_child_ind
            if right_child_ind < self.size and self.cost[smaller_index] > self.cost[right_child_ind]:
                smaller_index = right_child_ind

            if smaller_index != curr_index:
                self.pos[self.heap[smaller_index]], self.pos[self.heap[curr_index]] = self.pos[self.heap[curr_index]], self.pos[self.heap[smaller_index]]

                self.heap[curr_index], self.heap[smaller_index] = self.heap[smaller_index], self.heap[curr_index]

                self.cost[curr_index], self.cost[smaller_index] = self.cost[smaller_index], self.cost[curr_index]

            else:
                break

            curr_index = smaller_index
            left_child_ind = curr_index*2+1
            right_child_ind = curr_index*2+2

    def decrease_key(self, r_ind, c_ind, new_cost):
        linear_index = self.pack(r_ind, c_ind)

        if self.pos[linear_index]==-1 or self.cost[self.pos[linear_index]] < new_cost:
            return False
        else:
            self.cost[self.pos[linear_index]] = new_cost
            self.bubble_up(self.pos[linear_index])
            return True
    
    def is_empty(self):
        if self.size == 0: return True
        else: return False
