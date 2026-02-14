"""
grid_canvas.py — Interactive city grid canvas.

Renders the NxN city grid using sprite tiles and handles all mouse interactions
for placing buildings (walls), the fire truck (start), the fire (goal), and
custom road types (UCS weighted roads).

Data structures (all row × col 2-D lists):
    logic_grid      – 0 = open road, 1 = wall (building)
    road_type_grid  – road type name per cell (e.g. "RoadPlain1", "RoadCrack")
    image_ids       – tkinter canvas item IDs for road sprites
    building_ids    – tkinter canvas item IDs for building sprites
    overlay_ids     – pre-created hidden rectangles used for exploration/path overlays
"""

import random
import customtkinter as ctk

from gui.constants import (
    CANVAS_BG, GRID_LINE,
    ROAD_TYPES, PLAIN_ROADS,
    MAX_CELL_SIZE, MIN_CELL_SIZE
)


class GridCanvas:
    """Manages the tkinter Canvas that displays the city grid with sprite tiles.

    The canvas is centred inside its parent container and auto-sizes cells to
    fill the available space. Overlays (for exploration and path colouring) are
    pre-created as hidden rectangles at grid-creation time so that animating
    them during algorithm playback only requires fast `itemconfig` calls.
    """

    def __init__(self, parent_frame, asset_manager, rows, cols, cell_size):
        """Create the grid canvas and draw the initial grid.

        Args:
            parent_frame:  The CTkFrame that will contain the canvas.
            asset_manager: AssetManager instance for sprite lookups.
            rows, cols:    Initial grid dimensions.
            cell_size:     Initial cell pixel size (recalculated on create_grid).
        """
        self.parent    = parent_frame
        self.assets    = asset_manager
        self.rows      = rows
        self.cols      = cols
        self.cell_size = cell_size

        # ── Per-cell data grids ──
        self.road_type_grid = [[None] * cols for _ in range(rows)]
        self.logic_grid     = [[0]    * cols for _ in range(rows)]
        self.building_ids   = [[None] * cols for _ in range(rows)]
        self.image_ids      = [[None] * cols for _ in range(rows)]
        self.overlay_ids    = [[None] * cols for _ in range(rows)]

        # ── Sprite IDs for movable elements ──
        self.truck_image_id = None       # Canvas ID for the fire-truck sprite
        self.fire_image_id  = None       # Canvas ID for the fire sprite

        # ── Interaction state ──
        self.start_pos  = None           # (row, col) of the fire truck
        self.goal_pos   = None           # (row, col) of the fire
        self.mode       = "Wall"         # Active interaction mode
        self.algo_mode  = "BFS"          # Determines road-type pool on reset
        self.drag_visited = set()        # Cells already affected during a drag

        # ── External callbacks (wired by app.py after construction) ──
        self.road_type_callback = None   # Returns the sidebar's selected road type
        self.sfx                = None   # SoundManager reference
        self.on_goal_placed     = None   # Called when fire is placed
        self.on_goal_removed    = None   # Called when fire is removed

        # ── Canvas widget ──
        self.canvas = None
        self.create_grid()

    # ═══════════════════════════════════════════════════════════
    #  GRID CREATION
    # ═══════════════════════════════════════════════════════════

    def _compute_cell_size(self):
        """Calculate cell pixel-size to fill the parent container optimally.

        Returns the computed cell size (clamped between MIN/MAX_CELL_SIZE).
        """
        self.parent.update_idletasks()
        available_w = self.parent.winfo_width()  - 20   # Small padding margin
        available_h = self.parent.winfo_height() - 20

        size_by_w = available_w // self.cols if self.cols > 0 else MAX_CELL_SIZE
        size_by_h = available_h // self.rows if self.rows > 0 else MAX_CELL_SIZE
        cell_size = min(size_by_w, size_by_h)

        return max(MIN_CELL_SIZE, min(MAX_CELL_SIZE, cell_size))

    def create_grid(self):
        """Tear down the old canvas and draw a fresh grid from scratch.

        Steps:
            1. Destroy previous canvas (if any).
            2. Recompute cell_size from the current container dimensions.
            3. Create a new canvas centred inside the parent.
            4. Place random plain-road tiles on every cell.
            5. Pre-create hidden overlay rectangles for animation use.
        """
        if self.canvas:
            self.canvas.destroy()

        self.cell_size = self._compute_cell_size()
        canvas_w = self.cols * self.cell_size
        canvas_h = self.rows * self.cell_size

        self.canvas = ctk.CTkCanvas(
            self.parent, width=canvas_w, height=canvas_h,
            bg=CANVAS_BG, highlightthickness=0
        )
        self.canvas.place(relx=0.5, rely=0.5, anchor="center")

        # Bind mouse events for interactive placement
        self.canvas.bind("<Button-1>",        self.handle_click)
        self.canvas.bind("<B1-Motion>",       self.handle_drag)
        self.canvas.bind("<ButtonRelease-1>", self.handle_release)

        # Reset all per-cell data
        self.logic_grid     = [[0]    * self.cols for _ in range(self.rows)]
        self.road_type_grid = [[None] * self.cols for _ in range(self.rows)]
        self.image_ids      = [[None] * self.cols for _ in range(self.rows)]
        self.building_ids   = [[None] * self.cols for _ in range(self.rows)]
        self.overlay_ids    = [[None] * self.cols for _ in range(self.rows)]
        self.truck_image_id = None
        self.fire_image_id  = None
        self.start_pos      = None
        self.goal_pos       = None

        # Place road tiles and pre-create overlay rectangles
        for r in range(self.rows):
            for c in range(self.cols):
                self._place_road(r, c, PLAIN_ROADS)

                # Hidden overlay (made visible during algorithm animation)
                x1 = c * self.cell_size + 1
                y1 = r * self.cell_size + 1
                x2 = x1 + self.cell_size - 2
                y2 = y1 + self.cell_size - 2
                oid = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill="", outline="", stipple="gray12", state="hidden"
                )
                self.overlay_ids[r][c] = oid

    def _place_road(self, r, c, road_pool):
        """Place a random road tile from *road_pool* at cell (r, c)."""
        road_name = random.choice(road_pool)
        self.road_type_grid[r][c] = road_name

        cx = c * self.cell_size + self.cell_size // 2
        cy = r * self.cell_size + self.cell_size // 2
        img = self.assets.roads.get(road_name)

        if img:
            img_id = self.canvas.create_image(cx, cy, image=img, anchor="center")
            self.image_ids[r][c] = img_id
        else:
            # Fallback: plain coloured rectangle when sprite is missing
            x1, y1 = c * self.cell_size, r * self.cell_size
            x2, y2 = x1 + self.cell_size, y1 + self.cell_size
            rect_id = self.canvas.create_rectangle(
                x1, y1, x2, y2, outline=GRID_LINE, fill=CANVAS_BG
            )
            self.image_ids[r][c] = rect_id

    # ═══════════════════════════════════════════════════════════
    #  PLACING ELEMENTS (buildings, start truck, goal fire)
    # ═══════════════════════════════════════════════════════════

    def place_building(self, r, c):
        """Place a random building sprite at (r, c), marking the cell as a wall."""
        if self.building_ids[r][c] is not None:
            return                                 # Cell already occupied

        self.logic_grid[r][c] = 1
        bld_index = random.randint(1, len(self.assets.buildings))

        cx = c * self.cell_size + self.cell_size // 2
        cy = r * self.cell_size + self.cell_size // 2
        img = self.assets.buildings.get(bld_index)

        if img:
            bld_id = self.canvas.create_image(cx, cy, image=img, anchor="center")
            self.building_ids[r][c] = bld_id

    def remove_building(self, r, c):
        """Remove a building at (r, c) and mark the cell as open again."""
        if self.building_ids[r][c] is not None:
            self.canvas.delete(self.building_ids[r][c])
            self.building_ids[r][c] = None
        self.logic_grid[r][c] = 0

    def place_start(self, r, c):
        """Place the fire-truck (start position) at cell (r, c).

        Any previous start position is cleared. Buildings at the target cell
        are removed automatically.
        """
        # Remove old truck sprite
        if self.truck_image_id is not None:
            self.canvas.delete(self.truck_image_id)
            self.truck_image_id = None

        # Clear building at old start
        if self.start_pos:
            old_r, old_c = self.start_pos
            if self.building_ids[old_r][old_c]:
                self.remove_building(old_r, old_c)

        # Clear building at new start
        if self.building_ids[r][c]:
            self.remove_building(r, c)

        self.start_pos = (r, c)
        self.logic_grid[r][c] = 0                  # Start is always traversable

        cx = c * self.cell_size + self.cell_size // 2
        cy = r * self.cell_size + self.cell_size // 2
        img = self.assets.truck.get("right")       # Default facing direction

        if img:
            self.truck_image_id = self.canvas.create_image(
                cx, cy, image=img, anchor="center"
            )

    def place_goal(self, r, c):
        """Place the fire (goal position) at cell (r, c).

        Any previous goal is cleared. Buildings at the target cell are removed.
        Notifies the app to start the fire-crackling ambient sound.
        """
        # Remove old fire sprite
        if self.fire_image_id is not None:
            self.canvas.delete(self.fire_image_id)
            self.fire_image_id = None

        # Clear building at old goal
        if self.goal_pos:
            old_r, old_c = self.goal_pos
            if self.building_ids[old_r][old_c]:
                self.remove_building(old_r, old_c)

        # Clear building at new goal
        if self.building_ids[r][c]:
            self.remove_building(r, c)

        self.goal_pos = (r, c)
        self.logic_grid[r][c] = 0                  # Goal is always traversable

        cx = c * self.cell_size + self.cell_size // 2
        cy = r * self.cell_size + self.cell_size // 2
        img = self.assets.fire_frames.get(1)

        if img:
            self.fire_image_id = self.canvas.create_image(
                cx, cy, image=img, anchor="center"
            )

        # Notify app.py → starts ambient fire-crackling sound
        if self.on_goal_placed:
            self.on_goal_placed()

    # ═══════════════════════════════════════════════════════════
    #  OVERLAYS (exploration & path visualisation)
    # ═══════════════════════════════════════════════════════════

    def set_overlay(self, r, c, color):
        """Make the pre-created overlay at (r, c) visible with the given colour."""
        oid = self.overlay_ids[r][c]
        if oid is not None:
            self.canvas.itemconfig(oid, fill=color, state="normal")

    def clear_overlays(self):
        """Hide every overlay rectangle (fast batch `itemconfig`, no create/delete)."""
        for r in range(self.rows):
            for c in range(self.cols):
                oid = self.overlay_ids[r][c]
                if oid is not None:
                    self.canvas.itemconfig(oid, fill="", state="hidden")

    # ═══════════════════════════════════════════════════════════
    #  MOUSE EVENT HANDLERS
    # ═══════════════════════════════════════════════════════════

    def handle_click(self, event):
        """Process a single left-click on the canvas.

        Behaviour varies by mode:
            Wall  – toggle a building on/off.
            Start – move the fire truck here.
            Goal  – move the fire here.
            Road  – replace the road tile with the sidebar-selected type (UCS).
        """
        c = event.x // self.cell_size
        r = event.y // self.cell_size

        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return

        if self.mode == "Wall":
            if (r, c) == self.start_pos or (r, c) == self.goal_pos:
                return
            if self.logic_grid[r][c] == 1:
                self.remove_building(r, c)         # Toggle off
            else:
                self.place_building(r, c)           # Toggle on
                self._flash_cell(r, c)
            self.drag_visited.add((r, c))
            if self.sfx:
                self.sfx.play_cell_click()

        elif self.mode == "Start":
            self.place_start(r, c)
            if self.sfx:
                self.sfx.play_cell_click()

        elif self.mode == "Goal":
            self.place_goal(r, c)
            if self.sfx:
                self.sfx.play_cell_click()

        elif self.mode == "Road":
            if (r, c) == self.start_pos or (r, c) == self.goal_pos:
                return
            if self.logic_grid[r][c] == 1:
                return                             # Can't place road on a wall
            self._place_custom_road(r, c)
            self._flash_cell(r, c)
            self.drag_visited.add((r, c))
            if self.sfx:
                self.sfx.play_cell_click()

    def handle_drag(self, event):
        """Process mouse drag — continuously places walls or roads.

        Only Wall and Road modes support drag placement. Cells already visited
        in this drag stroke are skipped to avoid rapid re-toggling.
        """
        if self.mode not in ("Wall", "Road"):
            return

        c = event.x // self.cell_size
        r = event.y // self.cell_size

        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return
        if (r, c) in self.drag_visited:
            return
        if (r, c) == self.start_pos or (r, c) == self.goal_pos:
            return

        self.drag_visited.add((r, c))

        if self.mode == "Wall" and self.logic_grid[r][c] == 0:
            self.place_building(r, c)
            self._flash_cell(r, c)
            if self.sfx:
                self.sfx.play_cell_click()

        elif self.mode == "Road" and self.logic_grid[r][c] == 0:
            self._place_custom_road(r, c)
            self._flash_cell(r, c)
            if self.sfx:
                self.sfx.play_cell_click()

    def handle_release(self, event):
        """Reset the drag-tracking set when the mouse button is released."""
        self.drag_visited.clear()

    # ═══════════════════════════════════════════════════════════
    #  VISUAL FEEDBACK
    # ═══════════════════════════════════════════════════════════

    def _flash_cell(self, r, c):
        """Play a brief white flash on a cell for placement feedback."""
        oid = self.overlay_ids[r][c]
        if oid is None:
            return
        self.canvas.itemconfig(oid, fill="#ffffff", state="normal")
        self.canvas.after(80, lambda: self.canvas.itemconfig(oid, fill="", state="hidden"))

    # ═══════════════════════════════════════════════════════════
    #  CUSTOM ROAD PLACEMENT (UCS weighted roads)
    # ═══════════════════════════════════════════════════════════

    def _place_custom_road(self, r, c):
        """Replace the road tile at (r, c) with the user-selected type from the sidebar."""
        if self.road_type_callback is None:
            return

        road_name = self.road_type_callback()
        self.road_type_grid[r][c] = road_name

        # Remove old road sprite
        if self.image_ids[r][c] is not None:
            self.canvas.delete(self.image_ids[r][c])

        cx = c * self.cell_size + self.cell_size // 2
        cy = r * self.cell_size + self.cell_size // 2
        img = self.assets.roads.get(road_name)

        if img:
            img_id = self.canvas.create_image(cx, cy, image=img, anchor="center")
            self.image_ids[r][c] = img_id

            # Keep overlay above the new road tile for animation visibility
            oid = self.overlay_ids[r][c]
            if oid is not None:
                self.canvas.tag_raise(oid)

    # ═══════════════════════════════════════════════════════════
    #  UTILITY / PUBLIC API
    # ═══════════════════════════════════════════════════════════

    def resize(self, new_rows, new_cols, asset_manager):
        """Resize the grid to new dimensions (cell_size is recalculated)."""
        self.rows   = new_rows
        self.cols   = new_cols
        self.assets = asset_manager
        self.create_grid()

    def build_weighted_grid(self):
        """Build the weighted grid structure expected by the UCS algorithm.

        Returns:
            A 2-D list of dicts: [{"blocked": bool, "weight": int}, ...]
        """
        grid = []
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                blocked   = bool(self.logic_grid[r][c])
                road_name = self.road_type_grid[r][c]
                weight    = ROAD_TYPES[road_name][1] if road_name in ROAD_TYPES else 1
                row.append({"blocked": blocked, "weight": weight})
            grid.append(row)
        return grid

    def get_logic_grid(self):
        """Return the simple 0/1 grid used by BFS and DFS."""
        return self.logic_grid

    def disable_interaction(self):
        """Unbind all mouse events (called during animations)."""
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")

    def enable_interaction(self):
        """Re-bind mouse events (called after animations complete)."""
        self.canvas.bind("<Button-1>",        self.handle_click)
        self.canvas.bind("<B1-Motion>",       self.handle_drag)
        self.canvas.bind("<ButtonRelease-1>", self.handle_release)

    def set_algo_mode(self, algo):
        """Update the active algorithm mode (affects road types on grid reset)."""
        self.algo_mode = algo
