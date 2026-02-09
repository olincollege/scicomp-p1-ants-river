# scicomp-p1-ants
Ant simulation project for Scientific Computing SP26, seeking to replicate Watmough and Edelstein-Keshet, 1995.

![Screenshot of the interface](/docs-pics/full-iface.png)

## Usage (with `uv`)
[`uv`](https://docs.astral.sh/uv/) is an incredible Python package manager. If you have it installed, simply run `uv python -B run main.py` and the program will launch with all dependencies being automatically installed.

## Usage (without `uv`)
If you don't have `uv` installed and don't want to use it:
0. Make sure you have at least Python 3.13.
1. Set up a venv to install dependencies into.
2. `pip install -r requirements.txt`
3. `python -B main.py`

## Interface
On the left is the ant world. Ants are represented as white dots and pheromone levels are represented as a red heatmap. 

On the right are the various controls. The top half of the controls are for the simulation state and the bottom half adjust simulation parameters. Between these two sections are metrics for the current ant population and the ratio between ants currently following a trail and ants currently lost.

## Troubleshooting
If the simulation crashes either immediately or after the first few steps, this is due to a bug related to Pygame and the loading of `.pyc` files. Running Python with the `-B` flag should prevent this, but if it does not, try clearing the venv (`uv venv --clear`/`uv clean`) and reinstalling. If _this_ does not resolve things, please get in touch with me - this is a pervasive bug and more people reproducing it is very helpful.