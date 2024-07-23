import pygame
from globals import *

class Nest(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.radius = 20  # Set the radius of the circle
        diameter = self.radius * 2
        self.image = pygame.Surface((diameter, diameter), pygame.SRCALPHA)  # Create a surface with alpha channel
        pygame.draw.circle(self.image, (245,245,220), (self.radius, self.radius), self.radius)  # Draw a circle
        self.rect = self.image.get_rect(center=pos)
    
    def update(self):
        pass
