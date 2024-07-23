import pygame
from globals import *

class Food(pygame.sprite.Sprite):
    def __init__(self, pos, groups): #, food_list
        super().__init__(groups)

        self.image = pygame.Surface((16,16))
        self.image.fill(0)
        self.image.set_colorkey(0)
        pygame.draw.circle(self.image, [2,150,2], [8, 8], 4)
        self.rect = self.image.get_rect(center=pos)
        self.food_group = groups
        #self.food_list = food_list
        #print(f'{self.food_list}: hi, im inside food script')

    def update(self):
        if pygame.mouse.get_pressed()[2] :  # Right mouse button
            pos = pygame.mouse.get_pos()
            for food_sprite in self.food_group:
                if pygame.Vector2(pos).distance_to(food_sprite.rect.center) < FOOD_RADIUS + 5:
                    self.food_group.remove(food_sprite)
                    #food_sprite.kill()


