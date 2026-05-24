<div align="center">

# 🚒 Fire Brigade Pathfinding Visualizer

*Place a fire truck. Start a fire. Watch four algorithms race to put it out.*

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python)](https://python.org/)
[![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-blue?style=flat-square)]()
[![Course](https://img.shields.io/badge/Course-Artificial%20Intelligence%20%40%20FAST--NUCES-green?style=flat-square)]()

![App Main Screen](<img width="1920" height="1032" alt="Screenshot 2026-05-25 015909" src="https://github.com/user-attachments/assets/13645506-f8df-426d-92d4-f2093b1094a1" />)

</div>

---

An interactive grid-based visualizer for four classic AI search algorithms — BFS, DFS, UCS, and A\*. Paint a city, pick an algorithm, and watch it explore in real time. The fire truck animates along the found path, faces the correct direction as it moves, and the fire blinks out on arrival — with a full sound design to match (siren, fire crackling, extinguisher).

---

## Algorithms

Every data structure is implemented from scratch — no `deque`, no `heapq`, nothing from Python's standard collections. The `data_structures/` package contains a hand-rolled array-based Queue, Stack, and binary MinHeap with `O(log n)` decrease-key via a `pos[]` index array.

| Algorithm | Data Structure | Optimal? | Notes |
|---|---|---|---|
| **BFS** | Queue (FIFO) | ✅ Unweighted | Explores level by level |
| **DFS** | Stack (LIFO) | ❌ | Deep-first, no path guarantee |
| **UCS** | MinHeap | ✅ Weighted | Expands lowest-cost cell first |
| **A\*** | MinHeap + heuristic | ✅ Admissible h | Manhattan or Euclidean, selectable |

A\* uses a `(f, -g)` tuple as the heap priority — the negative g-value breaks ties in favour of cells closer to the goal, reducing unnecessary expansion.

---

### BFS — Breadth-First Search

Explores level by level, guaranteeing the shortest path on an unweighted grid. Without obstacles the frontier expands outward as a perfect uniform ring — one of the most visually recognisable exploration patterns in search.

<p align="center">
  <img width="1920" height="1032" alt="Screenshot 2026-05-25 020244" src="https://github.com/user-attachments/assets/b9f290e1-4705-45e9-ba40-96cc10c24619" />
  <img width="1920" height="1032" alt="Screenshot 2026-05-25 020532" src="https://github.com/user-attachments/assets/a16548f4-cbf4-454c-974e-fd656adde2b5" />
  <br>
  <sub>Left: natural ring expansion with no obstacles &nbsp;·&nbsp; Right: navigating a blocked city layout</sub>
</p>

---

### DFS — Depth-First Search

Dives as deep as possible along one branch before backtracking. Without obstacles the contrast with BFS is immediate — instead of a uniform ring, DFS cuts one deep corridor before exploring anything else. Does not guarantee the shortest path.

<p align="center">
  <img width="1920" height="1032" alt="Screenshot 2026-05-25 020259" src="https://github.com/user-attachments/assets/92449551-d9ee-41cd-9744-37d1bb2ddab1" />
  <img width="1920" height="1032" alt="Screenshot 2026-05-25 020542" src="https://github.com/user-attachments/assets/99741990-17a9-4c43-88fe-d8bea43c4ef8" />
  <br>
  <sub>Left: deep single-branch exploration &nbsp;·&nbsp; Right: backtracking through obstacles</sub>
</p>

---

### UCS — Uniform-Cost Search

Expands the cell with the lowest accumulated cost first using a MinHeap. The only algorithm that uses weighted roads — and the weight awareness is real: place expensive road tiles on the obvious shortest path and UCS actively reroutes to a longer but cheaper alternative.

**Road types and their step costs:**

| Road Type | Cost |
|---|---|
| Plain Road | 1 |
| Crack Road | 2 |
| Drainage Road | 3 |
| Pothole Road | 4 |

The two screenshots below use the **same obstacle layout** — only the road type changes. In the first, all roads are plain (cost 1) so UCS takes the direct path through. In the second, drainage roads (cost 3) are painted along that same path — UCS recalculates and takes a longer route because it is cheaper overall.

<p align="center">
  <img width="1920" height="1032" alt="Screenshot 2026-05-25 020619" src="https://github.com/user-attachments/assets/ee5ecf88-9f05-4019-b93f-3a72aa739da3" />
  <img width="1920" height="1032" alt="Screenshot 2026-05-25 020641" src="https://github.com/user-attachments/assets/ee901931-b234-42fd-b642-d27522cc802e" />
  <br>
  <sub>Left: plain roads — direct path taken &nbsp;·&nbsp; Right: drainage roads on the same path — UCS reroutes to a cheaper alternative</sub>
</p>

---

### A* — Heuristic Search

Combines actual cost from start `g` with a heuristic estimate to goal `h`, expanding in order of `f = g + h`. Explores far fewer cells than UCS while still guaranteeing the optimal path. Two heuristics are selectable from the sidebar — the difference in explored area is visible when run on the same grid.

- **Manhattan** — `|Δr| + |Δc|` — tighter bound, explores less, preferred for 4-directional grids
- **Euclidean** — `√(Δr² + Δc²)` — slightly looser, explores marginally more cells

<p align="center">
  <img width="1920" height="1032" alt="Screenshot 2026-05-25 020342" src="https://github.com/user-attachments/assets/9deed4e5-05ab-4aaa-9837-53bf91839b76" />
  <img width="1920" height="1032" alt="Screenshot 2026-05-25 020655" src="https://github.com/user-attachments/assets/4bb26371-ddd6-461d-940d-6eea0f0be372" />
  <br>
  <sub>Left: no obstacles — narrow focused beam directly toward the goal &nbsp;·&nbsp; Right: with obstacles</sub>
</p>

<p align="center">
  <img width="1920" height="1032" alt="Screenshot 2026-05-25 020353" src="https://github.com/user-attachments/assets/cc240bd4-2339-46c1-a674-714e7d7fbee8" />
  <img width="1920" height="1032" alt="Screenshot 2026-05-25 020705" src="https://github.com/user-attachments/assets/3f14fe18-b197-4710-bacd-6344895bff1c" />
  <br>
  <sub>Left: Manhattan heuristic &nbsp;·&nbsp; Right: Euclidean heuristic — same grid, subtle difference in explored cells</sub>
</p>

---

## Same Grid, All Four Algorithms

The same environment run through all four — the exploration patterns make the algorithmic differences immediately obvious.

<p align="center">
  <img width="1920" height="1032" alt="Screenshot 2026-05-25 020717" src="https://github.com/user-attachments/assets/5bc5e9e8-45d8-40a4-a41f-03dc6095bd99" />
  <br>
  <sub>The shared environment before running any algorithm</sub>
</p>

---

## Code Structure

```
├── Main.py
├── algorithms/
│   ├── algorithms.py       # BFS, DFS, UCS, A* implementations
│   └── cells.py            # cell, WightedCell, UniformWeightedCell
├── data_structures/
│   └── data_structures.py  # Queue, Stack, MinHeap — all from scratch
└── gui/
    ├── app.py              # Main application window
    ├── grid_canvas.py      # Grid rendering and interaction
    ├── sidebar.py          # Controls panel
    ├── animations.py       # Exploration, path, and truck movement phases
    ├── sound_manager.py    # Siren, fire crackling, extinguisher SFX
    └── asset_manager.py    # Sprite and road tile loading
```

The algorithm logic operates on a separate `work_grid` of cell objects — completely decoupled from the GUI. Algorithms return a `visited_history` array and final path; the GUI animates from those alone.

---

## Getting Started

```bash
pip install customtkinter pillow pygame
python Main.py
```

1. Select **Start** → place the fire truck
2. Select **Goal** → place the fire
3. Select **Wall** → paint buildings
4. For UCS: paint road types to set edge weights
5. Pick an algorithm → **Run Algorithm**

---

## Author

**Sohaib Saeed** — [@aka-sohaib](https://github.com/aka-sohaib)

---

<div align="center">
<sub>FAST-NUCES · Artificial Intelligence · Semester 4</sub>
</div>
