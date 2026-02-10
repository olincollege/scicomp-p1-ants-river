import src.model as model

import pygame
from pygame._sdl2 import Window as sdlwindow
from typing import Callable

class PygameLabel:
    """
    A simple label class for displaying text on a background, centered.
    """
    def __init__(self, rect: pygame.Rect, text: str, color = None, font = None):
        self.rect = rect
        self.text = text
        self.font = font if font is not None else pygame.font.Font(None, 36)
        self.color = color if color is not None else pygame.Color('white')
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surf = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

class PygameButton(PygameLabel):
    """
    An extension of the label class that adds a callback/color change on click.
    """
    def __init__(self, rect: pygame.Rect, text: str, callback: Callable, color_inactive = None, color_active = None, color_disabled = None, disabled = False, font = None):
        super().__init__(rect, text, color_inactive, font)
        self.callback = callback
        self.color_inactive = color_inactive if color_inactive is not None else pygame.Color('lightskyblue3')
        self.color_active = color_active if color_active is not None else pygame.Color('dodgerblue2')
        self.color_disabled = color_disabled if color_disabled is not None else pygame.Color('dimgray')
        self.color = self.color_disabled if disabled else self.color_inactive
        self.disabled = disabled

    def handle_event(self, event: pygame.event.Event):
        if self.disabled:
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.color = self.color_active
                self.callback()
        elif event.type == pygame.MOUSEBUTTONUP:
            self.color = self.color_inactive
    
    def set_disabled(self, disabled: bool):
        self.disabled = disabled
        if disabled:
            self.color = self.color_disabled
        else:
            self.color = self.color_inactive

class ParamController():
    """
    Label, +, and - buttons for a single parameter.
    """

    def __init__(self, screen: pygame.Surface, world: model.AntWorld, x: float, y: float, param_name: str, setter: Callable, delta: float, initial_value: float, figs: int = 2):
        self.screen = screen
        self.param_name = param_name
        self.setter = setter
        self.delta = delta
        self.value = initial_value
        self.is_float = delta < 1
        self.figs = figs

        x_offset = screen.get_size()[1]//world.params.world_size * 256 + 20
        x_end = screen.get_size()[0] - 10
        x_width_4ths = (x_end - x_offset) / 4 - 10
        x_width_8ths = (x_end - x_offset) / 8 - 10

        label_string = f"{param_name}: {initial_value:.{self.figs}f}" if self.is_float else f"{param_name}: {int(initial_value)}"
        self.label = PygameLabel(pygame.Rect(x, y, x_width_4ths, 40), label_string, color=pygame.Color('lightgreen'))
        self.plus_button = PygameButton(pygame.Rect(x, y + 50, x_width_8ths, 40), "+", lambda: self.update_value(self.delta))
        self.minus_button = PygameButton(pygame.Rect(x + (x_end - x_offset) / 8, y + 50, x_width_8ths, 40), "-", lambda: self.update_value(-self.delta))

    def update_value(self, delta: float):
        self.value = max(0, self.value + delta) # prevent negative values
        self.setter(self.value)
        if self.is_float:
            self.label.text = f"{self.param_name}: {self.value:.{self.figs}f}"
        else:
            self.label.text = f"{self.param_name}: {int(self.value)}"
    
    def draw(self):
        self.label.draw(self.screen)
        self.plus_button.draw(self.screen)
        self.minus_button.draw(self.screen)
    
    def handle_event(self, event: pygame.event.Event):
        self.plus_button.handle_event(event)
        self.minus_button.handle_event(event)

class WorldControls:
    """
    Helper class to render the controls for the ant world.
    """

    def __init__(self, screen: pygame.Surface, world: model.AntWorld):
        self.screen = screen
        self.world = world
        self.buttons = []
        self.labels = []
        self.param_controllers = []
        self.is_paused = True
        self.fps = 30
        self.show_ants = True

        self.layout_gui()

    def layout_gui(self):
        self.labels = []
        self.buttons = []
        self.param_controllers = []
        
        # the GUI layout gets a bit messy here 
        # x_offset is the starting x value of the controls, to the right of the world visualization
        # x_end is the ending x value of the controls
        # there's a default padding of 20 pixels between controls
        # xs_4ths and x_width_4ths, etc. are helpers for 4/8 controls in a row
        x_offset = self.screen.get_size()[1]//self.world.params.world_size *256 + 20
        x_end = self.screen.get_size()[0] - 10


        xs_4ths = [(x_end - x_offset) * i / 4 + x_offset for i in range(5)]
        x_width_4ths = (x_end - x_offset) / 4 - 10
        xs_8ths = [(x_end - x_offset) * i / 8 + x_offset for i in range(9)]
        x_width_8ths = (x_end - x_offset) / 8 - 10

        # Title
        self.labels.append(PygameLabel(pygame.Rect(x_offset, 10, x_end - x_offset - 10, 40), "Ant Simulator", color=pygame.Color('salmon1')))

        # World status
        self.ts_label = PygameLabel(pygame.Rect(x_offset, 60, (x_end - x_offset) / 2 - 10, 40), f"Time step: {self.world.timestep}", color=pygame.Color('gray'))
        self.labels.append(self.ts_label)
        self.fps_label = PygameLabel(pygame.Rect(xs_4ths[2], 60, (x_end - x_offset) / 2 - 10, 40), f"FPS: {self.fps}", color=pygame.Color('gray'))
        self.labels.append(self.fps_label)
        
        # World controls
        self.pause_button = PygameButton(pygame.Rect(x_offset, 110, x_width_4ths, 40), "Play", self.toggle_pause)
        self.buttons.append(self.pause_button)
        self.step_button = PygameButton(pygame.Rect(xs_4ths[1], 110, x_width_4ths, 40), "Step", self.step_forward)
        self.buttons.append(self.step_button)
        self.fps_up_button = PygameButton(pygame.Rect(xs_4ths[2], 110, x_width_4ths, 40), "FPS+", self.increase_fps)
        self.buttons.append(self.fps_up_button)
        self.fps_down_button = PygameButton(pygame.Rect(xs_4ths[3], 110, x_width_4ths, 40), "FPS-", self.decrease_fps)
        self.buttons.append(self.fps_down_button)
        self.reset_button = PygameButton(pygame.Rect(x_offset, 160, (x_end - x_offset) / 2 - 10, 40), "Reset", self.reset_world)
        self.buttons.append(self.reset_button)
        self.toggle_ants_button = PygameButton(pygame.Rect(xs_4ths[2], 160, (x_end - x_offset) / 2 - 10, 40), f"Toggle ants", lambda: setattr(self, 'show_ants', not self.show_ants))
        self.buttons.append(self.toggle_ants_button)

        # metrics: Population, F/L
        metrics_y = 230
        self.pop_label = PygameLabel(pygame.Rect(x_offset, metrics_y, (x_end - x_offset) / 2 - 10, 40), f"Population: {len(self.world.ants)}", color=pygame.Color('gray'))
        self.labels.append(self.pop_label)
        ants_following = sum([ant.status == model.AntStatus.FOLLOWING for ant in self.world.ants])
        ants_lost = sum([ant.status == model.AntStatus.LOST for ant in self.world.ants])
        fl_ratio = ants_following / ants_lost if ants_lost > 0 else 0
        self.fl_label = PygameLabel(pygame.Rect(xs_4ths[2], metrics_y, (x_end - x_offset) / 2 - 10, 40), f"F/L: {ants_following}/{ants_lost} = {fl_ratio:.1f}", color=pygame.Color('gray'))
        self.labels.append(self.fl_label)

        # Parameter values and controls. tau, phi_low, C_s, delta_phi, and turning kernel.
        # the /256 is to make the param vals match with those in the paper
        param_y = 300
        self.tau_pc = ParamController(self.screen, self.world, xs_8ths[0], param_y, 'tau', lambda val: setattr(self.world.params, 'tau', val), 1, self.world.params.tau)
        self.param_controllers.append(self.tau_pc)
        self.phi_low_pc = ParamController(self.screen, self.world, xs_8ths[2], param_y, 'phi_low', lambda val: setattr(self.world.params, 'phi_low', val/256), 1, self.world.params.phi_low*256)
        self.param_controllers.append(self.phi_low_pc)
        self.cs_pc = ParamController(self.screen, self.world, xs_8ths[4], param_y, 'C_s', lambda val: setattr(self.world.params, 'C_s', val), 1, self.world.params.C_s)
        self.param_controllers.append(self.cs_pc)
        self.dphi_pc = ParamController(self.screen, self.world, xs_8ths[6], param_y, 'delta_phi', lambda val: setattr(self.world.params, 'delta_phi', val/256), 1, self.world.params.delta_phi*256)
        self.param_controllers.append(self.dphi_pc)

        # Turning kernel controls
        # all but 180 are *2 b/c the non-180 probs are split across left and right turns
        tk_param_y = param_y + 100
        self.tk_45_pc = ParamController(self.screen, self.world, xs_8ths[0], tk_param_y, 'B.45', lambda val: self.set_B(45, val/2), 0.01, self.world.params.B[45]*2, figs=3)
        self.param_controllers.append(self.tk_45_pc)
        self.tk_90_pc = ParamController(self.screen, self.world, xs_8ths[2], tk_param_y, 'B.90', lambda val: self.set_B(90, val/2), 0.001, self.world.params.B[90]*2, figs=3)
        self.param_controllers.append(self.tk_90_pc)
        self.tk_135_pc = ParamController(self.screen, self.world, xs_8ths[4], tk_param_y, 'B.135', lambda val: self.set_B(135, val/2), 0.001, self.world.params.B[135]*2, figs=3)
        self.param_controllers.append(self.tk_135_pc)
        self.tk_180_pc = ParamController(self.screen, self.world, xs_8ths[6], tk_param_y, 'B.180', lambda val: self.set_B(180, val), 0.001, self.world.params.B[180], figs=3)
        self.param_controllers.append(self.tk_180_pc)
    
    def set_B(self, angle: int, value: float):
        self.world.params.B[angle] = value
        self.world.params.B[-angle] = value

    def reset_world(self):
        self.world.reset()
        self.ts_label.text = f"Time step: {self.world.timestep}"
        self.is_paused = True
        self.pause_button.text = "Play"

    def increase_fps(self):
        self.fps += 10 if self.fps >= 10 else 1
        self.fps = min(60, self.fps)
        self.fps_label.text = f"FPS: {self.fps}"

        self.fps_down_button.set_disabled(False)
        if self.fps >= 60:
            self.fps_up_button.set_disabled(True)

    def decrease_fps(self):
        self.fps -= 10 if self.fps > 10 else 1
        self.fps = max(1, self.fps)
        self.fps_label.text = f"FPS: {self.fps}"
        self.fps_up_button.set_disabled(False)
        if self.fps <= 1:
            self.fps_down_button.set_disabled(True)

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        self.pause_button.text = "Play" if self.is_paused else "Pause"
    
    def step_forward(self):
        if self.is_paused:
            self.world.step()
    
    def draw(self):
        # update metric labels
        self.ts_label.text = f"Time step: {self.world.timestep}"
        self.pop_label.text = f"Population: {len(self.world.ants)}"
        ants_following = sum([ant.status == model.AntStatus.FOLLOWING for ant in self.world.ants])
        ants_lost = sum([ant.status == model.AntStatus.LOST for ant in self.world.ants])
        fl_ratio = ants_following / ants_lost if ants_lost > 0 else 0
        self.fl_label.text = f"F/L: {ants_following}/{ants_lost} = {fl_ratio:.1f}"

        # draw everything
        for button in self.buttons:
            button.draw(self.screen)
        for label in self.labels:
            label.draw(self.screen)
        for pc in self.param_controllers:
            pc.draw()

    def handle_event(self, event: pygame.event.Event):
        for button in self.buttons:
            button.handle_event(event)
        for pc in self.param_controllers:
            pc.handle_event(event)
    

class WorldRenderer:
    """
    Helper class to render the world itself.
    """
    def __init__(self, screen: pygame.Surface, world: model.AntWorld):
        self.screen = screen
        self.world = world
        self.layout_gui()
    
    def lattice_to_pixels(self) -> None:
        for node in self.world.lattice.nodes:
            x, y = node.position
            intensity = min(255, node.pheromone_level * 2)
            self.heatmap_surface.set_at((x, y), (intensity, 0, 0))
    
    def ants_to_pixels(self) -> None:
        for ant in self.world.ants:
            x, y = ant.current_node.position
            self.heatmap_surface.set_at((x, y), (255, 255, 255))

    def draw(self, show_ants = True):
        self.lattice_to_pixels()
        if show_ants:
            self.ants_to_pixels()
        pygame.draw.rect(self.screen, (255, 255, 255), (0, 0, self.world.params.world_size * self.scaling_factor + 2, self.world.params.world_size * self.scaling_factor + 2))
        self.screen.blit(pygame.transform.scale_by(self.heatmap_surface, self.scaling_factor), (1, 1))

    def layout_gui(self):
        self.heatmap_surface = pygame.Surface((self.world.params.world_size, self.world.params.world_size))
        self.scaling_factor = self.screen.get_size()[1]//self.world.params.world_size

def main():
    pygame.init()
    screen = pygame.display.set_mode((1920, 1024+2), pygame.RESIZABLE)
    pygame.display.set_caption("Ant Simulator")
    sdlwindow.from_display_module().maximize()
    clock = pygame.time.Clock()
    running = True
    params = model.WorldParams.default_large()
    world = model.AntWorld(params)
    controls = WorldControls(screen, world)
    renderer = WorldRenderer(screen, world)
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                renderer.screen = screen
                controls.screen = screen
                renderer.layout_gui()
                controls.layout_gui()
            else:
                controls.handle_event(event)
        if not controls.is_paused:
            world.step()
            if world.timestep % 10 == 0:
                print(f"Time step: {world.timestep}")
        renderer.draw(show_ants=controls.show_ants)
        controls.draw()
        pygame.display.flip()

        clock.tick(controls.fps)
    pygame.quit()

if __name__ == "__main__":
    main()