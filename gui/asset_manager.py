"""
asset_manager.py — Sprite loader and cache for the Fire Brigade Pathfinding GUI.

Loads PNG sprite sheets for buildings, fire, truck (directional), and road tiles,
resizes them to the current cell size using Lanczos resampling, and converts them
to Tk-compatible PhotoImage objects.

All PhotoImage references are held in instance dictionaries so that Python's
garbage collector does not destroy them while they are displayed on the canvas.
"""

import os
from PIL import Image, ImageTk

from gui.constants import (
    BUILDING_DIR, FIRE_DIR, TRUCK_DIR, ROAD_DIR,
    BUILDING_COUNT, FIRE_FRAME_COUNT, TRUCK_DIRECTIONS,
    ROAD_TYPES
)


class AssetManager:
    """Central image loader and cache for all game sprites.

    Attributes:
        cell_size:   Current pixel size that all sprites are resized to.
        buildings:   {index (1–16)  → PhotoImage}
        fire_frames: {frame index   → PhotoImage}
        truck:       {direction str → PhotoImage}
        roads:       {road type str → PhotoImage}
    """

    def __init__(self, cell_size):
        """Initialise the asset cache and load all sprites.

        Args:
            cell_size: The initial cell pixel size for sprite resizing.
        """
        self.cell_size   = cell_size
        self.buildings   = {}
        self.fire_frames = {}
        self.truck       = {}
        self.roads       = {}

        self.load_all(cell_size)

    # ═══════════════════════════════════════════════════════════
    #  PUBLIC API
    # ═══════════════════════════════════════════════════════════

    def load_all(self, cell_size):
        """Load and resize every asset category to *cell_size × cell_size*."""
        self.cell_size = cell_size
        self._load_buildings()
        self._load_fire()
        self._load_truck()
        self._load_roads()

    def reload(self, new_cell_size):
        """Reload all assets at a new cell size (e.g. after a grid resize)."""
        self.load_all(new_cell_size)

    # ═══════════════════════════════════════════════════════════
    #  PRIVATE LOADERS
    # ═══════════════════════════════════════════════════════════

    def _resize(self, img, size=None):
        """Resize a PIL Image to *(size × size)* and convert to PhotoImage.

        Args:
            img:  A PIL Image object.
            size: Target pixel dimension (defaults to self.cell_size).

        Returns:
            A tkinter-compatible ImageTk.PhotoImage.
        """
        s = size or self.cell_size
        img = img.resize((s, s), Image.LANCZOS)
        return ImageTk.PhotoImage(img)

    def _load_buildings(self):
        """Load building sprites B1.png through B{BUILDING_COUNT}.png."""
        self.buildings.clear()
        for i in range(1, BUILDING_COUNT + 1):
            path = os.path.join(BUILDING_DIR, f"B{i}.png")
            if os.path.exists(path):
                img = Image.open(path).convert("RGBA")
                self.buildings[i] = self._resize(img)

    def _load_fire(self):
        """Load the fire sprite (single frame: 3.png)."""
        self.fire_frames.clear()
        path = os.path.join(FIRE_DIR, "3.png")
        if os.path.exists(path):
            img = Image.open(path).convert("RGBA")
            self.fire_frames[1] = self._resize(img)

    def _load_truck(self):
        """Load directional truck sprites (Up.png, Down.png, left.png, right.png)."""
        self.truck.clear()
        for direction in TRUCK_DIRECTIONS:
            path = os.path.join(TRUCK_DIR, f"{direction}.png")
            if os.path.exists(path):
                img = Image.open(path).convert("RGBA")
                self.truck[direction] = self._resize(img)

    def _load_roads(self):
        """Load all road-type sprites defined in ROAD_TYPES."""
        self.roads.clear()
        for road_name, (filename, _weight) in ROAD_TYPES.items():
            path = os.path.join(ROAD_DIR, filename)
            if os.path.exists(path):
                img = Image.open(path).convert("RGBA")
                self.roads[road_name] = self._resize(img)
