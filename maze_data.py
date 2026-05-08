"""
maze_data.py - Maze Data Structures
northWall and eastWall arrays
These arrays represent the maze walls

Data Structure :
- northWall[R+1][C+1]: 1 = wall intact, 0 = passage (eaten)
  - Row 0 is a phantom row: northWall[0][c] represents the TOP edge
  - Row R (last row): northWall[R][c] represents the BOTTOM edge
  
- eastWall[R+1][C+1]: 1 = wall intact, 0 = passage (eaten)
  - Column 0 is a phantom column: eastWall[r][0] represents LEFT edge
  - Column C (last col): eastWall[r][C] represents RIGHT edge
"""

def make_walls(R, C):
    """
    Create initial walls for a maze of size R x C.
    
    Returns:
        northWall: R+1 x C+1 array, all walls intact (1)
        eastWall:  R+1 x C+1 array, all walls intact (1)
    """
    northWall = [[1] * (C + 1) for _ in range(R + 1)]
    eastWall  = [[1] * (C + 1) for _ in range(R + 1)]
    return northWall, eastWall


def eat_wall(northWall, eastWall, r, c, direction):
    """
    Remove the wall between cell (r,c) and its neighbor.
    
    Direction mapping:
        'N' (North): remove northWall[r][c] (wall above current cell)
        'S' (South): remove northWall[r+1][c] (wall below current cell)
        'W' (West):  remove eastWall[r][c-1] (left neighbor's east wall)
        'E' (East):  remove eastWall[r][c] (current cell's east wall)
    """
    if direction == 'N':
        northWall[r][c] = 0
    elif direction == 'S':
        northWall[r + 1][c] = 0
    elif direction == 'W':
        eastWall[r][c - 1] = 0
    elif direction == 'E':
        eastWall[r][c] = 0


def can_pass(northWall, eastWall, r, c, direction, R, C):
    """
    Check if movement from (r,c) in 'direction' is possible.
    
    Returns True if there is no wall blocking movement.
    """
    if direction == 'N':
        return r > 0 and northWall[r][c] == 0
    elif direction == 'S':
        return r < R - 1 and northWall[r + 1][c] == 0
    elif direction == 'W':
        return c > 0 and eastWall[r][c - 1] == 0
    elif direction == 'E':
        return c < C - 1 and eastWall[r][c] == 0
    return False


# Direction constants: (name, delta_row, delta_col)
DIRS = [('N', -1, 0), ('S', 1, 0), ('W', 0, -1), ('E', 0, 1)]