import model

import matplotlib.pyplot as plt
from matplotlib import colors, widgets
from matplotlib.backend_bases import Event
import matplotlib.style as mplstyle
import matplotlib
import time
import math
import functools

def lattice_to_heatmap(lattice: model.Lattice) -> list[list[float]]:
    size = int(math.sqrt(len(lattice.nodes)))
    heatmap = [[0.0 for _ in range(size)] for _ in range(size)]
    for node in lattice.nodes:
        x, y = node.position
        heatmap[y][x] = node.pheromone_level
    return heatmap

def ants_to_scatter(ants: list[model.Ant]) -> tuple[list[int], list[int], list[str]]:
    xs = []
    ys = []
    colors = []
    for ant in ants:
        x, y = ant.current_node.position
        color = 'blue' if ant.status == model.AntStatus.LOST else 'red'
        xs.append(x)
        ys.append(y)
        colors.append(color)
    return xs, ys, colors

def update_world(world: model.AntWorld, scatter, heatmap, heatmap_ax, steps_per_frame: int):
    start_time = time.monotonic()
    for _ in range(steps_per_frame):
        world.step()
    heatmap_data = lattice_to_heatmap(world.lattice)
    heatmap.set_array(heatmap_data)
    scatter_data_x, scatter_data_y, scatter_colors = ants_to_scatter(world.ants)
    scatter.set_offsets(list(zip(scatter_data_x, scatter_data_y)))
    scatter.set_color(scatter_colors)
    heatmap.axes.set_title(f'Ant Colony Simulation (t={world.timestep})')
    end_time = time.monotonic()
    print(f"{steps_per_frame} step(s) to {world.timestep} ran at {(steps_per_frame) / (end_time - start_time):.2f} Hz.")

class IfaceState:
    running: bool = True
    paused: bool = True
    steps_per_frame: int = 1

    def update_paused(self, pause_button: widgets.Button, event: Event):
        self.paused = not self.paused
        pause_button.label.set_text('Pause' if not self.paused else 'Play')
    
    def update_spf(self, new_spf: float):
        self.steps_per_frame = int(new_spf)
    
    def stop_running(self, event: Event):
        self.running = False

if __name__ == "__main__":
    print(f"Rendering with {matplotlib.get_backend()}")
    mplstyle.use('fast')
    params = model.WorldParams.default_large()
    params.world_size = 256
    params.phi_low = 230/256
    world = model.AntWorld(params)
    base_plot = plt.figure()
    heatmap_ax = base_plot.add_axes((0, 0.05, 1, 0.9), projection=None, polar=False)
    heatmap_data = lattice_to_heatmap(world.lattice)
    scatter_data_x, scatter_data_y, scatter_colors = ants_to_scatter(world.ants)
    scatter = heatmap_ax.scatter(scatter_data_x, scatter_data_y, c=scatter_colors, s=3)
    heatmap = heatmap_ax.imshow(heatmap_data, cmap='Greys', interpolation='nearest', norm=colors.LogNorm(vmin=0.1, vmax=100))
    base_plot.colorbar(heatmap)
    lost_patch = plt.Line2D([0], [0], marker='o', color='w', label='Lost/Exploring Ant', markerfacecolor='blue', markersize=5)
    found_patch = plt.Line2D([0], [0], marker='o', color='w', label='Following Ant', markerfacecolor='red', markersize=5)
    heatmap_ax.legend(handles=[lost_patch, found_patch], loc='upper right')
    heatmap_ax.set_title('Ant Colony Simulation (t=0)')

    state = IfaceState()
    pause_button = widgets.Button(base_plot.add_axes((0.05, 0.9, 0.1, 0.05)), 'Play')
    pause_button.on_clicked(functools.partial(state.update_paused, pause_button))

    spf_slider = widgets.Slider(base_plot.add_axes((0.05, 0.7, 0.2, 0.05)), 'Steps/Frame', valmin=1, valmax=100, valinit=1, valstep=1)
    spf_slider.on_changed(state.update_spf)

    base_plot.canvas.mpl_connect('close_event', state.stop_running)
    plt.ion()
    plt.show()
    while state.running:
        update_world(world, scatter, heatmap, heatmap_ax, state.steps_per_frame)
        plt.pause(0.001)
        while state.paused and state.running:
            plt.pause(0.1)