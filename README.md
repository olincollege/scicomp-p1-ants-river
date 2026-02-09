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