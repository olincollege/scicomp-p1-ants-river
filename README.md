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

## Comparison to Original
Paper's figure 3(b) at t=1500|This model with same parameters
---|---
![A screenshot of Figure 3(b) from Watmough and Edelstein-Keshet, 1995.](/docs-pics/their-fig-3b.png)|![A screenshot from this software, run with the same parameters as the paper](/docs-pics/my-fig-3b.png)

Qualitatively, this model has trails that are more numerous and winding than the original paper. They reach less far from the center, but are denser near the center. Quantitatively, the ant population is much higher for this model than in the paper (1033 vs 485). This pattern is likely due to the paper's straighter paths leading more ants off the borders of the lattice. This points to a possible difference in the way the turning kernel is implemented, such that the paper's ants are less likely to make turns. Interestingly, the paper notes a followers/lost ant ratio (F/L ratio) of only 4.4, while this model's is closer to 40. In other words, in this model, there are fewer ants leading trails, despite there being a greater number of trails created. This could be a result of a possible difference in the way fidelity is implemented, with this paper's ants being less likely to follow trails for an extended length of time.

## Software Architecture
The core model is implemented in `src/model.py`. The model is implemented in a fairly object-oriented way, with separate `Ant`, `Lattice`, `AntWorld`, etc. This makes it simpler to reason about where behavior is implemented as well as allowing easier type-checking for correctness. It was written to allow some extent of flexibility, e.g. very few numbers are hardcoded, even implied ones like pheromone evaporation rates. However, some assumptions made it into the final model, like the ant algorithms assuming each node has 8 neighbors.

`model.py` is verified by Pytest with `src/test_model.py` (`uv run pytest`). This file checks the behavior of everything from the lattice builder to the entire simulation runner, and caught several bugs during development.

The various `src/interface_*.py` files were created to explore several approaches to a live control interface. `interface_toolbar_old.py` and `interface_matplotlib.py` were the first interfaces written, and attempted to use Matplotlib as the graphics framework for its built-in graphing and widget support. However, Matplotlib did not have the rendering performance necessary for a smooth live simulation, so Pygame was used in the final interface, implemented in `interface_pygame.py`. Because Pygame does not come with widgets, most of that file is just defining widgets and laying them out, then calling into `model.py` for the actual functionality.

`main.py` simply calls into `src/interface_pygame.py`.

`TASK_TABLE.md` and `PLANNING.md` are snapshots of my thinking at the start of this project. `TASK_TABLE` laid out an estimated timeline, and `PLANNING` was the initial brainstorming for the data model.