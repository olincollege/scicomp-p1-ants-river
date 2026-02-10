# scicomp-p1-ants
Ant simulation project for Scientific Computing SP26, seeking to replicate [Watmough and Edelstein-Keshet, 1995](https://personal.math.ubc.ca/~keshet/pubs/JamesAnts.pdf).

![Screenshot of the interface](/docs-pics/full-iface.png)

## Usage (with `uv`)
[`uv`](https://docs.astral.sh/uv/) is an incredible Python package manager. If you have it installed, simply run `uv run python main.py` and the program will launch with all dependencies being automatically installed.

## Usage (without `uv`)
If you don't have `uv` installed and don't want to use it:
0. Make sure you have at least Python 3.13.
1. Set up a venv to install dependencies into.
2. `pip install -r requirements.txt`
3. `python main.py`

## Interface
On the left is the ant world. Ants are represented as white dots and pheromone levels are represented as a red heatmap. 

On the right are the various controls. The top half of the controls are for the simulation state and the bottom half adjust simulation parameters. Between these two sections are metrics for the current ant population and the ratio between ants currently following a trail and ants currently lost.

parameter name|effect
---|---
tau|Controls rate of pheromone deposition per ant
phi_low|Controls minimum chance of ants staying on a trail they're following
C_s|Controls at what level of pheromone the ant's antennae saturate
delta_phi|Controls if ants are more likely to stay on stronger trails
B.45-B.180|Controls how likely the ants are to turn various amounts

## Software Architecture
The core model is implemented in `src/model.py`. The model is implemented in a fairly object-oriented way, with separate `Ant`, `Lattice`, `AntWorld`, etc. This makes it simpler to reason about where behavior is implemented as well as allowing easier type-checking for correctness. It was written to allow some extent of flexibility, e.g. very few numbers are hardcoded, even implied ones like pheromone evaporation rates. However, some assumptions made it into the final model, like the ant algorithms assuming each node has 8 neighbors.

`model.py` is verified by Pytest with `src/test_model.py` (`uv run pytest`). This file checks the behavior of everything from the lattice builder to the entire simulation runner, and caught several bugs during development.

The various `src/interface_*.py` files were created to explore several approaches to a live control interface. `interface_toolbar_old.py` and `interface_matplotlib.py` were the first interfaces written, and attempted to use Matplotlib as the graphics framework for its built-in graphing and widget support. However, Matplotlib did not have the rendering performance necessary for a smooth live simulation, so Pygame was used in the final interface, implemented in `interface_pygame.py`. Because Pygame does not come with widgets, most of that file is just defining widgets and laying them out, then calling into `model.py` for the actual functionality.

`main.py` simply calls into `src/interface_pygame.py`.

`TASK_TABLE.md` and `PLANNING.md` are snapshots of my thinking at the start of this project. `TASK_TABLE` laid out an estimated timeline, and `PLANNING` was the initial brainstorming for the data model.