"""
MAZE GENERATOR & SOLVER - Main Application

A complete interactive maze generation and solving program using Pygame.
- Generation: Stack-based DFS "mouse" that eats walls
- Solving: Backtracking with red path and blue dead-end visualization
- Challenge: Extra walls (1 in 20) to create cycles

Compatible with Python 3.7+ and Pygame 2.0+
"""

import pygame
import random
import sys
from maze_data import make_walls
from maze_generator import MazeGenerator
from maze_solver import MazeSolver

# Colours
WHITE      = (255, 255, 255)
BLACK      = ( 26,  26,  26)
BG         = (244, 244, 242)
WALL_COL   = ( 26,  26,  26)
VISITED_LT = (100, 200, 150,  46)
MOUSE_COL  = ( 30, 158, 117, 128)
PATH_RED   = (226,  75,  74,  90)
DEAD_BLUE  = ( 55, 138, 221,  77)
SOL_GREEN  = ( 29, 158, 117, 115)
MARKER_YLW = (240, 196,  25)
PANEL_BG   = (255, 255, 255)
BTN_BORDER = (180, 180, 180)
BTN_HOVER  = (230, 230, 228)
TEXT_GREY  = (100, 100, 100)

# Layout constants 
PANEL_W      = 720
PANEL_MARGIN = 20
BTN_H        = 34
STATUS_H     = 24
LEGEND_H     = 24
PADDING      = 14

pygame.init()
FONT_SM  = pygame.font.SysFont("Segoe UI", 13)
FONT_MED = pygame.font.SysFont("Segoe UI", 14, bold=True)
FONT_TTL = pygame.font.SysFont("Segoe UI", 20, bold=True)

# Speed map (steps per frame) - slower for better visualization
SPEED_MAP = [1, 2, 3, 5, 8]


class Slider:
    """UI Slider widget for adjusting numeric values."""
    def __init__(self, label, x, y, w, min_v, max_v, value):
        self.label = label
        self.rect = pygame.Rect(x, y, w, 16)
        self.min_v = min_v
        self.max_v = max_v
        self.value = value
        self.dragging = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rx = max(self.rect.x, min(event.pos[0], self.rect.right))
            t = (rx - self.rect.x) / self.rect.w
            self.value = round(self.min_v + t * (self.max_v - self.min_v))

    def draw(self, surf):
        lbl = FONT_SM.render(f"{self.label}: {self.value}", True, BLACK)
        surf.blit(lbl, (self.rect.x, self.rect.y - 18))
        pygame.draw.rect(surf, WHITE, self.rect, border_radius=4)
        t = (self.value - self.min_v) / (self.max_v - self.min_v)
        tx = self.rect.x + int(t * self.rect.w)
        if tx > self.rect.x:
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, tx - self.rect.x, self.rect.h)
            pygame.draw.rect(surf, (0, 122, 255), fill_rect, border_radius=4)
        pygame.draw.rect(surf, BLACK, self.rect, width=1, border_radius=4)
        pygame.draw.circle(surf, BLACK, (tx, self.rect.centery), 7, 1)
        pygame.draw.circle(surf, (0, 122, 255), (tx, self.rect.centery), 6)


class Button:
    """UI Button widget."""
    def __init__(self, label, x, y, w, h):
        self.label = label
        self.rect = pygame.Rect(x, y, w, h)
        self.disabled = False
        self.hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos) and not self.disabled
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.disabled and self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, surf):
        col = BTN_HOVER if (self.hovered and not self.disabled) else WHITE
        pygame.draw.rect(surf, col, self.rect, border_radius=8)
        pygame.draw.rect(surf, BTN_BORDER, self.rect, width=1, border_radius=8)
        alpha = 255 if not self.disabled else 100
        lbl = FONT_SM.render(self.label, True, BLACK if alpha == 255 else (*BLACK, alpha))
        surf.blit(lbl, lbl.get_rect(center=self.rect.center))


class Checkbox:
    """UI Checkbox widget."""
    def __init__(self, label, x, y, checked=False):
        self.label = label
        self.x, self.y = x, y
        self.checked = checked
        self.box = pygame.Rect(x, y, 16, 16)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.box.collidepoint(event.pos):
                self.checked = not self.checked

    def draw(self, surf):
        pygame.draw.rect(surf, WHITE, self.box, border_radius=3)
        pygame.draw.rect(surf, BTN_BORDER, self.box, width=1, border_radius=3)
        if self.checked:
            pygame.draw.line(surf, BLACK, (self.box.x+3, self.box.centery),
                             (self.box.centerx-1, self.box.bottom-4), 2)
            pygame.draw.line(surf, BLACK, (self.box.centerx-1, self.box.bottom-4),
                             (self.box.right-3, self.box.y+3), 2)
        lbl = FONT_SM.render(self.label, True, BLACK)
        surf.blit(lbl, (self.box.right + 6, self.box.y + 1))


class MazeApp:
    """Main application integrating generation and solving."""
    
    def __init__(self):
        self.screen = None
        self.clock = pygame.time.Clock()

        # UI widgets
        self.sl_rows = Slider("Rows", 0, 0, 100, 5, 25, 12)
        self.sl_cols = Slider("Cols", 0, 0, 100, 5, 35, 18)
        self.sl_speed = Slider("Speed", 0, 0, 100, 1, 5, 3)
        self.chk_cycle = Checkbox("Extra walls (1 in 20)", 0, 0, False)
        self.btn_gen = Button("Generate maze", 0, 0, 140, BTN_H)
        self.btn_solve = Button("Solve maze", 0, 0, 110, BTN_H)
        self.btn_reset = Button("Reset", 0, 0, 90, BTN_H)
        
        self.btn_solve.disabled = True
        self.btn_reset.disabled = True

        self.status = 'Press "Generate maze" to begin.'
        self.phase = 'idle'   

        # Maze state
        self.R = self.C = 0
        self.CELL = 24
        self.northWall = self.eastWall = None
        self.generator = None
        self.solver = None
        self.startR = self.startC = None
        self.endR = self.endC = None

        self._layout()

    def _layout(self):
        """Compute all pixel positions based on current R/C."""
        R = self.sl_rows.value
        C = self.sl_cols.value
        max_w = min(680, PANEL_W - 2 * PANEL_MARGIN)
        cell = max(14, min(32, max_w // C))
        maze_w = C * cell + 1
        maze_h = R * cell + 1
        panel_w = max(PANEL_W, maze_w + 2 * PANEL_MARGIN)
        panel_h = (PADDING + 20 + PADDING + PADDING + BTN_H + 
                   PADDING + STATUS_H + maze_h + PADDING + LEGEND_H + PADDING)

        win_w = panel_w + 2 * PANEL_MARGIN
        win_h = 60 + panel_h + 20

        if self.screen is None or self.screen.get_size() != (win_w, win_h):
            self.screen = pygame.display.set_mode((win_w, win_h))
            pygame.display.set_caption("Maze Generator & Solver")

        self.CELL = cell
        self.R = R
        self.C = C

        px = PANEL_MARGIN
        py = 60
        self.panel_rect = pygame.Rect(px, py, panel_w, panel_h)

        sy = py + PADDING + 18
        self.sl_rows.rect = pygame.Rect(px + PADDING + 40, sy, 90, 16)
        self.sl_cols.rect = pygame.Rect(px + PADDING + 40 + 150, sy, 90, 16)
        self.sl_speed.rect = pygame.Rect(px + PADDING + 40 + 300, sy, 90, 16)
        for sl in (self.sl_rows, self.sl_cols, self.sl_speed):
            sl.rect.y = sy
        self.chk_cycle.box = pygame.Rect(px + PADDING + 40 + 430, sy, 16, 16)
        self.chk_cycle.x = self.chk_cycle.box.x
        self.chk_cycle.y = self.chk_cycle.box.y

        by = sy + 20 + PADDING
        bx = px + PANEL_MARGIN
        for btn in (self.btn_gen, self.btn_solve, self.btn_reset):
            btn.rect.topleft = (bx, by)
            bx += btn.rect.w + 10

        self.status_y = by + BTN_H + PADDING // 2

        canvas_x = px + (panel_w - maze_w) // 2
        canvas_y = self.status_y + STATUS_H + 4
        self.canvas_rect = pygame.Rect(canvas_x, canvas_y, maze_w, maze_h)
        self.legend_y = canvas_y + maze_h + PADDING

    def _draw_maze(self, highlights=None):
        """Draw maze walls and optional cell highlights."""
        surf = self.screen
        cr = self.canvas_rect
        cell = self.CELL

        pygame.draw.rect(surf, WHITE, cr)

        if highlights:
            ov = pygame.Surface((cr.w, cr.h), pygame.SRCALPHA)
            for r, c, col in highlights:
                ov.fill(col, (c * cell + 2, r * cell + 2, cell - 3, cell - 3))
            surf.blit(ov, cr.topleft)

        nw = self.northWall
        ew = self.eastWall
        R, C = self.R, self.C
        ox, oy = cr.x, cr.y

        # Draw north walls (horizontal)
        for r in range(R + 1):
            for c in range(C):
                if nw[r][c]:
                    pygame.draw.line(surf, WALL_COL,
                                     (ox + c * cell, oy + r * cell),
                                     (ox + (c + 1) * cell, oy + r * cell), 2)
        
        # Draw east walls (vertical)
        for r in range(R):
            for c in range(C + 1):
                if ew[r][c]:
                    pygame.draw.line(surf, WALL_COL,
                                     (ox + c * cell, oy + r * cell),
                                     (ox + c * cell, oy + (r + 1) * cell), 2)

        pygame.draw.rect(surf, WALL_COL, cr, 1)

        # Draw start/end markers
        if self.startR is not None:
            sz = max(5, cell * 0.35)
            for mr, mc in ((self.startR, self.startC), (self.endR, self.endC)):
                pygame.draw.circle(surf, MARKER_YLW,
                                   (ox + mc * cell + cell // 2,
                                    oy + mr * cell + cell // 2), int(sz))

    def _draw_ui(self):
        """Draw all UI elements."""
        surf = self.screen
        W, H = surf.get_size()
        surf.fill(BG)

        ttl = FONT_TTL.render("Maze Generator & Solver", True, BLACK)
        surf.blit(ttl, ttl.get_rect(centerx=W // 2, y=16))

        pygame.draw.rect(surf, WHITE, self.panel_rect, border_radius=12)
        pygame.draw.rect(surf, (220, 220, 215), self.panel_rect, width=1, border_radius=12)

        for sl in (self.sl_rows, self.sl_cols, self.sl_speed):
            sl.draw(surf)

        self.chk_cycle.draw(surf)

        for btn in (self.btn_gen, self.btn_solve, self.btn_reset):
            btn.draw(surf)

        st = FONT_SM.render(self.status, True, TEXT_GREY)
        surf.blit(st, st.get_rect(centerx=self.panel_rect.centerx, y=self.status_y))

        self._draw_maze(self._current_highlights())

        legend_items = [
            ((226, 75, 74), "Current path"),
            ((55, 138, 221), "Dead end"),
            ((29, 158, 117), "Solution"),
            ((240, 196, 25), "Start / End"),
        ]
        lx = self.panel_rect.x + 20
        ly = self.legend_y
        for col, label in legend_items:
            pygame.draw.circle(surf, col, (lx + 5, ly + 8), 5)
            lbl = FONT_SM.render(label, True, TEXT_GREY)
            surf.blit(lbl, (lx + 14, ly))
            lx += lbl.get_width() + 30

    def _current_highlights(self):
        """Get highlight list for current phase."""
        hi = []
        
        if self.phase == 'gen' and self.generator:
            visited, current = self.generator.get_progress()
            for r in range(self.R):
                for c in range(self.C):
                    if visited[r][c]:
                        hi.append((r, c, VISITED_LT))
            if current:
                hi.append((current[0], current[1], MOUSE_COL))
                
        elif self.phase == 'solve' and self.solver:
            path, current, _ = self.solver.get_progress()
            for r in range(self.R):
                for c in range(self.C):
                    if path[r][c] == 2:
                        hi.append((r, c, PATH_RED))
                    elif path[r][c] == 3:
                        hi.append((r, c, DEAD_BLUE))
            if current:
                hi.append((current[0], current[1], (226, 75, 74, 178)))
                
        elif self.phase == 'solved' and self.solver:
            path, _, solution = self.solver.get_progress()
            for r in range(self.R):
                for c in range(self.C):
                    if path[r][c] == 2:
                        hi.append((r, c, SOL_GREEN))
            if solution:
                for r, c in solution:
                    hi.append((r, c, SOL_GREEN))
                    
        return hi

    def _start_generate(self):
        """Start maze generation."""
        self._layout()
        
        self.northWall, self.eastWall = make_walls(self.R, self.C)
        self.generator = MazeGenerator(self.R, self.C, self.northWall, self.eastWall)
        
        extras = self.chk_cycle.checked
        self.generator.start(extras=extras)
        
        # Start and end on left/right edges
        self.startR = random.randrange(self.R)
        self.startC = 0
        self.endR = random.randrange(self.R)
        self.endC = self.C - 1
        
        self.phase = 'gen'
        self.status = 'Generating maze... (mouse eating walls)'
        self.btn_solve.disabled = True
        self.btn_reset.disabled = False

    def _start_solve(self):
        """Start maze solving."""
        if self.phase != 'done-gen' or not self.northWall:
            return
            
        self.solver = MazeSolver(self.R, self.C, self.northWall, self.eastWall)
        self.solver.start(self.startR, self.startC, self.endR, self.endC)
        
        self.phase = 'solve'
        self.status = 'Solving maze... (red path, blue dead ends)'
        self.btn_solve.disabled = True

    def _reset(self):
        """Reset to initial state."""
        self.phase = 'idle'
        self.status = 'Press "Generate maze" to begin.'
        self.northWall = None
        self.eastWall = None
        self.generator = None
        self.solver = None
        self.btn_solve.disabled = True
        self.btn_reset.disabled = True

    def run(self):
        """Main application loop."""
        self._layout()
        self.northWall = [[0] * (self.C + 1) for _ in range(self.R + 1)]
        self.eastWall = [[0] * (self.C + 1) for _ in range(self.R + 1)]

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                for sl in (self.sl_rows, self.sl_cols, self.sl_speed):
                    sl.handle_event(event)

                self.chk_cycle.handle_event(event)

                if self.btn_gen.handle_event(event):
                    self._start_generate()
                if self.btn_solve.handle_event(event):
                    self._start_solve()
                if self.btn_reset.handle_event(event):
                    self._reset()

            if self.phase == 'gen' and self.generator:
                for _ in range(SPEED_MAP[self.sl_speed.value - 1]):
                    if self.generator.is_complete():
                        self.phase = 'done-gen'
                        self.status = 'Maze generated! Press "Solve maze" to find the path.'
                        self.btn_solve.disabled = False
                        break
                    self.generator.step()
                    
            elif self.phase == 'solve' and self.solver:
                for _ in range(SPEED_MAP[self.sl_speed.value - 1]):
                    if self.solver.is_complete():
                        if self.solver.is_solved():
                            self.phase = 'solved'
                            self.status = f'Solved! Path found.'
                        else:
                            self.phase = 'done-gen'
                            self.status = 'No solution found.'
                        break
                    self.solver.step()

            self._draw_ui()
            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    app = MazeApp()
    app.run()