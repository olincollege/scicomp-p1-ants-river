"""
An experiment for using the Matplotlib toolbar to hold buttons for the interface
"""
import model

import matplotlib.pyplot as plt
from matplotlib.backend_tools import ToolBase, ToolToggleBase
from matplotlib.backend_managers import ToolEvent
import time
import math

plt.rcParams['toolbar'] = 'toolmanager'

class PauseTool(ToolToggleBase):
    """A tool to pause and unpause the simulation."""
    description = 'Pause/Unpause Simulation'
    default_keymap = 'p'
    paused: bool
    default_toggled = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.paused = True

    def enable(self, event: ToolEvent | None = None):
        self.paused = True

    def disable(self, event: ToolEvent | None = None):
        self.paused = False

def lattice_to_heatmap(lattice: model.Lattice) -> list[list[float]]:
    size = int(math.sqrt(len(lattice.nodes)))
    heatmap = [[0.0 for _ in range(size)] for _ in range(size)]
    for node in lattice.nodes:
        x, y = node.position
        heatmap[y][x] = node.pheromone_level
    return heatmap

if __name__ == "__main__":
    params = model.WorldParams.default_large()
    world = model.AntWorld(params)

    base_plot = plt.figure()
    assert base_plot.canvas.manager is not None and base_plot.canvas.manager.toolmanager is not None
    base_plot.canvas.manager.toolmanager.add_tool('Pause', PauseTool)
    base_plot.canvas.manager.toolbar.add_tool('Pause', 'navigation')
    pause_tool = base_plot.canvas.manager.toolmanager.get_tool('Pause')
    assert pause_tool is not None
    heatmap_ax = base_plot.add_subplot(1, 1, 1)
    heatmap_data = lattice_to_heatmap(world.lattice)
    heatmap = heatmap_ax.imshow(heatmap_data, cmap='hot', interpolation='nearest', vmin=0, vmax=params.C_s*5)
    base_plot.colorbar(heatmap)
    plt.ion()
    plt.show()
    for step in range(1000):
        start_time = time.monotonic()
        world.step()
        heatmap_data = lattice_to_heatmap(world.lattice)
        heatmap.set_array(heatmap_data)
        end_time = time.monotonic()
        print(f"Step {step} took {end_time - start_time:.4f} seconds.")
        plt.pause(0.01)
        while pause_tool.paused:
            plt.pause(0.1)
        