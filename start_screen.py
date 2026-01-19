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

        file_list = sorted(os.listdir(self.folder_path))
        for file in file_list:
            if file.endswith('.png'):
                img = pygame.image.load(os.path.join(self.folder_path, file)).convert_alpha()
                img = pygame.transform.scale(img, (DEFAULT_WIDTH, DEFAULT_HEIGHT))
                self.frames.append(img)

        self.current_frame = 0
        self.animation_speed = 0.15
        self.animation_counter = 0

        self.start_img = self.load_image('start.png')
        full_rect = self.start_img.get_rect(topleft=(505, 190))
        self.start_hitbox = full_rect.inflate(-180, -170)
        self.settings_img = self.load_image('settings.png')
        self.tutorial_img = self.load_image('tutorial.png')
        self.logo_img = self.load_image('Heliosylva.png')

        self.start_rect = self.start_img.get_rect(topleft=(500, 200))
        self.settings_rect = self.settings_img.get_rect(topleft=(600, 500))
        self.tutorial_rect = self.tutorial_img.get_rect(topleft=(600, 400))


    def load_image(self, name):
        path = os.path.join(os.path.dirname(__file__), 'buttons', name)
        return pygame.image.load(path).convert_alpha()

    def draw(self):
        self.animation_counter += self.animation_speed
        if self.animation_counter >= 1:
            self.animation_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)

        # Draw the current frame
        self.surface.blit(self.frames[self.current_frame], (0, 0))

    def draw_buttons(self):
        """Draws the buttons and the logo on top of the animation"""
        #pygame.draw.rect(self.surface, (255, 0, 0), self.start_hitbox, 2) # Red outline
        self.surface.blit(self.logo_img, (0, -50))
        self.surface.blit(self.start_img, self.start_rect)
        self.surface.blit(self.tutorial_img, self.tutorial_rect)
        self.surface.blit(self.settings_img, self.settings_rect)

    def check_click(self, mouse_pos):
        if self.start_hitbox.collidepoint(mouse_pos):
            return "START"
        if self.tutorial_rect.collidepoint(mouse_pos):
            return "TUTORIAL"
        return None