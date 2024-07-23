import pygame
import numpy as np
from globals import *

class PheroGrid():
    def __init__(self, screen_size):
        self.surfSize = (int(screen_size[0]/PRATIO), int(screen_size[1]/PRATIO))
        self.image = pygame.Surface(self.surfSize).convert()
        self.img_array = np.array(pygame.surfarray.array3d(self.image), dtype=float)

    def update(self, dt):
        evaporation_factor = 0.2 * (100/FPS) * (dt/10) * FPS
        self.img_array -= evaporation_factor
        self.img_array = np.clip(self.img_array, 0, 255)
        pygame.surfarray.blit_array(self.image, self.img_array)
        return self.image