"""
sidebar.py — Premium sidebar control panel.

Provides all user-facing controls for the Fire Brigade Pathfinding Visualizer:
    • Grid Size   – text entry + resize button (10–50 cells)
    • Place Mode  – segmented button (Start / Goal / Wall / Road [UCS only])
    • Algorithm   – dropdown menu (BFS, DFS, UCS, A*)
    • Actions     – Run, Clear, Reset buttons
    • Results     – live stat display (Path Length, Cost, Explored)
    • Mute Toggle – sound on/off with speaker icon

Design uses a card-style layout in a navy-purple dark theme with modern
typography (Segoe UI) and scrollable interior for small screens.
"""

import os
import customtkinter as ctk
from PIL import Image
from gui.constants import UI_DIR

# ──────────────────── THEME PALETTE ────────────────────
SIDEBAR_BG       = "#0f0f1a"       # Main sidebar background
CARD_BG          = "#1a1a2e"       # Card / section backgrounds
CARD_BORDER      = "#2a2a4a"       # Subtle card borders
HEADER_ACCENT    = "#7c3aed"       # Purple accent for header bar
LABEL_COLOR      = "#c8cad0"       # Primary label text
SUBLABEL_COLOR   = "#6b7280"       # Secondary / hint text
STAT_VALUE_COLOR = "#10b981"       # Green for stat values
ENTRY_BG         = "#16162a"       # Entry field background
ENTRY_BORDER     = "#3b3b5c"       # Entry field border

# Button colours (foreground, hover)
RUN_FG       = "#059669";  RUN_HOVER    = "#047857"
CLEAR_FG     = "#2563eb";  CLEAR_HOVER  = "#1d4ed8"
RESET_FG     = "#dc2626";  RESET_HOVER  = "#b91c1c"
RESIZE_FG    = "#6366f1";  RESIZE_HOVER = "#4f46e5"
MUTE_FG      = "#1e1e36";  MUTE_HOVER   = "#2a2a4a"


class Sidebar:
    """Premium sidebar control panel for the Fire Brigade Pathfinding Visualizer.

    All user interactions trigger callbacks provided by the parent AIVisualizer,
    decoupling the UI widgets from the application logic.

    Args:
        parent_frame:  The CTkFrame that hosts the sidebar.
        callbacks:     Dict mapping action names → callable handlers.
        sound_manager: Optional SoundManager for button click sounds.
    """

    def __init__(self, parent_frame, callbacks, sound_manager=None):
        self.callbacks = callbacks
        self.sfx       = sound_manager

        # ── Outer sidebar frame (fixed 250 px width) ──
        self.frame = ctk.CTkFrame(
            parent_frame, width=250, corner_radius=12,
            fg_color=SIDEBAR_BG, border_width=1, border_color=CARD_BORDER
        )
        self.frame.pack(side="left", fill="y", padx=(0, 10))
        self.frame.pack_propagate(False)

        # ── Scrollable interior (prevents clipping on small screens) ──
        self._inner = ctk.CTkScrollableFrame(
            self.frame, fg_color="transparent",
            scrollbar_button_color=CARD_BORDER,
            scrollbar_button_hover_color=HEADER_ACCENT
        )
        self._inner.pack(fill="both", expand=True, padx=6, pady=6)

        # Build each card section in visual order
        self._build_header()
        self._build_grid_card()
        self._build_mode_card()
        self._build_algo_card()
        self._build_action_card()
        self._build_results_card()
        self._build_mute_toggle()

    # ═══════════════════════════════════════════════════════════
    #  CARD HELPERS
    # ═══════════════════════════════════════════════════════════

    def _card(self, parent, pady=(4, 4)):
        """Create and pack a rounded card frame with a subtle border."""
        card = ctk.CTkFrame(
            parent, fg_color=CARD_BG, corner_radius=10,
            border_width=1, border_color=CARD_BORDER
        )
        card.pack(fill="x", padx=2, pady=pady)
        return card

    def _section_label(self, parent, icon, text):
        """Create a styled section header label (icon + title) inside a card."""
        ctk.CTkLabel(
            parent, text=f"{icon}  {text}",
            font=("Segoe UI Semibold", 12),
            text_color=LABEL_COLOR, anchor="w"
        ).pack(anchor="w", padx=10, pady=(8, 4))

    # ═══════════════════════════════════════════════════════════
    #  CARD SECTIONS
    # ═══════════════════════════════════════════════════════════

    def _build_header(self):
        """App branding header with purple accent bars."""
        header = ctk.CTkFrame(self._inner, fg_color="transparent")
        header.pack(fill="x", pady=(2, 6))

        # Top accent bar
        ctk.CTkFrame(
            header, fg_color=HEADER_ACCENT, height=3, corner_radius=2
        ).pack(fill="x", padx=20, pady=(0, 6))

        ctk.CTkLabel(
            header, text="🚒 Fire Brigade",
            font=("Segoe UI Bold", 18), text_color="#ffffff"
        ).pack()
        ctk.CTkLabel(
            header, text="Pathfinding Visualizer",
            font=("Segoe UI", 11), text_color=SUBLABEL_COLOR
        ).pack(pady=(0, 2))

        # Bottom accent bar
        ctk.CTkFrame(
            header, fg_color=HEADER_ACCENT, height=3, corner_radius=2
        ).pack(fill="x", padx=20, pady=(6, 0))

    def _build_grid_card(self):
        """Grid Size card — text entry and Resize button."""
        card = self._card(self._inner)
        self._section_label(card, "📐", "Grid Size")

        input_row = ctk.CTkFrame(card, fg_color="transparent")
        input_row.pack(fill="x", padx=10, pady=(2, 8))

        self.grid_size_entry = ctk.CTkEntry(
            input_row, width=70, height=30, placeholder_text="10",
            font=("Segoe UI", 12), corner_radius=6,
            fg_color=ENTRY_BG, border_color=ENTRY_BORDER, border_width=1
        )
        self.grid_size_entry.pack(side="left", padx=(0, 6))

        self.resize_btn = ctk.CTkButton(
            input_row, text="↻ Resize", width=90, height=30,
            fg_color=RESIZE_FG, hover_color=RESIZE_HOVER,
            font=("Segoe UI Semibold", 11), corner_radius=6,
            command=self._on_resize_click
        )
        self.resize_btn.pack(side="left", expand=True, fill="x")

        ctk.CTkLabel(
            card, text="Range: 10 – 50 cells",
            font=("Segoe UI", 9), text_color=SUBLABEL_COLOR
        ).pack(padx=10, anchor="w", pady=(0, 6))

    def _build_mode_card(self):
        """Place Mode card — segmented button + optional Road-type picker for UCS."""
        card = self._card(self._inner)
        self._section_label(card, "🖱️", "Place Mode")

        self._mode_inner = ctk.CTkFrame(card, fg_color="transparent")
        self._mode_inner.pack(fill="x", padx=10, pady=(2, 8))

        self.mode_switch = ctk.CTkSegmentedButton(
            self._mode_inner, values=["Start", "Goal", "Wall"],
            command=self._on_mode_change,
            font=("Segoe UI Semibold", 11),
            corner_radius=6, height=30,
            selected_color=HEADER_ACCENT,
            selected_hover_color="#6d28d9"
        )
        self.mode_switch.set("Wall")
        self.mode_switch.pack(fill="x")

        # Road type picker — shown only when mode=Road and algo=UCS
        self._road_picker_frame = ctk.CTkFrame(self._mode_inner, fg_color="transparent")

        ctk.CTkLabel(
            self._road_picker_frame, text="Road Type:",
            font=("Segoe UI", 10), text_color=SUBLABEL_COLOR
        ).pack(anchor="w", pady=(6, 2))

        self.road_type_menu = ctk.CTkOptionMenu(
            self._road_picker_frame,
            values=[
                "Plain Road (1)", "Crack Road (2)",
                "Drainage Road (3)", "Pothole Road (4)"
            ],
            width=180, height=28, corner_radius=6,
            font=("Segoe UI", 11),
            fg_color=ENTRY_BG, button_color=RESIZE_FG,
            button_hover_color=RESIZE_HOVER
        )
        self.road_type_menu.pack(fill="x")

        self._current_algo = "BFS"

    def _on_mode_change(self, value):
        """Handle mode segmented-button change — show/hide road picker accordingly."""
        if self.sfx:
            self.sfx.play_button_click()
        self.callbacks["set_mode"](value)

        # Show road-type picker only in Road mode with UCS selected
        if value == "Road" and self._current_algo == "UCS":
            self._road_picker_frame.pack(fill="x", pady=(2, 0))
        else:
            self._road_picker_frame.pack_forget()

    def _build_algo_card(self):
        """Algorithm selector card — dropdown menu."""
        card = self._card(self._inner)
        self._section_label(card, "🧠", "Algorithm")

        algo_inner = ctk.CTkFrame(card, fg_color="transparent")
        algo_inner.pack(fill="x", padx=10, pady=(2, 8))

        self.algo_menu = ctk.CTkOptionMenu(
            algo_inner,
            values=["BFS", "DFS", "UCS", "A* (Manhattan)", "A* (Euclidean)"],
            command=self._on_algo_change,
            font=("Segoe UI Semibold", 12), height=30, corner_radius=6,
            fg_color=ENTRY_BG, button_color=HEADER_ACCENT,
            button_hover_color="#6d28d9"
        )
        self.algo_menu.pack(fill="x")

    def _on_algo_change(self, value):
        """Handle algorithm dropdown change.

        When UCS is selected, the 'Road' mode is added to the segmented button.
        When switching away from UCS, 'Road' mode is removed and (if active)
        falls back to 'Wall' mode.
        """
        if self.sfx:
            self.sfx.play_button_click()
        self._current_algo = value

        if value == "UCS":
            # Add the Road mode option
            self.mode_switch.configure(values=["Start", "Goal", "Wall", "Road"])
        else:
            current_mode = self.mode_switch.get()
            self.mode_switch.configure(values=["Start", "Goal", "Wall"])
            if current_mode == "Road":
                # Fall back to Wall mode when leaving UCS
                self.mode_switch.set("Wall")
                self._road_picker_frame.pack_forget()
                self.callbacks["set_mode"]("Wall")

        if "algo_changed" in self.callbacks:
            self.callbacks["algo_changed"](value)

    def _build_action_card(self):
        """Action buttons card — Run, Clear, Reset."""
        card = self._card(self._inner)
        self._section_label(card, "⚡", "Actions")

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(2, 8))

        self.run_btn = ctk.CTkButton(
            btn_frame, text="▶  Run Algorithm",
            fg_color=RUN_FG, hover_color=RUN_HOVER,
            height=36, font=("Segoe UI Bold", 13), corner_radius=8,
            command=self._on_run_click
        )
        self.run_btn.pack(fill="x", pady=(0, 4))

        sub_row = ctk.CTkFrame(btn_frame, fg_color="transparent")
        sub_row.pack(fill="x")

        self.clear_btn = ctk.CTkButton(
            sub_row, text="🧹 Clear",
            fg_color=CLEAR_FG, hover_color=CLEAR_HOVER,
            height=28, font=("Segoe UI Semibold", 11), corner_radius=6,
            command=self._on_clear_click
        )
        self.clear_btn.pack(side="left", expand=True, fill="x", padx=(0, 3))

        self.reset_btn = ctk.CTkButton(
            sub_row, text="🔄 Reset",
            fg_color=RESET_FG, hover_color=RESET_HOVER,
            height=28, font=("Segoe UI Semibold", 11), corner_radius=6,
            command=self._on_reset_click
        )
        self.reset_btn.pack(side="left", expand=True, fill="x", padx=(3, 0))

    # ── Button click handlers (play SFX + delegate to callback) ──

    def _on_resize_click(self):
        """Handle Resize button press."""
        if self.sfx:
            self.sfx.play_button_click()
        self.callbacks["resize_grid"]()

    def _on_run_click(self):
        """Handle Run Algorithm button press."""
        if self.sfx:
            self.sfx.play_button_click()
        self.callbacks["run_algorithm"]()

    def _on_clear_click(self):
        """Handle Clear button press."""
        if self.sfx:
            self.sfx.play_button_click()
        self.callbacks["clear_path"]()

    def _on_reset_click(self):
        """Handle Reset button press."""
        if self.sfx:
            self.sfx.play_button_click()
        self.callbacks["reset_grid"]()

    def _build_results_card(self):
        """Results card — displays Steps, Cost, and Explored stats."""
        card = self._card(self._inner)
        self._section_label(card, "📊", "Results")

        stats = ctk.CTkFrame(card, fg_color="transparent")
        stats.pack(fill="x", padx=10, pady=(0, 8))

        self.path_length_label   = self._stat_row(stats, "Path Length", "—")
        self.total_cost_label    = self._stat_row(stats, "Cost",        "—")
        self.visited_count_label = self._stat_row(stats, "Explored",    "—")

    def _stat_row(self, parent, label, default):
        """Create a single stat row: label on the left, value on the right.

        Returns the value CTkLabel so it can be updated later.
        """
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=1)

        ctk.CTkLabel(
            row, text=f"{label}:",
            font=("Segoe UI", 11), text_color=SUBLABEL_COLOR, anchor="w"
        ).pack(side="left")

        val = ctk.CTkLabel(
            row, text=default,
            font=("Segoe UI Bold", 12), text_color=STAT_VALUE_COLOR, anchor="e"
        )
        val.pack(side="right")
        return val

    def _build_mute_toggle(self):
        """Compact sound mute/unmute toggle button with speaker icon."""
        mute_frame = ctk.CTkFrame(self._inner, fg_color="transparent")
        mute_frame.pack(fill="x", padx=2, pady=(4, 2))

        # Load speaker icons from the UI assets folder
        self._mute_icons = {}
        for name in ("mute", "unmute"):
            path = os.path.join(UI_DIR, f"{name}.png")
            if os.path.exists(path):
                img = Image.open(path).convert("RGBA")
                self._mute_icons[name] = ctk.CTkImage(
                    light_image=img, dark_image=img, size=(18, 18)
                )

        unmute_icon = self._mute_icons.get("unmute")
        self.mute_btn = ctk.CTkButton(
            mute_frame, text=" Sound On", image=unmute_icon,
            width=120, height=28,
            fg_color=MUTE_FG, hover_color=MUTE_HOVER,
            font=("Segoe UI", 11), corner_radius=6,
            anchor="center", command=self._on_mute_toggle
        )
        self.mute_btn.pack()

    def _on_mute_toggle(self):
        """Toggle mute state and update the button icon/text."""
        if not self.sfx:
            return
        is_muted = self.sfx.toggle_mute()
        if is_muted:
            icon = self._mute_icons.get("mute")
            self.mute_btn.configure(text=" Sound Off", image=icon)
        else:
            icon = self._mute_icons.get("unmute")
            self.mute_btn.configure(text=" Sound On", image=icon)

    # ═══════════════════════════════════════════════════════════
    #  PUBLIC API (read-only getters + result updates)
    # ═══════════════════════════════════════════════════════════

    def get_grid_size_input(self):
        """Return the raw text from the grid-size entry field."""
        return self.grid_size_entry.get()

    def get_selected_algo(self):
        """Return the currently selected algorithm name (e.g. 'BFS')."""
        return self.algo_menu.get()

    def get_selected_road_type(self):
        """Map the human-readable road-type dropdown value to an internal road name."""
        val = self.road_type_menu.get()
        if   "Plain"    in val: return "RoadPlain1"
        elif "Crack"    in val: return "RoadCrack"
        elif "Drainage" in val: return "RoadDrainage"
        elif "Pothole"  in val: return "RoadPothole"
        return "RoadPlain1"

    def update_results(self, path_length=None, total_cost=None, cells_explored=None):
        """Update the result stat labels with algorithm output.

        Any argument left as None will show '—' (dash).
        """
        self.path_length_label.configure(
            text=str(path_length) if path_length is not None else "—"
        )
        self.total_cost_label.configure(
            text=str(total_cost) if total_cost is not None else "—"
        )
        self.visited_count_label.configure(
            text=str(cells_explored) if cells_explored is not None else "—"
        )

    def clear_results(self):
        """Reset all result labels to the default dash ('—')."""
        self.path_length_label.configure(text="—")
        self.total_cost_label.configure(text="—")
        self.visited_count_label.configure(text="—")

    def disable_buttons(self):
        """Disable all action buttons (called during animation)."""
        self.run_btn.configure(state="disabled")
        self.clear_btn.configure(state="disabled")
        self.reset_btn.configure(state="disabled")
        self.resize_btn.configure(state="disabled")

    def enable_buttons(self):
        """Re-enable all action buttons (called after animation completes)."""
        self.run_btn.configure(state="normal")
        self.clear_btn.configure(state="normal")
        self.reset_btn.configure(state="normal")
        self.resize_btn.configure(state="normal")
