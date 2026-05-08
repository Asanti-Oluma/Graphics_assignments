# DFS Maze Generator & Solver

A Python program that builds a random, proper maze using a stack‑based DFS (“mouse eating walls”) and then solves it with backtracking (red path, blue dead ends, final green solution).  
Made for a Computer Graphics assignment.

## Features

- Maze generation – DFS with stack, walls disappear as the mouse moves.
- Maze solving – backtracking, shows current path (red), dead ends (blue), and final solution (green).
- Interactive UI –  
  - Generate maze button – creates a maze with current settings  
  - Solve maze button – runs the solver on the generated maze  
  - Reset button – clears the maze and returns to idle  
  - Rows / Cols sliders (5–25 rows, 5–35 columns)  
  - Speed slider (1 = slowest, 5 = fastest – steps per frame)  
  - Extra walls checkbox – adds cycles (1 in 20 chance)  
  - Colour legend
- Proper maze – every cell is connected by a unique path (a spanning tree) – extra walls add cycles when enabled.

## Requirements

- Python 3.7+  
- Pygame – install with pip install pygame

## How to Run

1. Save all four files in the same folder:  
   maze.py, maze_data.py, maze_generator.py, maze_solver.py
2. Open a terminal in that folder.
3. Run:  
   python maze.py

The window will open. Press Generate maze to create a new maze, then Solve maze to watch the solver.

## How It Works

### Data Structures

- northWall[R+1][C+1] – 1 = wall intact, 0 = passage eaten  
  (Row 0 = top border, Row R = bottom border)
- eastWall[R+1][C+1] – 1 = wall intact, 0 = passage eaten  
  (Col 0 = left border, Col C = right border)

### Generation (Stack‑based DFS)

1. Start at a random cell, mark visited, push onto stack.
2. While stack not empty:  
   - Look at current cell.  
   - If there is an unvisited neighbour, choose one randomly, eat the wall between them, push neighbour onto stack.  
   - Else (dead end) – pop from stack (backtrack).
3. Repeat until all cells visited → perfect maze.
4. If Extra walls is checked: during each move, with 5% probability, eat an additional random wall to create cycles.

### Solving (Backtracking)

- Use a stack to remember the current path.  
- At each step, look for an unvisited neighbour with no wall.  
- If found → move there, push onto stack, mark red (current path).  
- If dead end → pop, mark cell blue (dead end, never revisited).  
- When the end cell (rightmost column) is reached, the solver stops and the entire stack is displayed as the green solution path.

## Controls

| Control | Action |
|---------|--------|
| Mouse click | Press any button, drag a slider, click the checkbox |
| Rows / Cols sliders | Change maze size (must regenerate to take effect) |
| Speed slider | Adjust animation speed (1 = 1 step/frame, 5 = 8 steps/frame) |
| Extra walls checkbox | Enable/disable cycle creation for next generation |
| Generate maze | Create a new maze with current settings |
| Solve maze | Run the solver on the current maze (only enabled after generation) |
| Reset | Clear the maze and solver, return to idle |

## Demo

[Click here to watch the full demo (Loom recording)](https://www.loom.com/share/8c6f30a597e64ee4af82f9b849b47d42)

## Author

Asanti Oluma – UGR/8165/16 – Computer Graphics Assignment  
