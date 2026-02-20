"""
algorithms.py -- Pathfinding algorithms for the Fire Brigade Visualizer.

Contains:
    - BFS  (Breadth-First Search)
    - DFS  (Depth-First Search)
    - UCS  (Uniform-Cost Search)
    - A*   (Manhatten & Euclidean)
"""
import math
from algorithms.cells import cell, WightedCell, UniformWeightedCell
from data_structures.data_structures import queue, stack, MinHeap


# ===============================================================================
#  BFS -- Breadth-First Search
# ===============================================================================

def bfs(logic_grid, start_pos, goal_pos):
    rows = len(logic_grid)
    cols = len(logic_grid[0])
    
    #1. setup the working grid having parent's history and visited history
    work_grid = [[cell() for _ in range(cols)] for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            if(logic_grid[i][j]==1):
                work_grid[i][j].is_Blocked = True
    start_r, start_c = start_pos
    work_grid[start_r][start_c].Visited = True
    
    #2. initialize queue with max size 
    Q = queue(rows*cols)

    #3. tracking list history for animations
    visited_history = [None for _ in range(cols*rows)]
    visited_history[0] = start_pos
    visitedCellsCount = 1

    #4. setup starting point  and Queue with start pos
    curr_r, curr_c = start_pos
    Q.enqueue((curr_r, curr_c))

    #5. ------------- Main loop ----------------
    while not Q.isEmpty():
        curr_r, curr_c = Q.dequeue()
        
        #a. early exit if goal reached
        if (curr_r, curr_c) == goal_pos:
            break

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        #b. check all directions tuples
        for dr, dc in directions:
            next_r = curr_r + dr
            next_c = curr_c + dc

            #c. Boundry check
            if 0 <= next_r < rows and 0 <= next_c < cols:
                neighbour = work_grid[next_r][next_c]

                #d. Validity check
                if not neighbour.is_Blocked and not neighbour.Visited:
                    neighbour.Visited = True
                    neighbour.setParent((curr_r, curr_c))
                    Q.enqueue((next_r, next_c))
                    
                    #update the history for animations
                    visited_history[visitedCellsCount] = (next_r, next_c)
                    visitedCellsCount += 1

    #6. reconstruct final path
    if((curr_r, curr_c)==goal_pos):
        final_path = [None for _ in range(visitedCellsCount)]
        path_index =0

        path_r=curr_r
        path_c=curr_c
        
        while True:
            final_path[path_index] = (path_r, path_c)
            path_index += 1

            next_r = work_grid[path_r][path_c].parent_r
            next_c = work_grid[path_r][path_c].parent_c

            if next_r == -1 or next_c == -1:
                break
            
            path_r, path_c = next_r, next_c
    else:
        return False
    
    #7. polish visited & final array before returning
    final_history = visited_history[:visitedCellsCount]
    final_path = final_path[:path_index][::-1]
    
    return final_history, final_path


# ===============================================================================
#  DFS -- Depth-First Search
# ===============================================================================

def dfs(logic_grid, start_pos, goal_pos):
    rows = len(logic_grid)
    cols = len(logic_grid[0])

    #1. setup the working grid having parent's history and visited history
    work_grid = [[cell() for _ in range(cols)] for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            if(logic_grid[i][j]==1):
                work_grid[i][j].is_Blocked = True

    start_r, start_c = start_pos
    work_grid[start_r][start_c].Visited = True

    #2. initialize Stack with max size
    S = stack(rows*cols)

    #3. tracking list history for animations
    visited_history = [None for _ in range(cols*rows)]
    visited_history[0] = start_pos
    visitedCellsCount = 1

    #4. setup starting point  and Statck with start pos
    curr_r, curr_c = start_pos
    S.push((curr_r, curr_c))

    #5. ------------- Main loop ----------------
    while not S.isEmpty():
        curr_r,curr_c = S.pop()

        #a. early exit if goal reached
        if((curr_r,curr_c)==goal_pos):
            break

        directions= [(-1,0), (1, 0), (0,-1),(0, 1)]

        #b. check all directions tuples
        for dr, dc in directions:
            next_r = curr_r + dr
            next_c = curr_c + dc

            #c. Boundry check
            if 0<= next_r < rows and 0<= next_c < cols:
                neighbour = work_grid[next_r][next_c]

                #d. Validity check
                if not neighbour.is_Blocked and not neighbour.Visited:
                    neighbour.Visited = True
                    neighbour.setParent((curr_r, curr_c))
                    S.push((next_r, next_c))

                    #update the history for animations
                    visited_history[visitedCellsCount] = (next_r, next_c)
                    visitedCellsCount+=1

    #6. reconstruct final path
    if (curr_r, curr_c) == goal_pos:
        final_path = [None for _ in range(visitedCellsCount)]
        path_index = 0

        path_r = curr_r
        path_c = curr_c

        while True:
            final_path[path_index] = (path_r, path_c)
            path_index +=1

            next_r = work_grid[path_r][path_c].parent_r
            next_c = work_grid[path_r][path_c].parent_c

            if next_r == -1 or next_c == -1:
                break

            path_r, path_c = next_r, next_c
    else:
        return False
    
    #7. polish visited & final array before returning
    final_history = visited_history[: visitedCellsCount]
    final_path = final_path[: path_index][::-1]

    return final_history, final_path


# ===============================================================================
#  UCS -- Uniform-Cost Search
# ===============================================================================

def ucs(logic_grid, start_pos, goal_pos):
    rows = len(logic_grid)
    cols = len(logic_grid[0])

    #1. setting up the work grid
    work_grid = [[WightedCell() for _ in range(cols)] for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            if(logic_grid[i][j]["blocked"] == True):
                work_grid[i][j].isblocked = True
            if(logic_grid[i][j]["weight"] > 1):
                work_grid[i][j].weight = logic_grid[i][j]["weight"]

    #2. initialize priority queue
    PQ = MinHeap(rows*cols, cols, rows)

    #3. tracking list for animation order
    visited_history = [None for _ in range(cols*rows)]
    visited_history[0] = start_pos
    visited_cell_count =1

    #4. setup starting point in Priority queue
    curr_r, curr_c = start_pos
    PQ.enqueue(curr_r, curr_c, 0)

    #5. ------- Main Loop ---------
    while not PQ.is_empty():
        curr_r, curr_c, curr_w = PQ.dequeue()

        if(curr_r, curr_c) == goal_pos:
            break

        work_grid[curr_r][curr_c].isDequeued = True

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        #a. check all directions
        for dr, dc in directions:
            next_r = curr_r + dr
            next_c = curr_c + dc

            #b. bound check
            if 0<= next_r < rows and 0<= next_c<cols:
                next_d = curr_w + work_grid[next_r][next_c].weight
                neighbour = work_grid[next_r][next_c]
                
                #c. process if not blocked and not dequeued
                if not neighbour.isblocked and not neighbour.isDequeued:
                    #d. process if not visited
                    if not neighbour.visited:
                        neighbour.visited = True
                        neighbour.setParent((curr_r, curr_c))
                        neighbour.distance = next_d

                        PQ.enqueue(next_r, next_c, next_d)

                        visited_history[visited_cell_count] = (next_r, next_c)
                        visited_cell_count += 1

                    #e. decrease key if can
                    elif neighbour.visited:
                        if PQ.decrease_key(next_r, next_c, next_d):
                            neighbour.setParent((curr_r, curr_c))
                            neighbour.distance = next_d
    
    #6. reconstruct final path
    if((curr_r, curr_c)==goal_pos):
        final_path = [None for _ in range(visited_cell_count)]
        path_index =0

        path_r=curr_r
        path_c=curr_c
        
        while True:
            final_path[path_index] = (path_r, path_c)
            path_index += 1

            next_r = work_grid[path_r][path_c].parent_r
            next_c = work_grid[path_r][path_c].parent_c

            if next_r == -1 or next_c == -1:
                break
            
            path_r, path_c = next_r, next_c
    else:
        return False
    
    #7. polish visited & final array before returning
    final_history = visited_history[:visited_cell_count]
    final_path = final_path[:path_index][::-1]
    
    return final_history, final_path

# ===============================================================================
#  A* Manhatten OR Euclediedean
# ===============================================================================

#Manhattan distance
def get_h_manhattan(r, c, goalpos):
    gr, gc = goalpos
    return abs(r - gr) + abs(c - gc)

#eucliedean distance
def get_h_euclidean(r, c, goalpos):
    gr, gc = goalpos
    return math.sqrt((r - gr)**2 + (c - gc)**2)

def Astar(logic_grid, start_pos, goal_pos, is_euclidean):
    rows = len(logic_grid)
    cols = len(logic_grid[0])

    # select the heuristic function
    heuristic_func = get_h_euclidean if is_euclidean else get_h_manhattan

    #1. setting up the work grid
    work_grid = [[UniformWeightedCell() for _ in range(cols)] for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            if(logic_grid[i][j]["blocked"] == True):
                work_grid[i][j].isblocked = True

    #2. initialize priority queue
    PQ = MinHeap(rows*cols, cols, rows)

    #3. tracking list for animation order
    visited_history = [None for _ in range(cols*rows)]
    visited_history[0] = start_pos
    visited_cell_count =1

    #4. setup starting point in Priority queue
    curr_r, curr_c = start_pos
    PQ.enqueue(curr_r, curr_c, (heuristic_func(curr_r, curr_c, goal_pos), 0))

    #5. ------ MAIN LOOP --------
    while not PQ.is_empty():
        curr_r, curr_c, curr_w = PQ.dequeue()

        if (curr_r, curr_c) == goal_pos:
            break

        work_grid[curr_r][curr_c].isDequeued = True

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        #a. check all directions
        for dr, dc in directions:
            next_r = curr_r + dr
            next_c = curr_c + dc

            #b. calculate the next neighbour's f & g costs
            if 0<= next_r < rows and 0<= next_c<cols:
                curr_f, curr_g = curr_w 
                new_g = curr_g + work_grid[next_r][next_c].weight
                new_h = heuristic_func(next_r, next_c, goal_pos)
                new_f = new_g + new_h

                next_w = (new_f, -new_g)

                neighbour = work_grid[next_r][next_c]
                
                #c. process if not blocked and in Queue
                if not neighbour.isblocked and not neighbour.isDequeued:
                    #d. process if not visited
                    if not neighbour.visited:
                        neighbour.visited = True
                        neighbour.setParent((curr_r, curr_c))

                        PQ.enqueue(next_r, next_c, next_w)

                        visited_history[visited_cell_count] = (next_r, next_c)
                        visited_cell_count += 1

                    #e. decrease key if short dist found
                    elif neighbour.visited:
                        if PQ.decrease_key(next_r, next_c, next_w):
                            neighbour.setParent((curr_r, curr_c))
                            neighbour.distance = next_w
    
    #6. reconstruct final path
    if((curr_r, curr_c)==goal_pos):
        final_path = [None for _ in range(visited_cell_count)]
        path_index =0

        path_r=curr_r
        path_c=curr_c
        
        while True:
            final_path[path_index] = (path_r, path_c)
            path_index += 1

            next_r = work_grid[path_r][path_c].parent_r
            next_c = work_grid[path_r][path_c].parent_c

            if next_r == -1 or next_c == -1:
                break
            
            path_r, path_c = next_r, next_c
    else:
        return False
    
    #7. polish visited & final array before returning
    final_history = visited_history[:visited_cell_count]
    final_path = final_path[:path_index][::-1]
    
    return final_history, final_path
