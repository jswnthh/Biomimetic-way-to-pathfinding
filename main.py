import pygame
import sys
import random
import math
from food import Food
from player import Player
from nest import Nest
from globals import *
from pherogrid import PheroGrid

class Game:
    def __init__(self) -> None:
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.cur_w, self.cur_h = self.display_surface.get_size()
        self.screen_size = (self.cur_w, self.cur_h)
        self.phero_layer = PheroGrid(self.screen_size)
        self.surfSize = (int(self.display_surface.get_width() / ORATIO), int(self.display_surface.get_height() / ORATIO))
        self.cell_width = int(self.display_surface.get_width() / self.surfSize[0])
        self.cell_height = int(self.display_surface.get_height() / self.surfSize[1])
        
        #self.food_list = []
        # Groups
        self.player_group = pygame.sprite.Group()
        self.food_group = pygame.sprite.Group()
        self.nest_group = pygame.sprite.Group()
        self.obstacle_group = pygame.sprite.Group()
        # Sprites
        self.nest_sprite = Nest((WINDOW_WIDTH/2, WINDOW_HEIGHT/2), self.nest_group)
        for _ in range(ANTS):
            self.player_sprite = Player(self.display_surface,
                                       self.phero_layer,
                                       self.nest_sprite.rect.center,
                                       self.player_group)
        
        # Create toggle button with instruction text
        self.paused_instruction_1 = "Simulation Paused"
        self.paused_instruction_2 = "While play, Press 'a' to toggle on/off ants"
        self.paused_instruction_3 = "While play, 'Click' right/left to create/remove food"
        self.paused_instruction_4 = "While play, Press 's' to toggle on/off sensors"
        self.paused_instruction_5 = "While paused, Press 't' to toggle gridlines to build obstacles"
        self.paused_instruction_6 = "While paused, 'Click' right to create; While play, 'Click' left to remove the obstacles"
        self.font = pygame.font.Font(None, 24)
        self.clock = pygame.time.Clock()

        # Pause state
        self.paused = False
        self.show_sensor = False
        self.show_ant = True
        
        # Menu state
        self.show_menu = True
        #self.show_gridlines = False
        self.menu_options = ["Press Enter to Start the Simulation"]
        self.selected_option = 0  
        self.fps_checker = 0

    def draw_grid(self, show_gridlines = False):        
        if show_gridlines:
            # Draw vertical lines
            for x in range(0, self.display_surface.get_width(), self.cell_width):
                pygame.draw.line(self.display_surface, (255, 255, 255), (x, 0), (x, self.display_surface.get_height()))

            # Draw horizontal lines
            for y in range(0, self.display_surface.get_height(), self.cell_height):
                pygame.draw.line(self.display_surface, (255, 255, 255), (0, y), (self.display_surface.get_width(), y))

    def create_obstacle(self, x, y):
        # Calculate grid cell coordinates
        grid_x = x // self.cell_width
        grid_y = y // self.cell_height

        # Create sprite at grid cell coordinates
        obstacle_sprite = pygame.sprite.Sprite()
        obstacle_sprite.image = pygame.Surface((self.cell_width, self.cell_height))
        obstacle_sprite.image.fill((255, 0, 0))  # Red color
        obstacle_sprite.rect = obstacle_sprite.image.get_rect()
        obstacle_sprite.rect.topleft = (grid_x * self.cell_width, grid_y * self.cell_height)

        self.obstacle_group.add(obstacle_sprite)
        #print(f'obstacle added: {self.obstacle_group}')
        self.obstacle_group.draw(self.display_surface)


    def handle_menu_events(self):
        """
        Handles events for the menu.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.menu_options)

                elif event.key == pygame.K_RETURN:
                    if self.selected_option == 0:
                        self.show_menu = not self.show_menu

                    if self.selected_option == 1:
                        pass
                

    def display_menu(self):
        """Displays the menu options."""
        #self.show_gridlines = True  # Ensure gridlines are always shown in the menu state
        self.display_surface.fill((0, 0, 0))  
        pygame.event.get(pygame.NOEVENT)  
        self.clock.tick(10)

        font = pygame.font.SysFont(None, 36)
        option_height = 40
        box_width = 500
        box_height = len(self.menu_options) * option_height
        margin_top = (WINDOW_HEIGHT - box_height) // 2
        margin_left = (WINDOW_WIDTH - box_width) // 2

        # Draw white boxes for menu options
        pygame.draw.rect(self.display_surface, (255, 255, 255), (margin_left, margin_top, box_width, box_height))
        
        for i, option in enumerate(self.menu_options):
            if i == self.selected_option:
                color = (0, 0, 0) #(128, 128, 128) grey
            else:
                color = (0, 0, 0)  # Black color for text
            text = font.render(option, True, color)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, margin_top + i * option_height + option_height // 2))
            self.display_surface.blit(text, text_rect)

        about_font = pygame.font.SysFont('timesnewroman', 24)
        about = about_font.render("You're going to watch a colony of ants working together to create a path when the food is created.", True, (255, 255, 255))
        about_rect = about.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        self.display_surface.blit(about, about_rect)                

        pygame.display.flip()

    def handle_events(self):
        """
        Handles all game events, including pause and food spawning.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if not self.paused:  # Only spawn food when the game is not paused
                        self.spawn_food(pygame.mouse.get_pos())

                    if self.paused:
                        # When paused, create obstacle sprites
                        x, y = event.pos
                        if 0 <= x < self.display_surface.get_width() and 0 <= y < self.display_surface.get_height():
                            self.create_obstacle(x, y)

                if event.button == 3:
                    # Always attempt to remove obstacle sprites regardless of the game state
                    mouse_pos = pygame.mouse.get_pos()
                    for obstacle_sprite in self.obstacle_group:
                        if obstacle_sprite.rect.collidepoint(mouse_pos):
                            self.obstacle_group.remove(obstacle_sprite)
                            obstacle_sprite.kill()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                    if self.paused:
                        self.display_pause_ui(self.paused_instruction_1,
                                               self.paused_instruction_2,
                                               self.paused_instruction_3,
                                               self.paused_instruction_4,
                                               self.paused_instruction_5,
                                               self.paused_instruction_6)
                elif event.key == pygame.K_ESCAPE:
                    self.show_menu = True
                elif event.key == pygame.K_t:
                    #if self.paused:  # Toggle gridlines only when the game is paused
                    self.draw_grid(show_gridlines=True)
                elif event.key == pygame.K_s:
                    self.show_sensor = not self.show_sensor 
                elif event.key == pygame.K_a:
                    self.show_ant = not self.show_ant
                

    def spawn_food(self, mouse_pos):
        """
        Creates food bits around the clicked position within a circular area.
        """
        food_bits = FOOD_BITS
        radius = FOOD_RADIUS

        for _ in range(food_bits):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, radius)

            fx = mouse_pos[0] + distance * math.cos(angle)
            fy = mouse_pos[1] + distance * math.sin(angle)

            if pygame.math.Vector2(fx - mouse_pos[0], fy - mouse_pos[1]).length() <= radius:
                food_sprite = Food((fx, fy), self.food_group ) #, self.food_list
                #self.food_list.append(food_sprite)
                self.food_group.add(food_sprite)

    def display_pause_ui(self, message1, message2, message3, message4, message5, message6):
        """
        Displays a simple pause message when the game is paused.
        """
        font = pygame.font.SysFont('timesnewroman', 20)

        text1 = font.render(message1, True, (255, 255, 255))
        text_rect1 = text1.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        self.display_surface.blit(text1, text_rect1)

        text2 = font.render(message2, True, (255, 255, 255))
        text_rect2 = text2.get_rect(topleft=(20, 10))
        self.display_surface.blit(text2, text_rect2)

        text3 = font.render(message3, True, (255, 255, 255))
        text_rect3 = text3.get_rect(topleft=(20, 40))
        self.display_surface.blit(text3, text_rect3)

        text4 = font.render(message4, True, (255, 255, 255))
        text_rect4 = text4.get_rect(topleft=(20, 70))
        self.display_surface.blit(text4, text_rect4)

        text5 = font.render(message5, True, (255, 255, 255))
        text_rect5 = text5.get_rect(topleft=(20,100))
        self.display_surface.blit(text5, text_rect5)

        text6 = font.render(message6, True, (255, 255, 255))
        text_rect6 = text6.get_rect(topleft=(20,130))
        self.display_surface.blit(text6, text_rect6)

        pygame.display.flip()


    def run(self):
        while True:
            if self.show_menu:
                self.handle_menu_events() 
                self.display_menu()
            else:
                self.handle_events()
                if self.paused:
                    self.clock.tick(10)  # Limit CPU usage while paused
                else:
                    # Game update logic:
                    dt = self.clock.tick(FPS) / 100

                    phero_img = self.phero_layer.update(dt)
                    rescaled_img = pygame.transform.scale(phero_img, (self.cur_w, self.cur_h))
                    pygame.Surface.blit(self.display_surface, rescaled_img, (0, 0))

                    # Update and draw all sprites
                    self.food_group.update()
                    self.food_group.draw(self.display_surface)

                    # Draw obstacle sprites
                    self.obstacle_group.draw(self.display_surface)

                    self.nest_group.update()
                    self.nest_group.draw(self.display_surface)

                    self.player_group.update(dt, self.show_sensor)
                    if self.show_ant == True:
                        self.player_group.draw(self.display_surface)


                    # Display "Press Space to Pause" text
                    font = pygame.font.SysFont('timesnewroman', 24)
                    text = font.render("Press Space to Pause/Play and read instructions", True, (255, 255, 255))  # White color
                    text_rect = text.get_rect(center=(self.display_surface.get_width() // 2, self.display_surface.get_height() - 20))
                    self.display_surface.blit(text, text_rect)    

            # Update the display
            pygame.display.update()

            self.fps_checker += 1
            if self.fps_checker >= FPS:
                print(round(self.clock.get_fps(), 2))
                self.fps_checker = 0


if __name__ == '__main__':
    game = Game()
    game.run()
