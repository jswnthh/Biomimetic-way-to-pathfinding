import pygame
from pygame.math import Vector2 as vec
from random import randint
import math
import numpy as np
from globals import *
from vector import Vec2


class Player(pygame.sprite.Sprite):
    def __init__(self, surface, pherolayer, nest_sprite, groups):
        super().__init__(groups)

        self.screen = surface
        self.surfaceWidth, self.surfaceHeight = self.screen.get_size()
        self.pygameSize = (int(self.surfaceWidth/PRATIO), int(self.surfaceHeight/PRATIO))
        self.isMyTrail = np.full(self.pygameSize, False)
        self.pheroLayer = pherolayer
        self.nest_pos = nest_sprite
        self.image = pygame.Surface((12, 21)).convert() #ant
        self.image.set_colorkey(0)
        pygame.draw.circle(self.image, [255, 255, 255], [8, 8], 3) #ant 
        self.orig_img = pygame.transform.rotate(self.image.copy(), -90)
        self.rect = self.image.get_rect(center=self.nest_pos)

    
        # Movement attributes
        self.angle = randint(0, 360)
        self.dzDir = vec(math.cos(math.radians(self.angle)), math.sin(math.radians(self.angle)))
        self.pos = vec(self.rect.center)
        
        self.vel = vec(0, 0)
         
        
        self.last_sdp = (self.nest_pos[0]/PRATIO, self.nest_pos[1]/PRATIO)
        self.mode = 0
        
        # Sensor parameters
        self.sensor_radius = 50.0
        self.sensor_color = pygame.Color('yellow')

    def sensors(self):
        # Define sensor offsets and positions
        self.mid_sensL = Vec2.vint(self.pos + vec(21, -3).rotate(self.angle))
        self.mid_sensR = Vec2.vint(self.pos + vec(21, 3).rotate(self.angle))
        self.left_sens1 = Vec2.vint(self.pos + vec(18, -14).rotate(self.angle))
        self.left_sens2 = Vec2.vint(self.pos + vec(16, -21).rotate(self.angle))
        self.right_sens1 = Vec2.vint(self.pos + vec(18, 14).rotate(self.angle))
        self.right_sens2 = Vec2.vint(self.pos + vec(16, 21).rotate(self.angle))

    def check_edge(self):
        if not self.screen.get_rect().collidepoint(self.left_sens2) and self.screen.get_rect().collidepoint(self.right_sens2):
            #print(f'Obstacle not detected on left_sens2: {self.left_sens2} and on right_sens2: {self.right_sens2}. Changing direction clockwise.')
            # Rotate the direction vector by a certain angle to change direction
            self.dzDir += vec(0,1).rotate(self.angle)#.normalize()
            #print(f'updating desired direction: {self.dzDir}')
            self.wandrStr = 0.01
            self.steerStr = 5
        elif not self.screen.get_rect().collidepoint(self.right_sens2) and self.screen.get_rect().collidepoint(self.left_sens2):
            #print(f'Obstacle not detected on right_sens2: {self.right_sens2} and on left_sens2: {self.right_sens2}. Changing direction anti clockwise.')
            # Rotate the direction vector by a certain angle to change direction
            self.dzDir += vec(0,-1).rotate(self.angle)#.normalize()
            #print(f'updating desired direction: {self.dzDir}')
            self.wandrStr = 0.01
            self.steerStr = 5
        elif not self.screen.get_rect().collidepoint(Vec2.vint(self.pos + vec(21, 0).rotate(self.angle))):
            #print('Obstacle detected ahead. Changing direction.')
            self.dzDir += vec(-1, 0).rotate(self.angle) #.normalize()
            #print(f'updating desired direction: {self.dzDir}')
            self.maxSpeed = 7
            self.wandrStr = 0.01
            self.steerStr = 5

    def collision_detection(self):
        
        self.mid_result = self.left_result = self.right_result = [0,0,0] 
        self.mid_GA_result = self.left_GA_result = self.right_GA_result = [0,0,0]

        if self.screen.get_rect().collidepoint(self.mid_sensL) and self.screen.get_rect().collidepoint(self.mid_sensR):
            self.mid_result, self.mid_isID, self.mid_GA_result = self.sensCheck(self.mid_sensL, self.mid_sensR)
            #print(f'printing self.mid_result{self.mid_result} and self.mid_GA_result: {self.mid_GA_result}')
        if self.screen.get_rect().collidepoint(self.left_sens1) and self.screen.get_rect().collidepoint(self.left_sens2):
            self.left_result, self.left_isID, self.left_GA_result = self.sensCheck(self.left_sens1, self.left_sens2)
            #print(f'printing self.left_result{self.left_result} and self.')
        if self.screen.get_rect().collidepoint(self.right_sens1) and self.screen.get_rect().collidepoint(self.right_sens2):
            self.right_result, self.right_isID, self.right_GA_result = self.sensCheck(self.right_sens1, self.right_sens2)
            #print(f'printing self.right_result{self.right_result}')

    def find(self):
        self.foodColor = (2,150,2)
        self.scaledown_pos = (int(self.pos.x / PRATIO), int(self.pos.y / PRATIO))

        #print('entering mode 0')
        if self.mode == 0 and self.pos.distance_to(self.nest_pos) > 21:
            self.mode = 1

        elif self.mode == 1:  # Look for food, or trail to food.
            #print('entering mode 1')
            set1Color = (171, 4, 204) #blue
            # Check if the ant has moved to a new position
            if self.scaledown_pos != self.last_sdp and self.scaledown_pos[0] in range(0, self.pygameSize[0]) and self.scaledown_pos[1] in range(0, self.pygameSize[1]):
                # Add a scent trail
                self.pheroLayer.img_array[self.scaledown_pos] += set1Color
                # Mark the position as part of the ant's trail
                self.isMyTrail[self.scaledown_pos] = True
                # Update the last position
                self.last_sdp = self.scaledown_pos
        
            # Check the results from sensors to determine movement
            if self.mid_result[1] > max(self.left_result[1], self.right_result[1]):
                self.dzDir += vec(1, 0).rotate(self.angle)#.normalize()
                self.wandrStr = .02
            elif self.left_result[1] > self.right_result[1]:
                self.dzDir += vec(1, -2).rotate(self.angle)#.normalize()
                self.wandrStr = .02
            elif self.right_result[1] > self.left_result[1]:
                self.dzDir += vec(1, 2).rotate(self.angle)#.normalize()
                self.wandrStr = .02

            # Check if food is detected
            if self.left_GA_result == self.foodColor and self.right_GA_result != self.foodColor:
                #print('food detected by left')
                #print(self.left_GA_result)
                self.dzDir += vec(0, -1).rotate(self.angle).normalize()
                self.wandrStr = .02
            elif self.right_GA_result == self.foodColor and self.left_GA_result != self.foodColor:
                #print(self.right_GA_result)
                #print('food detected by right')
                self.dzDir += vec(0, 1).rotate(self.angle).normalize()
                self.wandrStr = .02
            elif self.mid_GA_result == self.foodColor:
                #print(self.mid_GA_result)
                #print('food detected by mid')
                # Head directly towards the food
                self.dzDir = vec(-1, 0).rotate(self.angle).normalize()
                self.maxSpeed = 12
                self.wandrStr = .05
                self.steerStr = 0.1
                self.mode = 2

    def delivery(self):
        if self.mode == 2:  # Once found food, either follow own trail back to nest_pos, or head in nest_pos's general direction.
            #print('entering mode 2')
            self.set2Color = (5, 172, 181)
            # Check if the ant has moved to a new position
            if self.scaledown_pos != self.last_sdp and self.scaledown_pos[0] in range(0, self.pygameSize[0]) and self.scaledown_pos[1] in range(0, self.pygameSize[1]):
                # Add a scent trail
                self.pheroLayer.img_array[self.scaledown_pos] += self.set2Color
                # Update the last position
                self.last_sdp = self.scaledown_pos

            # Check if the ant is close to the nest
            if self.pos.distance_to(self.nest_pos) < 24:
                # Head directly towards the nest
                self.dzDir = vec(-1, 0).rotate(self.angle).normalize()
                # Reset trail markers
                self.isMyTrail[:] = False
                self.maxSpeed = 8
                self.wandrStr = .02
                self.steerStr = 0.1
                self.mode = 1
            elif self.mid_result[2] > max(self.left_result[2], self.right_result[2]) and self.mid_isID:
                # Follow the scent trail in front
                self.dzDir += vec(1, 0).rotate(self.angle).normalize()
                self.wandrStr = .02
            elif self.left_result[2] > self.right_result[2] and self.left_isID:
                # Follow the scent trail on the left
                self.dzDir += vec(1, -2).rotate(self.angle).normalize()  # left (0,-1)
                self.wandrStr = .02
            elif self.right_result[2] > self.left_result[2] and self.right_isID:
                # Follow the scent trail on the right
                self.dzDir += vec(1, 2).rotate(self.angle).normalize()  # right (0, 1)
                self.wandrStr = .02
            else:
                # If no clear trail, head towards the nest's general direction
                self.dzDir += vec(self.nest_pos - self.pos).normalize() * .08
                self.wandrStr = .02
        
    def obstacle_collision(self):            
        wallColor = (255,0,0)  # avoid walls of this color
        
        if self.left_GA_result == wallColor:
            #print(f'left detected wall: {self.left_GA_result}')
            #print('obstacle detected')
            self.dzDir += vec(0,1).rotate(self.angle)#.normalize()
            self.wandrStr = .01
            self.steerStr = 6
        elif self.right_GA_result == wallColor:
            #print('obstacle detected')
            #print(f'right detected wall: {self.right_GA_result}')
            self.dzDir += vec(0,-1).rotate(self.angle)#.normalize()
            self.wandrStr = .01
            self.steerStr = 6
        elif self.mid_GA_result == wallColor:
            #print(f'mid detected wall: {self.mid_GA_result}')
            #print('obstacle detected')
            self.dzDir += vec(-2,0).rotate(self.angle)#.normalize()
            self.maxSpeed = 8
            self.wandrStr = .01
            self.steerStr = 6

    def move(self, dt):        
        self.randomAngle = randint(0, 360)
        self.randDir = vec(math.cos(math.radians(self.randomAngle)), math.sin(math.radians(self.randomAngle)))
        #self.dzDir = vec(math.cos(math.radians(self.angle)), math.sin(math.radians(self.angle)))
        self.dzDir = vec(self.dzDir + self.randDir * self.wandrStr).normalize()
        self.dzvelocity = self.dzDir * self.speed
        self.dzStrFrc = (self.dzvelocity - self.vel) * self.steerStr
        self.accel = self.dzStrFrc if vec(self.dzStrFrc).magnitude() <= self.steerStr else vec(self.dzStrFrc.normalize() * self.steerStr)
        self.velocityo = self.vel + self.accel * dt
        self.vel = self.velocityo if vec(self.velocityo).magnitude() <= self.speed else vec(self.velocityo.normalize() * self.speed)
        self.pos += self.vel * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        self.angle = math.degrees(math.atan2(self.vel[1],self.vel[0]))
        # adjusts angle of img to match heading
        self.image = pygame.transform.rotate(self.orig_img, -self.angle)
        self.rect = self.image.get_rect(center=self.rect.center) 
        # actually update position
        self.rect.center = self.pos
    
    # def calculate_teal_pheromone_density(self):

    #     # Initialize density counter
    #     pDensity = 0

    #     # Iterate over the pheromone layer's image array
    #     for row in self.pheroLayer.img_array:
    #         for pixel in row:
    #             # Check if the pixel color matches the teal color
    #             if tuple(pixel) == self.set2Color:
    #                 pDensity += 1

    #     # Calculate density as the ratio of teal pixels to the total number of pixels
    #     total_pixels = self.pygameSize[0] * self.pygameSize[1]
    #     teal_density_ratio = pDensity / total_pixels

    #     return teal_density_ratio


    # def draw_dynamic_line(self, screen, teal_density_ratio, nest_position, food_position):
    #     # Define colors based on density
    #     line_color = (int(self.set2Color[0] * teal_density_ratio), int(self.set2Color[1] * teal_density_ratio), int(self.set2Color[2] * teal_density_ratio))

    #     # Define thickness based on density
    #     line_thickness = int(2 + 10 * teal_density_ratio)  # Adjust the factor to control thickness dynamically

    #     # Draw the line from nest to food
    #     pygame.draw.line(screen, line_color, nest_position, food_position, line_thickness)

    def draw(self, show_sensor):
        if show_sensor:
            # Draw the sensors
            pygame.draw.circle(self.screen, self.sensor_color, self.mid_sensL, 3)
            pygame.draw.circle(self.screen, self.sensor_color, self.mid_sensR, 3)
            pygame.draw.circle(self.screen, self.sensor_color, self.left_sens1, 3)
            pygame.draw.circle(self.screen, self.sensor_color, self.left_sens2, 3)
            pygame.draw.circle(self.screen, self.sensor_color, self.right_sens1, 3)
            pygame.draw.circle(self.screen, self.sensor_color, self.right_sens2, 3)

    def sensCheck(self, pos1, pos2): # checks given points in Array, IDs, and pixels on screen.
        
        #print(f'p1:{pos1}, p2:{pos2}')
        self.sdpos1 = (int(pos1[0]/PRATIO),int(pos1[1]/PRATIO))
        self.sdpos2 = (int(pos2[0]/PRATIO),int(pos2[1]/PRATIO))
        #print(f'sdp1:{self.sdpos1}, sdp2:{self.sdpos2}')
        self.array_r1 = self.pheroLayer.img_array[self.sdpos1]
        #print(f'{array_r1}')
        self.array_r2 = self.pheroLayer.img_array[self.sdpos2]
        self.array_result = (max(self.array_r1[0], self.array_r2[0]), max(self.array_r1[1], self.array_r2[1]), max(self.array_r1[2], self.array_r2[2]))

        self.is1ID = self.isMyTrail[self.sdpos1]
        self.is2ID = self.isMyTrail[self.sdpos2]
        self.isID = self.is1ID or self.is2ID

        self.ga_r1 = self.screen.get_at(pos1)[:3]
        self.ga_r2 = self.screen.get_at(pos2)[:3]
        self.ga_result = (max(self.ga_r1[0], self.ga_r2[0]), max(self.ga_r1[1], self.ga_r2[1]), max(self.ga_r1[2], self.ga_r2[2]))
        
        return self.array_result, self.isID, self.ga_result

    def update(self, dt, show_sensor):
        self.speed = SPEED
        self.wandrStr = WANDERING
        self.steerStr = STEERING 
        self.sensors()
        self.collision_detection()
        self.find()
        self.delivery()
        self.obstacle_collision()
        self.check_edge()
        self.draw(show_sensor)
        self.move(dt)
        

    
