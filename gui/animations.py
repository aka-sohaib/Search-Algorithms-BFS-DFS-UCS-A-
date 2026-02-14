"""
animations.py — Step-by-step animation engine for the grid canvas.

Manages three animation phases that run sequentially:
    1. Exploration  – lights up visited cells in the algorithm's colour.
    2. Path         – highlights the final shortest path from goal → start.
    3. Truck        – moves the fire-truck sprite cell-by-cell along the path.

Speed adapts automatically to grid size: the frame interval is fixed at ~60 fps
while the *batch size* (cells per frame) scales up for larger grids to keep the
total animation duration reasonable.
"""

from gui.constants import EXPLORE_COLORS, PATH_COLORS, TRUCK_STEP_MS, TRUCK_GRID_THRESHOLD

# Fixed frame interval — targets a smooth ~60 fps refresh rate
FRAME_MS = 16


class Animator:
    """Controls all canvas animations: exploration, path, truck, and fire effects."""

    def __init__(self, root, grid_canvas, asset_manager):
        """Initialise the animator.

        Args:
            root:          The Tk root window (used for `after` scheduling).
            grid_canvas:   The GridCanvas instance to animate on.
            asset_manager: The AssetManager for sprite lookups (truck directions).
        """
        self.root   = root
        self.grid   = grid_canvas
        self.assets = asset_manager

    # ═══════════════════════════════════════════════════════════
    #  ADAPTIVE SPEED CONTROL
    # ═══════════════════════════════════════════════════════════

    def _explore_batch(self, total_cells):
        """Return how many cells to colour per frame during the exploration phase.

        Larger grids need bigger batches so the animation doesn't take forever.
        """
        if   total_cells <= 50:   return 1
        elif total_cells <= 100:  return 2
        elif total_cells <= 200:  return 4
        elif total_cells <= 500:  return 8
        elif total_cells <= 1000: return 20
        elif total_cells <= 1500: return 35
        else:                     return max(50, total_cells // 40)

    def _path_batch(self, path_len):
        """Return how many path cells to highlight per frame."""
        if   path_len <= 20:  return 1
        elif path_len <= 50:  return 2
        elif path_len <= 100: return 3
        else:                 return max(4, path_len // 30)

    def _should_animate_truck(self):
        """Decide whether to animate the truck step-by-step.

        On grids larger than TRUCK_GRID_THRESHOLD the truck is teleported
        instantly to keep the total animation time practical.
        """
        return (self.grid.rows <= TRUCK_GRID_THRESHOLD
                and self.grid.cols <= TRUCK_GRID_THRESHOLD)

    # ═══════════════════════════════════════════════════════════
    #  EXPLORATION ANIMATION
    # ═══════════════════════════════════════════════════════════

    def animate_exploration(self, visited_history, final_path, algo, on_done):
        """Start the exploration animation.

        Args:
            visited_history: Ordered list of (row, col) cells the algorithm visited.
            final_path:      The shortest path (passed through to on_done).
            algo:            Algorithm name (selects overlay colour).
            on_done:         Callback invoked when exploration finishes.
        """
        color = EXPLORE_COLORS.get(algo, "#fab005")
        batch = self._explore_batch(len(visited_history))
        self._explore_step(visited_history, final_path, algo, color, 0, batch, on_done)

    def _explore_step(self, visited, path, algo, color, index, batch, on_done):
        """Recursive frame callback — colours the next batch of explored cells."""
        if index >= len(visited):
            on_done(path, algo)
            return

        end = min(index + batch, len(visited))
        for i in range(index, end):
            r, c = visited[i]
            # Skip start and goal cells to keep their sprites visible
            if (r, c) != self.grid.start_pos and (r, c) != self.grid.goal_pos:
                self.grid.set_overlay(r, c, color)

        self.root.after(FRAME_MS, lambda: self._explore_step(
            visited, path, algo, color, end, batch, on_done
        ))

    # ═══════════════════════════════════════════════════════════
    #  PATH ANIMATION (draws from goal → start for visual effect)
    # ═══════════════════════════════════════════════════════════

    def animate_path(self, final_path, algo, on_done):
        """Start the path-highlight animation.

        Draws the path in reverse (goal → start) so it appears to "trace back"
        from the fire to the truck.
        """
        color = PATH_COLORS.get(algo, "#15aabf")
        batch = self._path_batch(len(final_path))
        self._path_step(final_path, algo, color, len(final_path) - 1, batch, on_done)

    def _path_step(self, path, algo, color, index, batch, on_done):
        """Recursive frame callback — highlights the next batch of path cells."""
        if index < 0:
            on_done(path, algo)
            return

        end = max(index - batch, -1)
        for i in range(index, end, -1):
            r, c = path[i]
            if (r, c) != self.grid.start_pos and (r, c) != self.grid.goal_pos:
                self.grid.set_overlay(r, c, color)

        self.root.after(FRAME_MS, lambda: self._path_step(
            path, algo, color, end, batch, on_done
        ))

    # ═══════════════════════════════════════════════════════════
    #  TRUCK MOVEMENT ANIMATION
    # ═══════════════════════════════════════════════════════════

    def animate_truck(self, final_path, on_done):
        """Move the truck along the path, stopping one cell before the goal.

        The truck halts adjacent to the fire so it can "aim" the extinguisher.
        On large grids (> TRUCK_GRID_THRESHOLD) the truck is teleported instead.
        """
        truck_path = final_path[:-1] if len(final_path) > 1 else final_path

        if not self._should_animate_truck():
            self._jump_truck_to_goal(truck_path)
            on_done()
            return

        self._truck_step(truck_path, 0, on_done)

    def _jump_truck_to_goal(self, path):
        """Instantly reposition the truck to the last cell in *path* (skip animation)."""
        if not path:
            return

        r, c = path[-1]
        # Determine facing direction from the last two cells
        direction = "right"
        if len(path) > 1:
            prev_r, prev_c = path[-2]
            direction = self._get_direction(r - prev_r, c - prev_c)

        truck_img = self.assets.truck.get(direction)
        if truck_img and self.grid.truck_image_id:
            cx = c * self.grid.cell_size + self.grid.cell_size // 2
            cy = r * self.grid.cell_size + self.grid.cell_size // 2
            self.grid.canvas.coords(self.grid.truck_image_id, cx, cy)
            self.grid.canvas.itemconfig(self.grid.truck_image_id, image=truck_img)
            self.grid.canvas.tag_raise(self.grid.truck_image_id)

    def _truck_step(self, path, index, on_done):
        """Recursive frame callback — moves the truck one cell per TRUCK_STEP_MS."""
        if index >= len(path):
            on_done()
            return

        r, c = path[index]
        direction = self._get_direction(
            r - path[index - 1][0], c - path[index - 1][1]
        ) if index > 0 else "right"

        truck_img = self.assets.truck.get(direction)
        if truck_img and self.grid.truck_image_id:
            cx = c * self.grid.cell_size + self.grid.cell_size // 2
            cy = r * self.grid.cell_size + self.grid.cell_size // 2
            self.grid.canvas.coords(self.grid.truck_image_id, cx, cy)
            self.grid.canvas.itemconfig(self.grid.truck_image_id, image=truck_img)
            self.grid.canvas.tag_raise(self.grid.truck_image_id)

        self.root.after(TRUCK_STEP_MS, lambda: self._truck_step(path, index + 1, on_done))

    @staticmethod
    def _get_direction(dr, dc):
        """Map a row/col delta to a sprite direction name."""
        if dr == -1: return "Up"
        if dr ==  1: return "Down"
        if dc == -1: return "left"
        if dc ==  1: return "right"
        return "right"                 # Fallback

    # ═══════════════════════════════════════════════════════════
    #  FIRE DISPLAY & EXTINGUISH EFFECT
    # ═══════════════════════════════════════════════════════════

    def start_fire_cycle(self):
        """Ensure the fire sprite is visible on top of overlays."""
        if self.grid.goal_pos and self.grid.fire_image_id:
            self.grid.canvas.tag_raise(self.grid.fire_image_id)

    def stop_fire_cycle(self):
        """No-op — kept for API symmetry (single-frame fire has no cycling)."""
        pass

    def extinguish_fire(self, on_done):
        """Play a blink effect and then remove the fire sprite.

        Args:
            on_done: Callback invoked after the fire is fully removed.
        """
        self._extinguish_step(0, on_done)

    def _extinguish_step(self, count, on_done):
        """Recursive blink: toggles fire visibility 3 times, then deletes it."""
        if count >= 6:
            # Final removal
            if self.grid.fire_image_id is not None:
                self.grid.canvas.delete(self.grid.fire_image_id)
                self.grid.fire_image_id = None
            on_done()
            return

        # Alternate between hidden and visible for a blink effect
        if self.grid.fire_image_id:
            state = "hidden" if count % 2 == 1 else "normal"
            self.grid.canvas.itemconfig(self.grid.fire_image_id, state=state)

        self.root.after(120, lambda: self._extinguish_step(count + 1, on_done))
