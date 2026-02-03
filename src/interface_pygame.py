import model

import pygame
import math

def lattice_to_pixels(lattice: model.Lattice, surf: pygame.Surface) -> None:
    size = int(math.sqrt(len(lattice.nodes)))
    for node in lattice.nodes:
        x, y = node.position
        intensity = min(255, node.pheromone_level * 2)
        surf.set_at((x, y), (intensity, 0, 0))


def main():
    pygame.init()
    screen = pygame.display.set_mode((1920, 1024)) # TODO: make screen-size agnostic
    clock = pygame.time.Clock()
    running = True
    params = model.WorldParams.default_large()
    world = model.AntWorld(params)
    heatmap_surface = pygame.Surface((params.world_size, params.world_size))
    scaling_factor = screen.get_size()[1]//params.world_size

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        world.step()
        if world.timestep % 10 == 0:
            print(f"Time step: {world.timestep}")
        lattice_to_pixels(world.lattice, heatmap_surface)
        screen.blit(pygame.transform.scale_by(heatmap_surface, scaling_factor), (0, 0))
        pygame.display.flip()
        clock.tick(10)
    pygame.quit()

if __name__ == "__main__":
    main()