import os
import sys
import pygame
import copy
import numpy as np

DEFAULT_BGCOLOR = (137, 207, 240)
DEFAULT_WIDTH   = 1280
DEFAULT_HEIGHT  = 720
GRID_SIZE = 12
MAX_TILES = 35
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'tiles')

rgb = tuple[int,int,int]

#SPRITES_DIR = os.path.join(ASSETS_DIR, 'sprites')

PRRSET_WORLD = [[0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0, -2, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, -2, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, -2, 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0]]

                

class Quitter:

    bgcolor : rgb
    width   : int
    height  : int
    surface : pygame.Surface
    clock   : pygame.time.Clock

    def __init__(self,
                 bgcolor : rgb = DEFAULT_BGCOLOR,
                 width   : int = DEFAULT_WIDTH,
                 height  : int = DEFAULT_HEIGHT) -> None:
        self.bgcolor = bgcolor if bgcolor else DEFAULT_BGCOLOR
        self.width   = width if width else DEFAULT_WIDTH
        self.height  = height if height else DEFAULT_HEIGHT
        self.ground = None
        self.x = 0
        self.y = 0
        self.set_path = False
        self.rm_path = False
        self.paths_remaining = MAX_TILES
        self.reset_grid()
        self.round_active = False
        self.edit_mode = True
        pygame.font.init()        

    def x_transform(self, x, w, h):
        return (x * w / 2, (x * h/2)/2)
    
    def y_transform(self,y, w, h):
        return ((-y * w) / 2, (y * h/2)/2)
    
    def load_image(self, name):
        path = os.path.join(ASSETS_DIR, name)
        return pygame.image.load(path).convert_alpha()
    
    def initiate_blocks(self):
        self.ground_sprite = self.load_image('grass_cube.png')
        self.path_sprite = self.load_image('path.png')
        self.water_sprite = self.load_image('water.png')
        self.chckpnt_sprite = self.load_image('grey.png')
        self.red_sprite = self.load_image('red.png')
        #self.tree_sprite = pygame.image.load('tree.png').convert_alpha()
        scale_factor = 3
        self.ground = pygame.transform.scale(self.ground_sprite,(int(self.ground_sprite.get_width() * scale_factor), int(self.ground_sprite.get_height() * scale_factor)))
        self.path = pygame.transform.scale(self.path_sprite,(int(self.path_sprite.get_width() * scale_factor), int(self.path_sprite.get_height() * scale_factor)))
        self.water = pygame.transform.scale(self.water_sprite,(int(self.water_sprite.get_width() * scale_factor), int(self.water_sprite.get_height() * scale_factor)))
        self.chckpnt = pygame.transform.scale(self.chckpnt_sprite,(int(self.chckpnt_sprite.get_width() * scale_factor), int(self.chckpnt_sprite.get_height() * scale_factor)))
        self.red = pygame.transform.scale(self.red_sprite,(int(self.red_sprite.get_width() * scale_factor), int(self.red_sprite.get_height() * scale_factor)))
        self.spriteSize = (self.ground.get_width(), self.ground.get_height())

    def run_app(self) -> None:
        pygame.init()
        pygame.display.set_caption("Quitter")
        self.surface = pygame.display.set_mode((self.width,self.height))
        self.clock = pygame.time.Clock()
        self.initiate_blocks()
        self.run_event_loop()

    def quit_app(self) -> None:
        pygame.quit()
        sys.exit()

    #Optimize This
    def map_grid(self): 
        
        w, h = self.spriteSize

        half_w = w / 2
        half_h = h / 4

        pivot_x = DEFAULT_WIDTH / 2
        pivot_y = 50

        rel_x = self.x - pivot_x
        rel_y = self.y - pivot_y

        mouse_j = (rel_x / half_w + rel_y / half_h) / 2
        mouse_i = (rel_y / half_h - rel_x / half_w) / 2

        grid_i, grid_j = int(np.floor(mouse_i)), int(np.floor(mouse_j))

        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):

                draw_x = pivot_x + (j - i) * half_w - half_w
                draw_y = pivot_y + (j + i) * half_h

                # Hover effect
                if self.edit_mode and self.world_grid[i][j] >= 0 and i == grid_i and j == grid_j:
                    draw_y -= 10
                    if self.set_path and self.paths_remaining > 0:
                        if  self.world_grid[i][j] != 1:
                            self.world_grid[i][j] = 1
                            self.paths_remaining -= 1
                    elif self.rm_path:
                        if  self.world_grid[i][j] != 0:
                            self.world_grid[i][j] = 0
                            self.paths_remaining += 1
                
                if self.world_grid[i][j] == 0:
                    self.surface.blit(self.ground, (draw_x, draw_y))
                elif self.world_grid[i][j] == 1:
                    self.surface.blit(self.path, (draw_x, draw_y))
                elif self.world_grid[i][j] == -1:
                    valid_path = self.is_grid_valid(self.world_grid, GRID_SIZE)
                    if valid_path:
                        self.surface.blit(self.water, (draw_x, draw_y))
                    else:
                        self.surface.blit(self.chckpnt, (draw_x, draw_y))
                elif self.world_grid[i][j] == -2:
                    self.surface.blit(self.red, (draw_x, draw_y))

    def start_round(self):
        pygame.draw.rect(self.surface, (0,0,0), pygame.Rect(100,100,20,20))

    def draw_window(self) -> None:
        self.surface.fill(self.bgcolor)
        self.map_grid()   
        self.font = pygame.font.Font(None, 50)
        self.surface.blit(self.path_sprite, (50, 650))
        self.text = self.font.render(f'Remaining: {self.paths_remaining}', True, (0, 0, 0))
        self.surface.blit(self.text, (100, 650))
        if self.round_active:
            self.start_round()
        #self.surface.blit(self.tree_sprite, (100, 100))
        pygame.display.update()

    #Optimize This
    def is_grid_valid(self, world_grid, grid_size):
        all_path_coords = []
        start_node = None

        for i in range(grid_size):
            for j in range(grid_size):
                val = world_grid[i][j]
                
                if val not in [1, -1]:
                    continue
                
                all_path_coords.append((i, j))
                
                if val == -1 and start_node is None:
                    start_node = (i, j)

                ones_around = 0
                neg_ones_around = 0
                
                for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < grid_size and 0 <= nj < grid_size:
                        neighbor = world_grid[ni][nj]
                        if neighbor == 1:
                            ones_around += 1
                        elif neighbor == -1:
                            neg_ones_around += 1

                if val == -1:
                    if ones_around != 1:
                        return False
                
                elif val == 1:
                    if ones_around < 1 or ones_around > 2:
                        return False
                    if neg_ones_around > 0 and ones_around > 1:
                        return False

        if not start_node:
            return len(all_path_coords) == 0
        
        visited = set()
        stack = [start_node]
        
        while stack:
            curr = stack.pop()
            if curr not in visited:
                visited.add(curr)
                curr_i, curr_j = curr
                for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    ni, nj = curr_i + di, curr_j + dj
                    if (ni, nj) in all_path_coords and (ni, nj) not in visited:
                        stack.append((ni, nj))

        return len(visited) == len(all_path_coords)
    
    def reset_grid(self):
        self.paths_remaining = MAX_TILES
        self.world_grid = copy.deepcopy(PRRSET_WORLD)

    def run_event_loop(self) -> None:
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.quit_app()
                elif event.type == pygame.MOUSEMOTION:
                    self.x, self.y = event.pos
                elif event.type == pygame.MOUSEBUTTONDOWN: # 1 is left, 3 is right
                    if event.button == 1:
                        self.set_path = True
                    elif event.button == 3:
                        self.rm_path = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.set_path = False
                    elif event.button == 3:
                        self.rm_path = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_grid()
                        self.edit_mode = True
                        self.round_active = False
                    if event.key == pygame.K_SPACE:
                        if self.is_grid_valid(self.world_grid, GRID_SIZE):
                            self.edit_mode = False
                            self.round_active = True
                elif event.type == pygame.KEYUP:
                    pass
            self.draw_window()
            self.clock.tick(60)

# ========

if __name__ == "__main__":
    q = Quitter()
    q.run_app()

