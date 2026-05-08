"""
maze_solver.py - Maze Solving Module

Backtracking Algorithm with Visual Feedback:
- path[r][c] == 0: Unvisited
- path[r][c] == 2: Current path (red dot)
- path[r][c] == 3: Dead end (blue dot)

The mouse moves randomly through open passages. When it hits a dead end,
it backtracks and marks the dead cell blue to avoid re-trying it.
"""

import random
from maze_data import can_pass, DIRS


class MazeSolver:
    """Handles backtracking maze solving with red/blue visualization."""
    
    def __init__(self, R, C, northWall, eastWall):
        """
        Initialize solver with maze dimensions and walls.
        
        Args:
            R, C: Maze dimensions
            northWall, eastWall: Wall arrays for passability checks
        """
        self.R = R
        self.C = C
        self.northWall = northWall
        self.eastWall = eastWall
        self.path = None
        self.stack = None
        self.start_r = None
        self.start_c = None
        self.end_r = None
        self.end_c = None
        self.solved = False
        
    def start(self, start_r, start_c, end_r, end_c):
        """
        Begin solving from start to end.
        
        Args:
            start_r, start_c: Starting position (typically left edge)
            end_r, end_c: Goal position (typically right edge)
        """
        self.start_r = start_r
        self.start_c = start_c
        self.end_r = end_r
        self.end_c = end_c
        
        # Initialize path: 0 = unvisited, 2 = current, 3 = dead end
        self.path = [[0] * self.C for _ in range(self.R)]
        self.path[start_r][start_c] = 2
        self.stack = [(start_r, start_c)]
        self.solved = False
        
    def step(self):
        """
        Perform one step of solving.
        
        Returns:
            tuple: (r, c) of current mouse position, or None if solving complete
        """
        if not self.stack or self.solved:
            return None
            
        r, c = self.stack[-1]
        
        # Check if we reached the end
        if r == self.end_r and c == self.end_c:
            self.solved = True
            return (r, c)
        
        # Get valid unvisited neighbors in random order
        neighbors = []
        for d, dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.R and 0 <= nc < self.C:
                if self.path[nr][nc] == 0:  # Unvisited
                    if can_pass(self.northWall, self.eastWall, r, c, d, self.R, self.C):
                        neighbors.append((nr, nc))
        
        random.shuffle(neighbors)
        
        if neighbors:
            # Move to neighbor
            nr, nc = neighbors[0]
            self.path[nr][nc] = 2  
            self.stack.append((nr, nc))
            return (nr, nc)
        else:
            # Dead end - mark as blue and backtrack
            self.path[r][c] = 3
            self.stack.pop()
            return (r, c) if self.stack else None
    
    def is_complete(self):
        """Return True if solving is finished."""
        return self.solved or not self.stack
    
    def is_solved(self):
        """Return True if path to end was found."""
        return self.solved
    
    def get_progress(self):
        """
        Get solving progress.
        
        Returns:
            path: 2D array (0=unvisited, 2=path, 3=dead)
            current: Current mouse position (or None)
            solution: Full solution path (if solved)
        """
        current = self.stack[-1] if self.stack else None
        solution = self.stack if self.solved else None
        return self.path, current, solution