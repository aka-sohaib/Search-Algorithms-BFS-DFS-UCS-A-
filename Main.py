"""
Main.py — Entry point for the Fire Brigade Pathfinding Visualizer.

Usage:
    python Main.py

Launches the interactive GUI where users can build a city grid, place a
fire truck (start) and fire (goal), then run BFS / DFS / UCS to visualise
how the truck navigates to extinguish the fire.
"""

from gui.app import AIVisualizer

if __name__ == "__main__":
    app = AIVisualizer()
    app.mainloop()