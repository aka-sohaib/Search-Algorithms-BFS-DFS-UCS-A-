"""
cells.py -- Grid cell representations used by the pathfinding algorithms.

Contains:
    - cell          (unweighted cell for BFS / DFS)
    - WightedCell   (weighted cell for UCS)
"""


# ===============================================================================
#  cell -- Unweighted grid cell used by BFS and DFS
# ===============================================================================

class cell:
    def __init__ (self):
        self.is_Blocked = False
        self.Visited = False
        
        self.parent_r = -1
        self.parent_c = -1
    
    def setParent(self,coordinates):
        self.parent_r, self.parent_c = coordinates


# ===============================================================================
#  WightedCell -- Weighted grid cell used by UCS
# ===============================================================================

class WightedCell:
    def __init__(self):
        self.isblocked = False
        self.visited = False
        self.isDequeued = False

        self.weight = 1

        self.parent_r = -1
        self.parent_c = -1

        self.distance = -1
        
    def setParent(self,coordinates):
        self.parent_r, self.parent_c = coordinates

# ===============================================================================
#  WightedCell -- Weighted grid cell used by A*
# ===============================================================================

class UniformWeightedCell:
    def __init__(self):
        self.isblocked = False
        self.visited = False
        self.isDequeued = False

        self.weight = 1

        self.parent_r = -1
        self.parent_c = -1
        
    def setParent(self,coordinates):
        self.parent_r, self.parent_c = coordinates
