"""
maze_gen.py - Maze Generation Module

Stack-based DFS "Mouse" Algorithm (Recursive Backtracker):
1. Start with all walls intact
2. Place "mouse" in random cell, mark visited
3. While unvisited cells remain:
   - Find unvisited neighbor in random order
   - Eat wall between current and neighbor
   - Move to neighbor, push to stack
   - If no unvisited neighbors, backtrack (pop stack)
"""

import random
from maze_data import eat_wall, DIRS


class MazeGenerator:
    """Handles the stack-based DFS maze generation."""
    
    def __init__(self, R, C, northWall, eastWall):
        """
        Initialize generator with maze dimensions and wall arrays.
        
        Args:
            R, C: Maze dimensions (rows, columns)
            northWall, eastWall: Wall arrays to modify
        """
        self.R = R
        self.C = C
        self.northWall = northWall
        self.eastWall = eastWall
        self.visited = None
        self.stack = None
        self.extras = False  # Whether to add extra walls (cycles)
        
    def start(self, start_r=None, start_c=None, extras=False):
        """
        Begin maze generation from a random or specified start cell.
        
        Args:
            start_r, start_c: Starting position (random if None)
            extras: If True, add cycles (1 in 20 chance per move)
        """
        # Initialize visited array
        self.visited = [[0] * self.C for _ in range(self.R)]
        self.extras = extras
        
        # Choose random start cell if not specified
        if start_r is None:
            start_r = random.randrange(self.R)
            start_c = random.randrange(self.C)
        
        # Mark start as visited and push to stack
        self.visited[start_r][start_c] = 1
        self.stack = [(start_r, start_c)]
        
    def step(self):
        """
        Perform one step of generation.
        
        Returns:
            tuple: (r, c) of current mouse position, or None if generation complete
        """
        if not self.stack:
            return None
            
        r, c = self.stack[-1]
        
        # Get unvisited neighbors in random order
        neighbors = []
        for d, dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.R and 0 <= nc < self.C:
                if not self.visited[nr][nc]:
                    neighbors.append((nr, nc, d))
        
        random.shuffle(neighbors)
        
        if neighbors:
            # Move to an unvisited neighbor
            nr, nc, d = neighbors[0]
            
            # Eat the connecting wall
            eat_wall(self.northWall, self.eastWall, r, c, d)
            
            # This creates cycles that defeat the shoulder-to-wall rule
            if self.extras and random.random() < 0.05:
                # Try to eat a different wall to create a cycle
                for d2, dr2, dc2 in DIRS:
                    if d2 != d:  
                        nr2, nc2 = r + dr2, c + dc2
                        if 0 <= nr2 < self.R and 0 <= nc2 < self.C:
                            eat_wall(self.northWall, self.eastWall, r, c, d2)
                            break
            
            # Move to new cell
            self.visited[nr][nc] = 1
            self.stack.append((nr, nc))
            return (nr, nc)
        else:
            # Dead end - backtrack
            self.stack.pop()
            return (r, c) if self.stack else None
    
    def is_complete(self):
        """Return True if generation is finished."""
        return not self.stack
    
    def get_progress(self):
        """
        Get generation progress.
        
        Returns:
            visited_cells: 2D array of visited status
            current_cell: Current mouse position (or None)
        """
        current = self.stack[-1] if self.stack else None
        return self.visited, current