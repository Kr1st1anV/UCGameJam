import os
import sys
import pygame
import copy
import numpy as np
import maps as Maps
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

rgb = tuple[int,int,int]
num = random.randint(1,5)
#PRESET_WORLD = maps.levels[1]

#SPRITES_DIR = os.path.join(ASSETS_DIR, 'sprites')


PRESET_WORLD = [[-1, 0, 0, 0, "l1", 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, "b2", 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0, "b2", 0], 
                [0, "l1", 0, "b2", 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, "l1", 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, -9, 0, 0, 0, 0], 
                [0, 0, "b2", 0, 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, "b2", 0, 0], 
                [0, 0, 0, 0, "l1", 0, 0, 0, 0, -8], 
                [0, 0, 0, 0, 0, 0, 0, 0, 0, -1]]

class Mob:
    def __init__(self, grid_coords, sprite_size, pivot_x, pivot_y):
        self.health = 10
        self.waypoints = []
        w, h = sprite_size
        half_w, half_h = w / 2, h / 4
        pivot_x = DEFAULT_WIDTH /3
        pivot_y = 125 * 2
        self.mobcolor = [(200, 50, 50),(93, 63, 211),(0, 255, 255)]
        self.mobtype = [['dragonfly flying_0001.png', 'dragonfly flying_0002.png', 'dragonfly flying_0003.png', 'dragonfly flying_0004.png']
                        , ['worm moving_0001.png', 'worm moving_0002.png', 'worm moving_0003.png', 'worm moving_0004.png'],
                        ['butterfly_0001.png', 'butterfly_0002.png', 'butterfly_0003.png', 'butterfly_0004.png'],
                        ['snail idle_0001.png', 'snail idle_0002.png', 'snail idle_0003.png', 'snail idle_0004.png'],
                        ['beetle_0001.png', 'beetle_0002.png', 'beetle_0003.png', 'beetle_0004.png']]
        self.randmob = random.randint(0, len(self.mobtype) - 1)

        self.mobframes = [self.load_mob(frame) for frame in self.mobtype[self.randmob]]

        self.current_frame = 0
        self.animaton_speed = 0.20
        self.animation_counter = 0
        
        # Convert grid indices to isometric screen coordinates
        for i, j in grid_coords:
            tx = pivot_x + (j - i) * half_w
            ty = pivot_y + (j + i) * half_h
            self.waypoints.append(pygame.Vector2(tx, ty))
            
        self.pos = pygame.Vector2(self.waypoints[0]) if self.waypoints else pygame.Vector2(0,0)
        self.target_idx = 1
        self.speed = 1.0
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

        self.animation_counter += self.animaton_speed
        if self.animation_counter >= 1:
            self.animation_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.mobframes)

    def draw(self, surface):
        current_sprite = self.mobframes[self.current_frame]
        
        if self.target_idx < len(self.waypoints):
            target = self.waypoints[self.target_idx]
            if target.x < self.pos.x:
                current_sprite = pygame.transform.flip(current_sprite, True, False)

        sprite_rect = current_sprite.get_rect()
        sprite_rect.center = (self.pos.x, self.pos.y)
        surface.blit(current_sprite, sprite_rect)

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
        self.edit_mode = True

        self.highlight = True

        self.round_active = False
        self.round_ended = True
        
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

    def load_world(self, name):
        path = os.path.join(BGROUND_DIR, name)
        return pygame.image.load(path).convert_alpha()
    
    def load_towers(self, name):
        path = os.path.join(TOWERS_DIR, name)
        return pygame.image.load(path).convert_alpha()
    
    def initiate_blocks(self):
        scale_factor = 1
        self.tiles = {}
        for root, dir, files in os.walk(ASSETS_DIR):
            all_tiles = sorted(files)
            for tile in all_tiles:
                name = tile.split(".")[0]
                if tile == "path.png":
                    self.path_icon = self.load_image(tile)
                    self.path_icon = pygame.transform.scale(self.path_icon,(int(self.path_icon.get_width() * 1.5), int(self.path_icon.get_height() * 1.5)))
                temp_sprite = self.load_image(tile)
                self.temp_tile = pygame.transform.scale(temp_sprite,(int(temp_sprite.get_width() * scale_factor), int(temp_sprite.get_height() * scale_factor)))
                self.tiles[name] = self.temp_tile
        self.tree_sprite = self.load_image('tree.png')
        self.tiles["tree"] = self.temp_tile = pygame.transform.scale(self.tree_sprite,(int(self.tree_sprite.get_width() * 2.5), int(self.tree_sprite.get_height() *2.5)))
        self.spriteSize = (self.tiles["dark_grass"].get_width(), self.tiles["dark_grass"].get_height())
        self.h_tiles = {name : self.highlight_block(tile) for name, tile in self.tiles.items()}

    def initiate_towers(self):
        scale_factor = 0.75
        self.towers = {}
        self.bee_frames = []
        self.ladybug_frames = []
        
        for root, dirs, files in os.walk(TOWERS_DIR):
            all_files = sorted(files)
            for file in all_files:
                name = file.split(".")[0]
                temp_sprite = self.load_towers(file)
                scaled_sprite = pygame.transform.scale(temp_sprite, (int(temp_sprite.get_width() * scale_factor), int(temp_sprite.get_height() * scale_factor)))
                
                self.towers[name] = scaled_sprite
                
                if "bee" in name:
                    self.bee_frames.append(scaled_sprite)
                
                if "ladybug" in name:
                    self.ladybug_frames.append(scaled_sprite)

        self.bush_sprite = self.load_towers('bush.png')
        self.towers["bush"] = pygame.transform.scale(self.bush_sprite, (int(self.bush_sprite.get_width() * 1.2), int(self.bush_sprite.get_height() * 1.2)))
        
        self.towerSize = (self.towers["bee1"].get_width(), self.towers["bee1"].get_height())
        self.h_towers = {name : self.highlight_block(tower) for name, tower in self.towers.items()}
        
        self.bee_anim_index = 0
        self.bee_anim_timer = 0

    def run_app(self) -> None:
        pygame.init()
        pygame.display.set_caption("Power Offense")
        self.surface = pygame.display.set_mode((self.width,self.height))
        self.clock = pygame.time.Clock()
        self.initiate_blocks()
        self.initiate_towers()
        self.run_event_loop()

    def quit_app(self) -> None:
        pygame.quit()
        sys.exit()

    #Optimize This
    def map_grid(self): 
        
        w, h = self.spriteSize

        half_w = w / 2
        half_h = h / 4

        pivot_x = DEFAULT_WIDTH / 3
        pivot_y = 125 * 2

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
                if self.edit_mode and type(self.world_grid[i][j]) == int and self.world_grid[i][j] >= 0 and i == grid_i and j == grid_j:
                    #draw_y -= 10
                    self.highlight = True
                    if self.set_path and self.paths_remaining > 0:
                        if  self.world_grid[i][j] != 1:
                            self.world_grid[i][j] = 1
                            self.paths_remaining -= 1
                    elif self.rm_path:
                        if  self.world_grid[i][j] != 0:
                            self.world_grid[i][j] = 0
                            self.paths_remaining += 1
                else:
                    self.highlight = False
                if self.highlight:
                    if self.world_grid[i][j] == 0:
                        self.surface.blit(self.h_tiles["dark_grass"], (draw_x, draw_y)) # Grass
                    elif self.world_grid[i][j] == 1:
                        sprite = self.get_path_sprite(i, j)
                        self.surface.blit(sprite, (draw_x, draw_y))
                    elif self.world_grid[i][j] == -1:
                        valid_path = self.is_grid_valid(self.world_grid, GRID_SIZE)
                        if valid_path:
                            self.surface.blit(self.h_tiles["purple"], (draw_x, draw_y)) # Purple Block
                        else:
                            self.surface.blit(self.h_tiles["grey"], (draw_x, draw_y)) # Grey
                    elif self.world_grid[i][j] == -3:
                        self.surface.blit(self.h_tiles["white"], (draw_x, draw_y)) # White
                    elif self.world_grid[i][j] == -9:
                        self.surface.blit(self.h_tiles["dark_grass"], (draw_x, draw_y)) # Tree
                else:
                    if self.world_grid[i][j] == 0:
                        self.surface.blit(self.tiles["dark_grass"], (draw_x, draw_y)) # Grass
                    elif self.world_grid[i][j] == 1:
                        sprite = self.get_path_sprite(i, j)
                        self.surface.blit(sprite, (draw_x, draw_y))
                    elif self.world_grid[i][j] == -1:
                        valid_path = self.is_grid_valid(self.world_grid, GRID_SIZE)
                        if valid_path:
                            self.surface.blit(self.tiles["purple"], (draw_x, draw_y)) # Purple Block
                        else:
                            self.surface.blit(self.tiles["grey"], (draw_x, draw_y)) # Grey
                    elif self.world_grid[i][j] == "l1" or self.world_grid[i][j] == "b2":
                        self.surface.blit(self.tiles["red"], (draw_x, draw_y)) # Red
                    elif self.world_grid[i][j] == -3:
                        self.surface.blit(self.tiles["white"], (draw_x, draw_y)) # White
                    elif self.world_grid[i][j] == -9:
                        self.surface.blit(self.tiles["dark_grass"], (draw_x, draw_y)) # Tree
                    elif self.world_grid[i][j] == -8:
                        self.surface.blit(self.tiles["dark_grass"], (draw_x, draw_y)) # Tree

    def get_path_waypoints(self):
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

    def highlight_block(self, sprite, amount = 80):
        white_sprite = pygame.Surface(sprite.get_size()).convert_alpha()
        white_sprite.fill((amount, amount, amount, 0))
        highlighted_sprite = sprite.copy()
        highlighted_sprite.blit(white_sprite, (0,0), special_flags = pygame.BLEND_RGB_ADD)
        return highlighted_sprite
    
    def get_path_sprite(self, i, j):
        # 1. Check neighbors (1 or -1 means a path exists)
        tl = i > 0 and self.world_grid[i-1][j] in [1, -1]
        tr = j > 0 and self.world_grid[i][j-1] in [1, -1]
        bl = j < GRID_SIZE - 1 and self.world_grid[i][j+1] in [1, -1]
        br = i < GRID_SIZE - 1 and self.world_grid[i+1][j] in [1, -1]

        # 2. Build a key based on which neighbors are True
        # We will use alphabetical order so 'tl' and 'tr' becomes 'tltr'
        connections = []
        if tl: connections.append("tl")
        if tr: connections.append("tr")
        if bl: connections.append("bl")
        if br: connections.append("br")
        
        key = "".join(connections)

        # 3. The Mapping Dictionary (Your "Guess and Check" area)
        # The key is the neighbors found, the value is your filename
        mapping = {
            # --- 4-Way Junction ---
            "tltrblbr": "4way",

            # --- 3-Way Junctions ---
            "tltrbr":   "3waytl",
            "tltrbl":   "3waytr",
            "tlblbr":   "3waybr",
            "trblbr":   "3waybl",

            # --- 2-Way (Straights & Corners) ---
            "tlbr":     "posdia", # Straight line from Top-Left to Bottom-Right
            "trbl":     "negdia", # Straight line from Top-Right to Bottom-Left
            "blbr":     "blbr",   # Corner connecting Bottom-Left and Bottom-Right
            "tltr":     "tltr",   # Corner connecting Top-Left and Top-Right
            "tlbl":     "trbr",   # Corner connecting Top-Left and Bottom-Left
            "trbr":     "tlbl",   # Corner connecting Top-Right and Bottom-Right

            # --- 1-Way (Dead Ends) ---
            "tl":       "endbl",
            "tr":       "endbr",
            "bl":       "endtl",
            "br":       "endtr"
        }

        # Return the image from your loaded tiles, or a default path if not found
        tile_name = mapping.get(key, "path") 
        return self.tiles.get(tile_name, self.tiles["path"])


    
    def draw_UI(self) -> None: 
        self.font = pygame.font.Font(None, 35)
        self.mobs_text = self.font.render(f'Mobs: {self.mobs_to_spawn}', True, (0, 0, 0))
        self.points_text = self.font.render(f'Points: {self.points}', True, (0, 0, 0))
        self.units_text = self.font.render(f'Units:', True, (0, 0, 0))
        self.surface.blit(self.mobs_text, (750, 30))
        self.surface.blit(self.points_text, (750, 80))
        self.surface.blit(self.units_text, (1130, 550))

    def get_object_layers(self):
        w, h = self.spriteSize
        half_w, half_h = w / 2, h / 4
        pivot_x, pivot_y = DEFAULT_WIDTH / 3, 125 * 2

        rel_x, rel_y = self.x - pivot_x, self.y - pivot_y
        mouse_j = (rel_x / half_w + rel_y / half_h) / 2
        mouse_i = (rel_y / half_h - rel_x / half_w) / 2
        grid_i, grid_j = int(np.floor(mouse_i)), int(np.floor(mouse_j))

        self.bee_anim_timer += 0.15
        self.bee_anim_index = int(self.bee_anim_timer % len(self.bee_frames))
        
        # Subtle Up/Down: Sine wave based on time
        # 5 is the pixel height of the bob, 0.005 is the speed
        bobbing_offset = np.sin(pygame.time.get_ticks() * 0.005) * 5

        tree_elements = []
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if self.world_grid[i][j] == "b2":
                    draw_x = pivot_x + (j - i) * half_w - half_w
                    draw_y = pivot_y + (j + i) * half_h
                    bee_surf = self.bee_frames[self.bee_anim_index].copy()
                    if i == grid_i and j == grid_j:
                        bee_surf.set_alpha(100)
                    else:
                        bee_surf.set_alpha(255)

                    tree_elements.append({
                        'z': draw_y, 
                        'type': 'bee', 
                        'surf': bee_surf, 
                        # Added bobbing_offset to the Y position
                        'pos': (draw_x, (draw_y - h * 0.76) + bobbing_offset)
                    })
                    
                elif self.world_grid[i][j] == "l1":
                    draw_x = pivot_x + (j - i) * half_w - half_w
                    draw_y = pivot_y + (j + i) * half_h
                    bee_surf = self.ladybug_frames[self.bee_anim_index].copy()
                    if i == grid_i and j == grid_j:
                        bee_surf.set_alpha(100)
                    else:
                        bee_surf.set_alpha(255)

                    tree_elements.append({
                        'z': draw_y, 
                        'type': 'ladybug', 
                        'surf': bee_surf, 
                        # Added bobbing_offset to the Y position
                        'pos': (draw_x, (draw_y - h * 0.76) + bobbing_offset)
                    })
                    
                elif self.world_grid[i][j] == -9:
                    draw_x = pivot_x + (j - i) * half_w - half_w
                    draw_y = pivot_y + (j + i) * half_h
                    tree_surf = self.tiles["tree"].copy()
                    if i == grid_i and j == grid_j:
                        tree_surf.set_alpha(100)
                    else:
                        tree_surf.set_alpha(255)
                    tree_elements.append({
                        'z': draw_y, 
                        'type': 'tree', 
                        'surf': tree_surf, 
                        'pos': (draw_x - 20, draw_y - h * 1.75)
                    })
                elif self.world_grid[i][j] == -8:
                    draw_x = pivot_x + (j - i) * half_w - half_w
                    draw_y = pivot_y + (j + i) * half_h
                    tree_surf = self.towers["bush"].copy()
                    if i == grid_i and j == grid_j:
                        tree_surf.set_alpha(100)
                    else:
                        tree_surf.set_alpha(255)
                    tree_elements.append({
                        'z': draw_y, 
                        'type': 'bush', 
                        'surf': tree_surf, 
                        'pos': (draw_x, draw_y - 16)
                    })
        return tree_elements

    def draw_window(self) -> None:
        self.surface.fill(self.bgcolor)
        self.background = self.load_world("fullbg.png")
        self.bg_image = pygame.transform.scale(self.background,(int(self.background.get_width() * 0.7), int(self.background.get_height() * 0.75)))
        self.surface.blit(self.bg_image, (0, 0))
        # self.island = self.load_world("island.png")
        # self.island_image = pygame.transform.scale(self.island,(int(self.island.get_width() * 1.1), int(self.island.get_height() * 1.1)))
        # self.surface.blit(self.island_image, (150, -50))
        self.map_grid()
        self.tree_life = self.load_world("tree_of_life.png")
        self.tree_life_img = pygame.transform.scale(self.tree_life,(int(self.tree_life.get_width() * 1), int(self.tree_life.get_height() * 1)))
        self.surface.blit(self.tree_life_img, (250, 50))
        self.surface.blit(self.load_image('red.png'), (800, 600))
        self.surface.blit(self.load_image('purple.png'), (840, 600))
        self.surface.blit(self.load_image('water.png'), (880, 600))

        layer_queue = []
        layer_queue.extend(self.get_object_layers())

        if self.round_active:
            finished_mobs = [m for m in self.mobs if m.at_end]
            for _ in finished_mobs:
                self.points += 1
            
            self.mobs = [m for m in self.mobs if not m.at_end]
            for mob in self.mobs:
                mob.update()
                layer_queue.append({
                    'z': mob.pos.y, 
                    'type': 'mob', 
                    'obj': mob
                })

        # Sorts by furthest from screen to closest to screen
        layer_queue.sort(key=lambda item: item['z'])

        # Draw based off order
        for item in layer_queue:
            if item['type'] == 'tree':
                self.surface.blit(item['surf'], item['pos'])
            elif item['type'] == 'bush':
                self.surface.blit(item['surf'], item['pos'])
            elif item['type'] == 'bee':
                self.surface.blit(item['surf'], item['pos'])
            elif item['type'] == 'ladybug':
                self.surface.blit(item['surf'], item['pos'])
            elif item['type'] == 'mob':
                item['obj'].draw(self.surface)

        self.font = pygame.font.Font(None, 35)
        #self.surface.blit(self.path_icon, (50, 640))
        self.text = self.font.render(f'Tiles', True, (0, 0, 0))
        self.surface.blit(self.text, (750, 450))
        self.text = self.font.render(f'Remaining: {self.paths_remaining}', True, (0, 0, 0))
        self.surface.blit(self.text, (750, 485))
        
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
        self.world_grid = copy.deepcopy(PRESET_WORLD)

    def run_event_loop(self) -> None:
        while True:
            events = pygame.event.get()
            ### FOR WAVES SYSTEM
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
                        if not self.round_active:
                            self.reset_grid()
                            self.edit_mode = True
                            self.round_active = False

                    if event.key == pygame.K_SPACE:
                        if self.is_grid_valid(self.world_grid, GRID_SIZE) and not self.round_active and self.round_ended:
                            self.edit_mode = False
                            self.round_active = True
                            self.round_ended = False
                            self.mobs_to_spawn = 10 
                            # Set timer to trigger SPAWN_MOB_EVENT every 1000ms (1 second)
                            pygame.time.set_timer(self.SPAWN_MOB_EVENT, 1000)

                elif event.type == self.SPAWN_MOB_EVENT:
                    self.round_ended = False
                    if self.mobs_to_spawn > 0:
                        pts = self.get_path_waypoints()
                        new_mob = Mob(pts, self.spriteSize, DEFAULT_WIDTH/2, 50)
                        self.mobs.append(new_mob)
                        self.mobs_to_spawn -= 1
                    else:
                        pygame.time.set_timer(self.SPAWN_MOB_EVENT, 0)
                elif event.type == pygame.KEYUP:
                    pass
            if self.round_active and self.mobs_to_spawn == 0 and len(self.mobs) == 0:
                self.round_active = False
                self.round_ended = True
                self.edit_mode = True
                # Optional: self.paths_remaining = MAX_TILES # Reset tiles for next round?

            self.draw_window()
            self.clock.tick(60)

# ========

if __name__ == "__main__":
    q = Game()
    q.run_app()

