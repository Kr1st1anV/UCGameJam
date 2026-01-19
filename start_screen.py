import os
import sys
import pygame
import copy
import numpy as np
import maps
import random

DEFAULT_WIDTH   = 978
DEFAULT_HEIGHT  = 750

class StartScreen:
    def __init__(self, surface):
        self.surface = surface
        self.frames = []
        self.folder_path = os.path.join(os.path.dirname(__file__), 'startscreen')
        
        # 1. Load all 20 frames
        # Assumes files are named something like 'frame_0001.png' to 'frame_0020.png'
        file_list = sorted(os.listdir(self.folder_path))
        for file in file_list:
            if file.endswith('.png'):
                img = pygame.image.load(os.path.join(self.folder_path, file)).convert_alpha()
                # Scale to fill the screen
                img = pygame.transform.scale(img, (DEFAULT_WIDTH, DEFAULT_HEIGHT))
                self.frames.append(img)

        # 2. Animation Variables
        self.current_frame = 0
        self.animation_speed = 0.15  # Adjust this to make the intro faster/slower
        self.animation_counter = 0

    def draw(self):
        # Update animation index
        self.animation_counter += self.animation_speed
        if self.animation_counter >= 1:
            self.animation_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)

        # Draw the current frame
        self.surface.blit(self.frames[self.current_frame], (0, 0))