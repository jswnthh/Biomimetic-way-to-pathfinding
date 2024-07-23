import pygame
import sys
from globals import *

class Test():
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.surfSize = (int(self.screen.get_width() / ORATIO), int(self.screen.get_height() / ORATIO))
        self.cell_width = int(self.screen.get_width() / self.surfSize[0])
        self.cell_height = int(self.screen.get_height() / self.surfSize[1])

        self.sprites = pygame.sprite.Group()

        # Create toggle button with instruction text
        self.instruction_text = "Press 't' to toggle gridlines"
        self.font = pygame.font.Font(None, 24)
        self.toggle_button = self.font.render(self.instruction_text, True, (0, 0, 0))
        self.toggle_button_rect = self.toggle_button.get_rect(topleft=(10, 10))
        self.show_gridlines = False

    def draw_grid(self):
        if self.show_gridlines:
            # Draw vertical lines
            for x in range(0, self.screen.get_width(), self.cell_width):
                pygame.draw.line(self.screen, (0, 0, 0), (x, 0), (x, self.screen.get_height()))

            # Draw horizontal lines
            for y in range(0, self.screen.get_height(), self.cell_height):
                pygame.draw.line(self.screen, (0, 0, 0), (0, y), (self.screen.get_width(), y))

    def create_sprite(self, x, y):
        # Calculate grid cell coordinates
        grid_x = x // self.cell_width
        grid_y = y // self.cell_height

        # Create sprite at grid cell coordinates
        sprite = pygame.sprite.Sprite()
        sprite.image = pygame.Surface((self.cell_width, self.cell_height))
        sprite.image.fill((255, 0, 0))  # Red color
        sprite.rect = sprite.image.get_rect()
        sprite.rect.topleft = (grid_x * self.cell_width, grid_y * self.cell_height)

        self.sprites.add(sprite)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        x, y = event.pos
                        if 0 <= x < self.screen.get_width() and 0 <= y < self.screen.get_height():
                            self.create_sprite(x, y)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_t:
                        self.show_gridlines = not self.show_gridlines

            self.screen.fill((255, 255, 255))  # Fill with white color tuple

            self.draw_grid()

            self.sprites.draw(self.screen)

            # Draw toggle button onto screen surface
            self.screen.blit(self.toggle_button, self.toggle_button_rect.topleft)

            pygame.display.update()


if __name__ == '__main__':
    test = Test()
    test.run()
