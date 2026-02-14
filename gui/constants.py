"""
constants.py — Centralised configuration for the Fire Brigade Pathfinding GUI.

All tuneable values live here: file paths, window settings, grid dimensions,
colour palettes, road weights, asset counts, and animation timing.
Importing modules should never hard-code these values.
"""

import os

# ──────────────────────────── PATHS ────────────────────────────
# BASE_DIR points to the project root (one level above gui/)
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET_DIR  = os.path.join(BASE_DIR, "assets")             # All visual/audio resources

BUILDING_DIR = os.path.join(ASSET_DIR, "Buildings")       # B1.png – B16.png
FIRE_DIR     = os.path.join(ASSET_DIR, "Fire")             # Fire sprite frames
TRUCK_DIR    = os.path.join(ASSET_DIR, "FireBrigadier")    # Up/Down/left/right.png
ROAD_DIR     = os.path.join(ASSET_DIR, "Roads")            # Road tile variants
SOUND_DIR    = os.path.join(ASSET_DIR, "sounds")           # Sound effects (mp3)
UI_DIR       = os.path.join(ASSET_DIR, "UI")               # Mute/unmute icons
ICON_DIR     = os.path.join(ASSET_DIR, "AppIcon")          # app_icon.ico

# ──────────────────────────── WINDOW ───────────────────────────
WINDOW_TITLE   = "🚒 Fire Brigade Pathfinding Visualizer"
WINDOW_MINSIZE = (1000, 600)           # Minimum width × height

# ──────────────────────────── GRID DEFAULTS ────────────────────
DEFAULT_ROWS      = 10
DEFAULT_COLS      = 10
DEFAULT_CELL_SIZE = 25                 # Only used until first redraw
MIN_GRID_SIZE     = 10                 # Smallest grid the user can request
MAX_GRID_SIZE     = 50                 # Largest  grid the user can request
MIN_CELL_SIZE     = 10                 # Absolute minimum cell pixel size
MAX_CELL_SIZE     = 60                 # Absolute maximum cell pixel size


def get_cell_size(grid_size):
    """Return the cell pixel-size for a given grid dimension.

    Larger grids get smaller cells so the grid fits the canvas.
    """
    if   grid_size <= 20: return 25
    elif grid_size <= 30: return 20
    elif grid_size <= 40: return 16
    else:                 return 13

# ──────────────────────────── COLOURS ──────────────────────────
# Canvas area
CANVAS_BG  = "#1a1a2e"                # Dark navy canvas background
GRID_LINE  = "#2a2a3e"                # Subtle grid line colour

# Per-algorithm overlay colours (exploration phase)
EXPLORE_COLORS = {
    "BFS": "#fab005",                  # Amber
    "DFS": "#9775fa",                  # Violet
    "UCS": "#fd7e14",                  # Orange
}

# Per-algorithm overlay colours (final path)
PATH_COLORS = {
    "BFS": "#15aabf",                  # Cyan
    "DFS": "#f06595",                  # Magenta
    "UCS": "#94d82d",                  # Lime green
}

# ──────────────────────────── ROAD WEIGHTS (UCS) ───────────────
# Mapping: road type name → (sprite filename, traversal cost)
ROAD_TYPES = {
    "RoadPlain1":   ("RoadPlain1.png",   1),
    "RoadPlain2":   ("RoadPlain2.png",   1),
    "RoadCrack":    ("RoadCrack.png",    2),
    "RoadDrainage": ("RoadDrainage.png", 3),
    "RoadPothole":  ("RoadPothole.png",  4),
}

PLAIN_ROADS = ["RoadPlain1", "RoadPlain2"]   # Default pool (BFS / DFS)
ALL_ROADS   = list(ROAD_TYPES.keys())        # Full pool (UCS)

# ──────────────────────────── ASSETS ───────────────────────────
BUILDING_COUNT   = 16                  # B1.png through B16.png
FIRE_FRAME_COUNT = 1                   # Single fire sprite (3.png)
TRUCK_DIRECTIONS = ["Up", "Down", "left", "right"]

# ──────────────────────────── ANIMATION ────────────────────────
TRUCK_STEP_MS        = 80             # Milliseconds between truck steps
TRUCK_GRID_THRESHOLD = 30             # Grids larger than this skip truck animation
