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
                img = pygame.transform.scale(img, self.surface.get_size())
                self.frames.append(img)

        self.current_frame = 0
        self.animation_speed = 0.15
        self.animation_counter = 0
        ##################################################################
        self.start_img = self.load_image('start.png')
        self.start_img = pygame.transform.scale(self.start_img, (int(self.start_img.get_width() * 0.7), int(self.start_img.get_height() * 0.7)))
        full_rect = self.start_img.get_rect(topleft=(640, 160))
        self.start_hitbox = full_rect.inflate(-120, -120)
        ##################################################################
        self.settings_img = self.load_image('settings.png')
        self.settings_img = pygame.transform.scale(self.settings_img, (int(self.settings_img.get_width() * 0.7), int(self.settings_img.get_height() * 0.7)))
        settings_full_rect = self.settings_img.get_rect(topleft=(735, 615))
        self.settings_hitbox = settings_full_rect.inflate(-70, -65)

        ##################################################################
        self.tutorial_img = self.load_image('tutorial.png')
        tutorial_full_rect = self.tutorial_img.get_rect(topleft=(620, 400))
        self.tutorial_hitbox = tutorial_full_rect.inflate(-40, -30)

        ##################################################################
        self.logo_img = self.load_image('Heliosylva.png')
        self.logo_img = pygame.transform.scale(self.logo_img, (int(self.logo_img.get_width() * 0.7), int(self.logo_img.get_height() * 0.7)))

        self.settings_page = self.load_image('settingsmain.png')
        self.settings_page = pygame.transform.scale(
            self.settings_page,
            (int(self.settings_page.get_width() * 0.8), int(self.settings_page.get_height() * 0.8)),
        )

        self.settings_volume_label = ""
        self.settings_font = pygame.font.Font(None, 36)

        self.instr_page = self.load_image('instr_man.png')
        self.instr_page = pygame.transform.scale(
            self.instr_page,
            (int(self.instr_page.get_width() * 0.8), int(self.instr_page.get_height() * 0.8)),
        )

        self.start_rect = self.start_img.get_rect(topleft=(640, 160))
        self.settings_rect = self.settings_img.get_rect(topleft=(730, 610))
        self.tutorial_rect = self.tutorial_img.get_rect(topleft=(620, 400))

        # Hitboxes aligned to settingsmain.png blit at settings_page_pos
        self.settings_page_pos = (250, 130)
        spx, spy = self.settings_page_pos
        self.close_set_rect = pygame.Rect(spx + 81, spy + 88, 21, 22).inflate(16, 14)
        self.sound_left_rect = pygame.Rect(spx + 306, spy + 185, 20, 28).inflate(12, 10)
        self.sound_right_rect = pygame.Rect(spx + 425, spy + 185, 20, 28).inflate(12, 10)
        self.instr_rect = pygame.Rect(spx + 80, spy + 248, 400, 48)

        # Instructions page (instr_man.png) blit at (250, 30)
        self.instr_page_pos = (250, 30)
        ipx, ipy = self.instr_page_pos
        self.close_instr_rect = pygame.Rect(ipx + 81, ipy + 88, 21, 22).inflate(16, 14)

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
        #pygame.draw.rect(self.surface, (255, 0, 0), self.start_hitbox, 5) # Red outline
        #pygame.draw.rect(self.surface, (255, 0, 0), self.settings_hitbox, 5)

####################################################################################################################################
        self.surface.blit(self.logo_img, (0, 0))
        self.surface.blit(self.start_img, self.start_rect)
        self.surface.blit(self.settings_img, self.settings_rect)
        self.surface.blit(self.tutorial_img, self.tutorial_rect)
    
    def draw_settings(self):
        """Draws the buttons and the logo on top of the animation"""
        
        #pygame.draw.rect(self.surface, (255, 0, 0), self.close_set_rect, 5)

####################################################################################################################################
        self.surface.blit(self.settings_page, self.settings_page_pos)
        if self.settings_volume_label:
            label = self.settings_font.render(self.settings_volume_label, True, (45, 30, 18))
            # Volume readout beside the < > arrows on settingsmain.png
            self.surface.blit(label, (self.settings_page_pos[0] + 368, self.settings_page_pos[1] + 178))

    def set_settings_volume_label(self, text: str) -> None:
        self.settings_volume_label = text

    def draw_instructions(self):
        """Draws the buttons and the logo on top of the animation"""
        
        #pygame.draw.rect(self.surface, (255, 0, 0), self.settings_hitbox, 5)

####################################################################################################################################
        self.surface.blit(self.instr_page, self.instr_page_pos)

    def check_click(self, mouse_pos):
        if self.start_hitbox.collidepoint(mouse_pos):
            return "START"
        if self.tutorial_hitbox.collidepoint(mouse_pos):
            return "TUTORIAL"
        if self.settings_rect.collidepoint(mouse_pos):
            return "SETTINGS"
        return None
    def check_settings(self, mouse_pos):
        if self.close_set_rect.collidepoint(mouse_pos):
            return "CLOSE"
        if self.sound_left_rect.collidepoint(mouse_pos):
            return "SOUND_DOWN"
        if self.sound_right_rect.collidepoint(mouse_pos):
            return "SOUND_UP"
        if self.instr_rect.collidepoint(mouse_pos):
            return "INSTRUCTIONS"
        return None
    
    def check_closing_instructions(self, mouse_pos):
        if self.close_instr_rect.collidepoint(mouse_pos):
            return "CLOSE"
        return None
    