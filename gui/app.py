"""
app.py — Main application window and algorithm orchestrator.

This module contains the AIVisualizer class which serves as the root window
for the Fire Brigade Pathfinding Visualizer. It ties together the sidebar
controls, grid canvas, animation engine, asset manager, and sound system
into a cohesive interactive application.

Architecture:
    AIVisualizer (CTk root window)
    ├── Sidebar           — user controls (mode, algo, grid size, actions)
    ├── Header Bar        — branded title and version badge
    ├── Canvas Container  — holds the GridCanvas for city visualisation
    ├── Status Bar        — live mode / algorithm / grid size indicators
    ├── Animator          — step-by-step exploration, path, and truck animations
    └── SoundManager      — ambient and UI sound effects
"""

import os
import customtkinter as ctk

from gui.constants import (
    WINDOW_TITLE, WINDOW_MINSIZE,
    DEFAULT_ROWS, DEFAULT_COLS, DEFAULT_CELL_SIZE,
    MIN_GRID_SIZE, MAX_GRID_SIZE, TRUCK_GRID_THRESHOLD,
    ROAD_TYPES, ICON_DIR
)
from gui.asset_manager import AssetManager
from gui.grid_canvas   import GridCanvas
from gui.sidebar       import Sidebar
from gui.animations    import Animator
from gui.sound_manager import SoundManager

from algorithms import bfs, dfs, ucs, Astar


class AIVisualizer(ctk.CTk):
    """Root window — the Fire Brigade Pathfinding Visualizer.

    Responsibilities:
        1. Window setup (title, icon, fullscreen, dark theme).
        2. Layout construction (sidebar, header, canvas, status bar).
        3. Algorithm dispatch (BFS / DFS / UCS / A*).
        4. Animation chain orchestration (explore → path → truck → extinguish).
        5. Sound effect coordination (fire crackling, siren, extinguisher).
    """

    # ═══════════════════════════════════════════════════════════
    #  INITIALISATION
    # ═══════════════════════════════════════════════════════════

    def __init__(self):
        super().__init__()

        # ── Window chrome ──
        self.title(WINDOW_TITLE)
        self.minsize(*WINDOW_MINSIZE)

        # Set the taskbar / title-bar icon (if available)
        ico_path = os.path.join(ICON_DIR, "app_icon.ico")
        if os.path.exists(ico_path):
            self.iconbitmap(ico_path)

        # Adaptive fullscreen — fill the screen and maximise after render
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        self.geometry(f"{screen_w}x{screen_h}+0+0")
        self.after(10, lambda: self.state("zoomed"))

        # ── Theme ──
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color="#0a0a14")          # Deep navy background

        # ── Grid & animation state ──
        self.rows          = DEFAULT_ROWS
        self.cols          = DEFAULT_COLS
        self.cell_size     = DEFAULT_CELL_SIZE
        self.is_animating  = False                  # True while any animation runs

        # ── Subsystems ──
        self.sfx    = SoundManager()
        self.assets = AssetManager(self.cell_size)

        # ── Build the UI ──
        self._build_layout()

        # ── Animator (needs grid_canvas, so created after layout) ──
        self.animator = Animator(self, self.grid_canvas, self.assets)

        # ── Toast overlay state ──
        self._toast_label    = None
        self._toast_after_id = None

        # ── Fire crackling tracking ──
        self._fire_crackling_active = False

        # ── Delayed initial redraw (ensures container dimensions are real) ──
        self.after(100, self._initial_grid_refresh)

    # ═══════════════════════════════════════════════════════════
    #  LAYOUT CONSTRUCTION
    # ═══════════════════════════════════════════════════════════

    def _build_layout(self):
        """Build the full UI: sidebar → right panel (header, canvas, status bar)."""

        # Root container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # ── Sidebar ──
        self.sidebar = Sidebar(self.main_container, callbacks={
            "set_mode":      self.set_mode,
            "run_algorithm": self.run_algorithm,
            "clear_path":    self.clear_path,
            "reset_grid":    self.reset_grid,
            "resize_grid":   self.resize_grid,
            "algo_changed":  self.on_algo_changed,
        }, sound_manager=self.sfx)

        # ── Right-side panel (stacks vertically: header → canvas → status) ──
        self.right_panel = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.right_panel.pack(side="left", fill="both", expand=True)

        self._build_header()

        # Canvas wrapper with purple accent border
        self.canvas_container = ctk.CTkFrame(
            self.right_panel, corner_radius=12,
            fg_color="#0f0f1a",
            border_width=2, border_color="#7c3aed"
        )
        self.canvas_container.pack(fill="both", expand=True, padx=2, pady=2)

        # ── Grid Canvas (the interactive city map) ──
        self.grid_canvas = GridCanvas(
            self.canvas_container, self.assets,
            self.rows, self.cols, self.cell_size
        )

        # Wire canvas callbacks so grid events reach the right handlers
        self.grid_canvas.road_type_callback = self.sidebar.get_selected_road_type
        self.grid_canvas.sfx               = self.sfx
        self.grid_canvas.on_goal_placed     = self._start_fire_crackling_if_needed
        self.grid_canvas.on_goal_removed    = self._stop_fire_crackling

        self._build_status_bar()

    def _build_header(self):
        """Compact branded header bar above the canvas area."""
        header = ctk.CTkFrame(
            self.right_panel, fg_color="#0f0f1a", corner_radius=10,
            height=44, border_width=1, border_color="#2a2a4a"
        )
        header.pack(fill="x", pady=(0, 6))
        header.pack_propagate(False)

        # Title (left-aligned)
        ctk.CTkLabel(
            header, text="🔥  Fire Brigade AI  —  Pathfinding Visualizer",
            font=("Segoe UI Semibold", 14), text_color="#c8cad0"
        ).pack(side="left", padx=12)

        # Version badge (right-aligned)
        ctk.CTkLabel(
            header, text="  v1.0  ",
            font=("Segoe UI Bold", 10), text_color="#ffffff",
            fg_color="#7c3aed", corner_radius=6
        ).pack(side="right", padx=12)

    def _build_status_bar(self):
        """Live status bar below the canvas showing mode, algorithm, and grid size."""
        self.status_bar = ctk.CTkFrame(
            self.right_panel, fg_color="#0f0f1a", corner_radius=10,
            height=32, border_width=1, border_color="#2a2a4a"
        )
        self.status_bar.pack(fill="x", pady=(6, 0))
        self.status_bar.pack_propagate(False)

        # Helper to add an indicator + separator dot
        def _indicator(text):
            lbl = ctk.CTkLabel(self.status_bar, text=text,
                               font=("Segoe UI", 11), text_color="#6b7280")
            lbl.pack(side="left", padx=12)
            # Separator dot after each indicator (except the last)
            ctk.CTkLabel(self.status_bar, text="•", text_color="#3b3b5c",
                         font=("Segoe UI", 11)).pack(side="left")
            return lbl

        self._status_mode = _indicator("🖱️ Wall")
        self._status_algo = _indicator("🧠 BFS")

        # Last indicator — no trailing dot needed
        self._status_grid = ctk.CTkLabel(
            self.status_bar, text=f"📐 {self.rows}×{self.cols}",
            font=("Segoe UI", 11), text_color="#6b7280"
        )
        self._status_grid.pack(side="left", padx=12)

    def _update_status_bar(self):
        """Refresh all three status bar indicators to reflect current state."""
        self._status_mode.configure(text=f"🖱️ {self.grid_canvas.mode}")
        self._status_algo.configure(text=f"🧠 {self.sidebar.get_selected_algo()}")
        self._status_grid.configure(text=f"📐 {self.rows}×{self.cols}")

    # ═══════════════════════════════════════════════════════════
    #  TOAST NOTIFICATIONS
    # ═══════════════════════════════════════════════════════════

    def show_toast(self, message, duration_ms=3000, error=False):
        """Display a frosted-glass toast notification at the top of the canvas.

        Args:
            message:     Text to display.
            duration_ms: Auto-dismiss delay in milliseconds.
            error:       If True, shows red accent and plays the error sound.
        """
        # Dismiss any existing toast first
        if self._toast_after_id:
            self.after_cancel(self._toast_after_id)
        if self._toast_label:
            self._toast_label.destroy()

        if error:
            self.sfx.play_error()

        # Colour scheme: red accent for errors, purple for info
        accent = "#dc2626" if error else "#7c3aed"

        toast_frame = ctk.CTkFrame(
            self.canvas_container, fg_color="#1a1a2e", corner_radius=10,
            border_width=2, border_color=accent
        )
        toast_frame.place(relx=0.5, rely=0.03, anchor="n")

        # Icon
        icon = "⚠️" if error else "ℹ️"
        ctk.CTkLabel(
            toast_frame, text=icon,
            font=("Segoe UI", 14), text_color=accent
        ).pack(side="left", padx=(12, 4), pady=8)

        # Message text
        ctk.CTkLabel(
            toast_frame, text=message,
            font=("Segoe UI Semibold", 12), text_color="#e0e0e0"
        ).pack(side="left", padx=(0, 14), pady=8)

        self._toast_label = toast_frame
        self._toast_after_id = self.after(duration_ms, self._dismiss_toast)

    def _dismiss_toast(self):
        """Remove the active toast notification."""
        if self._toast_label:
            self._toast_label.destroy()
            self._toast_label = None
        self._toast_after_id = None

    # ═══════════════════════════════════════════════════════════
    #  INITIAL GRID REFRESH
    # ═══════════════════════════════════════════════════════════

    def _initial_grid_refresh(self):
        """Redraw grid after the window has fully rendered.

        On startup the container has no real dimensions yet, so assets load
        at an incorrect size. This deferred call recalculates cell_size from
        the now-real container width/height, reloads assets, and redraws.
        """
        correct_size = self.grid_canvas._compute_cell_size()
        self.assets.reload(correct_size)
        self.grid_canvas.create_grid()

    # ═══════════════════════════════════════════════════════════
    #  FIRE CRACKLING MANAGEMENT
    # ═══════════════════════════════════════════════════════════

    def _start_fire_crackling_if_needed(self):
        """Start the ambient fire crackling loop when a goal (fire) is on the grid."""
        if self.grid_canvas.goal_pos and not self._fire_crackling_active:
            self.sfx.start_fire_crackling()
            self._fire_crackling_active = True

    def _stop_fire_crackling(self):
        """Stop the ambient fire crackling loop."""
        if self._fire_crackling_active:
            self.sfx.stop_fire_crackling()
            self._fire_crackling_active = False

    # ═══════════════════════════════════════════════════════════
    #  SIDEBAR CALLBACKS
    # ═══════════════════════════════════════════════════════════

    def set_mode(self, value):
        """Handle mode switch (Start / Goal / Wall / Road)."""
        self.grid_canvas.mode = value
        self._update_status_bar()

    def on_algo_changed(self, algo):
        """Handle algorithm switch — preserve the current grid.

        When leaving UCS mode, downgrade any weighted roads back to plain
        roads so BFS/DFS don't see stale weight data.
        """
        old_algo = self.grid_canvas.algo_mode
        self.grid_canvas.set_algo_mode(algo)

        # Downgrade weighted roads when leaving UCS
        if old_algo == "UCS" and algo != "UCS":
            for r in range(self.grid_canvas.rows):
                for c in range(self.grid_canvas.cols):
                    rt = self.grid_canvas.road_type_grid[r][c]
                    if rt and rt not in ("RoadPlain1", "RoadPlain2"):
                        self.grid_canvas.road_type_grid[r][c] = "RoadPlain1"

        self._update_status_bar()

    def resize_grid(self):
        """Resize the grid to the value entered in the sidebar input field."""
        try:
            new_size = int(self.sidebar.get_grid_size_input())
            if new_size < MIN_GRID_SIZE or new_size > MAX_GRID_SIZE:
                self.show_toast(
                    f"⚠️ Grid size must be {MIN_GRID_SIZE}–{MAX_GRID_SIZE}",
                    3000, error=True
                )
                return

            self._stop_fire_crackling()
            self.rows = self.cols = new_size

            # Rebuild the grid at the new dimensions
            self.grid_canvas.resize(self.rows, self.cols, self.assets)
            self.assets.reload(self.grid_canvas.cell_size)
            self.grid_canvas.create_grid()
            self.sidebar.clear_results()
            self._update_status_bar()

            # Inform user about truck animation threshold
            if new_size > TRUCK_GRID_THRESHOLD:
                self.show_toast(
                    f"⚡ {new_size}×{new_size} grid — truck animation skipped for speed",
                    3000
                )

        except ValueError:
            self.show_toast("⚠️ Please enter a valid number", 3000, error=True)

    def clear_path(self):
        """Remove exploration/path overlays but keep walls, start, and goal."""
        self.grid_canvas.clear_overlays()
        self.sidebar.clear_results()
        self.animator.stop_fire_cycle()
        self.sfx.stop_siren()

        # Restore the fire sprite at the goal position (it gets removed during extinguish)
        if self.grid_canvas.goal_pos and self.grid_canvas.fire_image_id is None:
            r, c = self.grid_canvas.goal_pos
            self.grid_canvas.place_goal(r, c)
            self._start_fire_crackling_if_needed()

        # Restore the truck at the start position
        if self.grid_canvas.start_pos:
            r, c = self.grid_canvas.start_pos
            self.grid_canvas.place_start(r, c)

    def reset_grid(self):
        """Completely reset the grid — clears everything and redraws from scratch."""
        self._stop_fire_crackling()
        self.sfx.stop_siren()
        self.animator.stop_fire_cycle()
        self.grid_canvas.create_grid()
        self.sidebar.clear_results()

    # ═══════════════════════════════════════════════════════════
    #  ALGORITHM ROUTER
    # ═══════════════════════════════════════════════════════════

    def run_algorithm(self):
        """Dispatch to the correct algorithm runner based on the sidebar selection."""
        if self.is_animating:
            return

        algo = self.sidebar.get_selected_algo()

        if algo == "BFS":
            self.run_bfs()
        elif algo == "DFS":
            self.run_dfs()
        elif algo == "UCS":
            self.run_ucs()
        elif algo in ("A* (Manhattan)", "A* (Euclidean)"):
            # Pass True for Euclidean heuristic, False for Manhattan
            self.run_astar(is_euclidean=(algo == "A* (Euclidean)"))

    # ═══════════════════════════════════════════════════════════
    #  UI STATE CONTROL
    # ═══════════════════════════════════════════════════════════

    def disable_controls(self):
        """Lock the UI during an animation to prevent conflicting interactions."""
        self.is_animating = True
        self.sidebar.disable_buttons()
        self.grid_canvas.disable_interaction()

    def enable_controls(self):
        """Unlock the UI after an animation completes."""
        self.is_animating = False
        self.sidebar.enable_buttons()
        self.grid_canvas.enable_interaction()

    # ═══════════════════════════════════════════════════════════
    #  VALIDATION
    # ═══════════════════════════════════════════════════════════

    def _validate_start_goal(self):
        """Ensure both start and goal positions are placed before running."""
        if not self.grid_canvas.start_pos:
            self.show_toast("⚠️ Place a start position (fire truck) first!", 3000, error=True)
            return False
        if not self.grid_canvas.goal_pos:
            self.show_toast("⚠️ Place a goal position (fire) first!", 3000, error=True)
            return False
        return True

    # ═══════════════════════════════════════════════════════════
    #  ALGORITHM RUNNERS
    # ═══════════════════════════════════════════════════════════

    def run_bfs(self):
        """Run Breadth-First Search and animate the result."""
        if not self._validate_start_goal():
            return

        self.clear_path()
        result = bfs(
            self.grid_canvas.get_logic_grid(),
            self.grid_canvas.start_pos,
            self.grid_canvas.goal_pos
        )

        if result is False:
            self.show_toast("❌ No path found to the fire!", 3000, error=True)
            return

        visited_history, final_path = result
        self.sidebar.update_results(cells_explored=len(visited_history))
        self.disable_controls()
        self.animator.start_fire_cycle()
        self.animator.animate_exploration(
            visited_history, final_path, "BFS", self._on_exploration_done
        )

    def run_dfs(self):
        """Run Depth-First Search and animate the result."""
        if not self._validate_start_goal():
            return

        self.clear_path()
        result = dfs(
            self.grid_canvas.get_logic_grid(),
            self.grid_canvas.start_pos,
            self.grid_canvas.goal_pos
        )

        if result is False:
            self.show_toast("❌ No path found to the fire!", 3000, error=True)
            return

        visited_history, final_path = result
        self.sidebar.update_results(cells_explored=len(visited_history))
        self.disable_controls()
        self.animator.start_fire_cycle()
        self.animator.animate_exploration(
            visited_history, final_path, "DFS", self._on_exploration_done
        )

    def run_ucs(self):
        """Run Uniform-Cost Search and animate the result (uses weighted grid)."""
        if not self._validate_start_goal():
            return

        self.clear_path()
        weighted_grid = self.grid_canvas.build_weighted_grid()
        result = ucs(
            weighted_grid,
            self.grid_canvas.start_pos,
            self.grid_canvas.goal_pos
        )

        if result is False:
            self.show_toast("❌ No path found to the fire!", 3000, error=True)
            return

        visited_history, final_path = result

        # Sum edge weights along the final path for the total cost display
        total_cost = 0
        for r, c in final_path:
            road_name = self.grid_canvas.road_type_grid[r][c]
            if road_name:
                total_cost += ROAD_TYPES[road_name][1]

        self.sidebar.update_results(
            cells_explored=len(visited_history),
            total_cost=total_cost
        )
        self.disable_controls()
        self.animator.start_fire_cycle()
        self.animator.animate_exploration(
            visited_history, final_path, "UCS", self._on_exploration_done
        )

    def run_astar(self, is_euclidean=False):
        """Run A* Search and animate the result (uses weighted grid).

        A* uses the same weighted-grid format as UCS but with uniform
        weights (all 1).  The *is_euclidean* flag selects between
        Manhattan and Euclidean heuristics — passed straight through
        to the Astar algorithm.

        Args:
            is_euclidean: If True, use Euclidean distance heuristic;
                          if False (default), use Manhattan distance.
        """
        if not self._validate_start_goal():
            return

        self.clear_path()

        # A* expects the same dict grid as UCS ({"blocked": bool, "weight": int})
        weighted_grid = self.grid_canvas.build_weighted_grid()
        result = Astar(
            weighted_grid,
            self.grid_canvas.start_pos,
            self.grid_canvas.goal_pos,
            is_euclidean
        )

        if result is False:
            self.show_toast("❌ No path found to the fire!", 3000, error=True)
            return

        visited_history, final_path = result

        # A* uses uniform weights (all 1), so total cost equals path length
        total_cost = len(final_path)

        algo_label = "A* (Euclidean)" if is_euclidean else "A* (Manhattan)"
        self.sidebar.update_results(
            cells_explored=len(visited_history),
            total_cost=total_cost
        )
        self.disable_controls()
        self.animator.start_fire_cycle()
        self.animator.animate_exploration(
            visited_history, final_path, algo_label, self._on_exploration_done
        )

    # ═══════════════════════════════════════════════════════════
    #  ANIMATION CHAIN CALLBACKS
    #  Execution order: explore → path → truck → extinguish → done
    # ═══════════════════════════════════════════════════════════

    def _on_exploration_done(self, final_path, algo):
        """Phase 2: exploration finished → animate the shortest path."""
        self.animator.animate_path(final_path, algo, self._on_path_done)

    def _on_path_done(self, final_path, algo):
        """Phase 3: path drawn → show stats, start siren, move the truck."""
        self.sidebar.update_results(path_steps=len(final_path))
        self.sfx.start_siren()
        self.animator.animate_truck(final_path, self._on_truck_done)

    def _on_truck_done(self):
        """Phase 4: truck arrived → stop siren, play extinguisher, douse the fire."""
        self.sfx.stop_siren()
        self.sfx.play_extinguisher()
        self._stop_fire_crackling()
        self.animator.extinguish_fire(self._on_fire_extinguished)

    def _on_fire_extinguished(self):
        """Phase 5: fire is out → re-enable all controls."""
        self.enable_controls()
