import model

import pygame
import math
from typing import Callable

class PygameButton:
    def __init__(self, rect: pygame.Rect, text: str, callback: Callable | None = None):
        self.rect = rect
        self.text = text
        self.callback = callback
        self.font = pygame.font.Font(None, 36)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.inert = self.callback is None

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surf = self.font.render(self.text, True, (0, 0, 0))
        screen.blit(text_surf, (self.rect.x + 5, self.rect.y + 5))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if not self.inert:
                    self.color = self.color_active
                if self.callback:
                    self.callback()
        elif event.type == pygame.MOUSEBUTTONUP:
            self.color = self.color_inactive

def lattice_to_pixels(lattice: model.Lattice, surf: pygame.Surface) -> None:
    size = int(math.sqrt(len(lattice.nodes)))
    for node in lattice.nodes:
        x, y = node.position
        intensity = min(255, node.pheromone_level * 2)
        surf.set_at((x, y), (intensity, 0, 0))

class WorldControls:
    # controls for:
    # pause/play
    # frames per second
    # step forward one frame
    # world params: tau, terning kernel, phi_low, C_s, delta_phi

    def __init__(self, screen: pygame.Surface, world: model.AntWorld):
        self.screen = screen
        self.world = world
        self.buttons = []
        self.is_paused = True
        self.fps = 50

        x_offset = screen.get_size()[1]//world.params.world_size *256 + 20
        self.pause_button = PygameButton(pygame.Rect(x_offset, 10, 150, 40), "Play", self.toggle_pause)
        self.buttons.append(self.pause_button)
        self.step_button = PygameButton(pygame.Rect(x_offset, 60, 150, 40), "Step", self.step_forward)
        self.buttons.append(self.step_button)
        self.fps_up_button = PygameButton(pygame.Rect(x_offset, 110, 70, 40), "FPS+", self.increase_fps)
        self.buttons.append(self.fps_up_button)
        self.fps_down_button = PygameButton(pygame.Rect(x_offset + 80, 110, 70, 40), "FPS-", self.decrease_fps)
        self.buttons.append(self.fps_down_button)
        self.fps_label = PygameButton(pygame.Rect(x_offset, 160, 150, 40), f"FPS: {self.fps}", inert=True)
        self.buttons.append(self.fps_label)

    def increase_fps(self):
        self.fps += 10 if self.fps >= 10 else 1
        self.fps = min(60, self.fps)
        self.fps_label.text = f"FPS: {self.fps}"
    def decrease_fps(self):
        self.fps -= 10 if self.fps > 10 else 1
        self.fps = max(1, self.fps)
        self.fps_label.text = f"FPS: {self.fps}"

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        self.pause_button.text = "Play" if self.is_paused else "Pause"
    
    def step_forward(self):
        if self.is_paused:
            self.world.step()
    
    def draw(self):
        for button in self.buttons:
            button.draw(self.screen)

    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)

class WorldRenderer:
    def __init__(self, screen: pygame.Surface, world: model.AntWorld):
        self.screen = screen
        self.world = world
        self.heatmap_surface = pygame.Surface((world.params.world_size, world.params.world_size))
        self.scaling_factor = screen.get_size()[1]//world.params.world_size

    def draw(self):
        lattice_to_pixels(self.world.lattice, self.heatmap_surface)
        pygame.draw.rect(self.screen, (255, 255, 255), (0, 0, self.world.params.world_size * self.scaling_factor + 2, self.world.params.world_size * self.scaling_factor + 2))
        self.screen.blit(pygame.transform.scale_by(self.heatmap_surface, self.scaling_factor), (1, 1))

def main():
    pygame.init()
    screen = pygame.display.set_mode((1920, 1024+2)) # TODO: make screen-size agnostic
    clock = pygame.time.Clock()
    running = True
    params = model.WorldParams.default_large()
    world = model.AntWorld(params)
    controls = WorldControls(screen, world)
    renderer = WorldRenderer(screen, world)

    while running:
        for event in pygame.event.get():
            controls.handle_event(event)
            if event.type == pygame.QUIT:
                running = False

        if not controls.is_paused:
            world.step()
            if world.timestep % 10 == 0:
                print(f"Time step: {world.timestep}")

        renderer.draw()
        controls.draw()
        pygame.display.flip()

        clock.tick(controls.fps)
    pygame.quit()

if __name__ == "__main__":
    main()