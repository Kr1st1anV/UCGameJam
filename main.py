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
                [0, 0, 0, 0, 0, 0, -2, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0, -2, 0, 0, 0], 
                [0, 0, 0, -2, 0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 0, -2, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, -2, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, -2, 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0]]

class Mob:
    def __init__(self, grid_coords, sprite_size, pivot_x, pivot_y):
        self.waypoints = []
        w, h = sprite_size
        half_w, half_h = w / 2, h / 4
        
        # Convert grid indices to isometric screen coordinates
        for i, j in grid_coords:
            tx = pivot_x + (j - i) * half_w
            ty = pivot_y + (j + i) * half_h
            self.waypoints.append(pygame.Vector2(tx, ty + 80))
            
        self.pos = pygame.Vector2(self.waypoints[0]) if self.waypoints else pygame.Vector2(0,0)
        self.target_idx = 1
        self.speed = 0.5
        self.at_end = False

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
        # Draw a small red square as the 'runner'
        runner_rect = pygame.Rect(0, 0, 24, 24)
        runner_rect.center = (self.pos.x, self.pos.y)
        pygame.draw.rect(surface, (200, 50, 50), runner_rect)
        pygame.draw.rect(surface, (255, 255, 255), runner_rect, 2)                

class Game:

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
        self.runner = None
        self.x = 0
        self.y = 0
        self.set_path = False
        self.rm_path = False
        self.paths_remaining = MAX_TILES
        self.reset_grid()
        self.round_active = False
        self.edit_mode = True
        
        self.SPAWN_MOB_EVENT = pygame.USEREVENT + 1
        self.mobs = [] # List to track all active mobs
        self.mobs_to_spawn = 0
        self.points = 0
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
        scale_factor = 2.8
        self.ground = pygame.transform.scale(self.ground_sprite,(int(self.ground_sprite.get_width() * scale_factor), int(self.ground_sprite.get_height() * scale_factor)))
        self.path = pygame.transform.scale(self.path_sprite,(int(self.path_sprite.get_width() * scale_factor), int(self.path_sprite.get_height() * scale_factor)))
        self.water = pygame.transform.scale(self.water_sprite,(int(self.water_sprite.get_width() * scale_factor), int(self.water_sprite.get_height() * scale_factor)))
        self.chckpnt = pygame.transform.scale(self.chckpnt_sprite,(int(self.chckpnt_sprite.get_width() * scale_factor), int(self.chckpnt_sprite.get_height() * scale_factor)))
        self.red = pygame.transform.scale(self.red_sprite,(int(self.red_sprite.get_width() * scale_factor), int(self.red_sprite.get_height() * scale_factor)))
        self.spriteSize = (self.ground.get_width(), self.ground.get_height())

    def run_app(self) -> None:
        pygame.init()
        pygame.display.set_caption("Tower Offense")
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
        pivot_y = 125

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

    def get_path_waypoints(self):
        # 1. Find the starting -1 (bottom-most row preference)
        start_pos = None
        for i in range(GRID_SIZE - 1, -1, -1):
            for j in range(GRID_SIZE):
                if self.world_grid[i][j] == -1:
                    start_pos = (i, j)
                    break
            if start_pos: break

        if not start_pos: return []

        path_coords = [start_pos]
        visited = {start_pos}
        current = start_pos

        # 2. Trace the line
        while True:
            curr_i, curr_j = current
            found_next = False
            for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                ni, nj = curr_i + di, curr_j + dj
                if 0 <= ni < GRID_SIZE and 0 <= nj < GRID_SIZE:
                    val = self.world_grid[ni][nj]
                    if (ni, nj) not in visited and (val == 1 or val == -1):
                        path_coords.append((ni, nj))
                        visited.add((ni, nj))
                        current = (ni, nj)
                        found_next = True
                        if val == -1: # Reached the end
                            return path_coords
                        break
            if not found_next: break
        return path_coords

    def start_round(self):
        pygame.draw.rect(self.surface, (0,0,0), pygame.Rect(100,100,20,20))
    
    def draw_UI(self) -> None: 
        self.font = pygame.font.Font(None, 50)
        self.mobs_text = self.font.render(f'Mobs: {self.mobs_to_spawn}', True, (0, 0, 0))
        self.points_text = self.font.render(f'Points: {self.points}', True, (0, 0, 0))
        self.surface.blit(self.mobs_text, (100, 30))
        self.surface.blit(self.points_text, (100, 80))

    def draw_window(self) -> None:
        self.surface.fill(self.bgcolor)
        self.map_grid()   
        self.font = pygame.font.Font(None, 50)
        self.surface.blit(self.path_sprite, (50, 650))
        self.text = self.font.render(f'Remaining: {self.paths_remaining}', True, (0, 0, 0))
        self.surface.blit(self.text, (100, 650))
        if self.round_active:
            for mob in self.mobs:
                if not mob.at_end:
                    mob.update()
                    mob.draw(self.surface)
        #self.surface.blit(self.tree_sprite, (100, 100))
        self.draw_UI()
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
                            self.mobs_to_spawn = 10 
                            # Set timer to trigger SPAWN_MOB_EVENT every 1000ms (1 second)
                            pygame.time.set_timer(self.SPAWN_MOB_EVENT, 1000)
                elif event.type == self.SPAWN_MOB_EVENT:
                    if self.mobs_to_spawn > 0:
                        pts = self.get_path_waypoints()
                        new_mob = Mob(pts, self.spriteSize, DEFAULT_WIDTH/2, 50)
                        self.mobs.append(new_mob)
                        self.mobs_to_spawn -= 1
                    else:
                        pygame.time.set_timer(self.SPAWN_MOB_EVENT, 0)
                elif event.type == pygame.KEYUP:
                    pass
            self.draw_window()
            self.clock.tick(60)

# ========

if __name__ == "__main__":
    q = Game()
    q.run_app()

