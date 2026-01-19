import os
import sys
import pygame
import copy
import numpy as np
import random

DEFAULT_BGCOLOR = (137, 207, 240)
DEFAULT_WIDTH   = 978
DEFAULT_HEIGHT  = 750
GRID_SIZE = 10
MAX_TILES = 35
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'tiles')
BGROUND_DIR = os.path.join(os.path.dirname(__file__), 'bground')
TOWERS_DIR = os.path.join(os.path.dirname(__file__), 'towers')
MOBS_DIR = os.path.join(os.path.dirname(__file__), 'mobs')

class Mob:
    def __init__(self, grid_coords, sprite_size, pivot_x, pivot_y):
        self.waypoints = []
        w, h = sprite_size
        half_w, half_h = w / 2, h / 4
        pivot_x = DEFAULT_WIDTH /3
        pivot_y = 125 * 2
        self.mobcolor = [(200, 50, 50),(93, 63, 211),(0, 255, 255)]
        self.mobtype = ['red.png', 'purple.png', 'water.png']
        self.randmob = random.randint(0, len(self.mobtype) - 1)
        
        # Convert grid indices to isometric screen coordinates
        for i, j in grid_coords:
            tx = pivot_x + (j - i) * half_w
            ty = pivot_y + (j + i) * half_h
            self.waypoints.append(pygame.Vector2(tx, ty))
            
        self.pos = pygame.Vector2(self.waypoints[0]) if self.waypoints else pygame.Vector2(0,0)
        self.target_idx = 1
        self.speed = 1.2
        self.at_end = False
    
    def load_mob(self, name):
        path = os.path.join(MOBS_DIR, name)
        return pygame.image.load(path).convert_alpha()

    def update(self):
        if self.target_idx < len(self.waypoints):
            target = self.waypoints[self.target_idx]
            move_vec = target - self.pos
            if move_vec.length() > self.speed:
                self.pos += move_vec.normalize() * self.speed
            else:
                self.pos = pygame.Vector2(target)
                self.target_idx += 1
        else:
            self.at_end = True  

    def draw(self, surface):
        pass
        # Draw a small red square as the 'runner'
        #mob_sprite = self.load_mob("bee1.png")
        #surface.blit(mob_sprite, (self.pos.x - 32, self.pos.y - 32))           
