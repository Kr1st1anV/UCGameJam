import os
import sys
import pygame
import copy
import numpy as np
from maps import Maps
import random
from start_screen import StartScreen

DEFAULT_BGCOLOR = (137, 207, 240)
DEFAULT_WIDTH   = 978
DEFAULT_HEIGHT  = 750
GRID_SIZE = 10
MAX_TILES = 25
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'tiles')
BGROUND_DIR = os.path.join(os.path.dirname(__file__), 'bground')
TOWERS_DIR = os.path.join(os.path.dirname(__file__), 'towers')
BUTTONS_DIR = os.path.join(os.path.dirname(__file__), 'buttons')
MOBS_DIR = os.path.join(os.path.dirname(__file__), 'mobs')

rgb = tuple[int,int,int]
num = random.randint(1,5)
PRESET_WORLD = Maps().levels[6]

#SPRITES_DIR = os.path.join(ASSETS_DIR, 'sprites')

'''
PRESET_WORLD = [[0, -1, 0, 0, "l1", 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, "b2", 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0, "b2", 0], 
                [0, "l1", 0, "b2", 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, "l1", 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, -9, 0, 0, 0, 0], 
                [0, 0, "b2", 0, 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, "b2", 0, 0], 
                [0, 0, 0, 0, "l1", 0, 0, 0, 0, -8], 
                [0, 0, 0, 0, 0, 0, 0, 0, 0, -1]]
'''
class Mob:
    def __init__(self, grid_coords, sprite_size, pivot_x, pivot_y, mob_type=None):
        self.health = 10
        self.waypoints = []
        w, h = sprite_size
        half_w, half_h = w / 2, h / 4
        pivot_x = DEFAULT_WIDTH /3
        pivot_y = 125 * 2.6
        self.mobtype = [['worm moving_0001.png', 'worm moving_0002.png', 'worm moving_0003.png', 'worm moving_0004.png'],
                        ['butterfly_0001.png', 'butterfly_0002.png', 'butterfly_0003.png', 'butterfly_0004.png'],
                        ['dragonfly flying_0001.png', 'dragonfly flying_0002.png', 'dragonfly flying_0003.png', 'dragonfly flying_0004.png'],
                        ['snail idle_0001.png', 'snail idle_0002.png', 'snail idle_0003.png', 'snail idle_0004.png'],
                        ['beetle_0001.png', 'beetle_0002.png', 'beetle_0003.png', 'beetle_0004.png']]
        self.mob_dmg = [1, 5, 10, 20, 50]
        self.mob_speed = [3, 5, 5, 2, 3]
        self.mob_health_values = [10, 20, 50, 100, 200]
        self.mob_cost = [1, 5, 10, 20, 50]
        
        if mob_type is not None:
            self.randmob = mob_type
        else:
            self.randmob = random.randint(0, len(self.mobtype) - 1)
        self.health = self.mob_health_values[self.randmob]
        self.dmg = self.mob_dmg[self.randmob]
        print(f"Spawned mob type {self.randmob} with {self.health} health")
        print(f"Spawned mob type {self.randmob} with {self.dmg} dmg")

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

        self.mobframes_right = [self.load_mob(f) for f in self.mobtype[self.randmob]]
        self.mobframes_left = [pygame.transform.flip(f, True, False) for f in self.mobframes_right]
    
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
                current_sprite = self.mobframes_left[self.current_frame]
            else:
                current_sprite = self.mobframes_right[self.current_frame]

        sprite_rect = current_sprite.get_rect(center=(self.pos.x, self.pos.y))
        surface.blit(current_sprite, sprite_rect)

        if self.health > 0:
            bar_width = 40
            health_pct = self.health / self.mob_health_values[self.randmob]
            pygame.draw.rect(surface, (255, 0, 0), (self.pos.x - 20, self.pos.y - 40, bar_width, 5))
            pygame.draw.rect(surface, (0, 255, 0), (self.pos.x - 20, self.pos.y - 40, bar_width * health_pct, 5))

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
        self.ui_hitboxes = {}
        self.x = 0
        self.y = 0
        self.set_path = False
        self.rm_path = False
        self.paths_remaining = MAX_TILES
        self.reset_grid()
        self.edit_mode = True
        self.build = True
        self.wave = 1

        self.highlight = True

        self.round_active = False
        self.round_ended = True
        
        self.SPAWN_MOB_EVENT = pygame.USEREVENT + 1
        self.mobs = [] # List to track all active mobs
        self.selected_mob_type = 0
        self.mobs_to_spawn = 0
        self.mob_spawn_number = [10,12,12,15,15,20,20,20,20]
        self.points = 0

        self.branches = [10,10,10]
        self.current_branches = self.branches[self.wave-1]

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
    
    def initiate_tree_health_bars(self):
        self.health_frames = []
        # The specific percentages you mentioned
        self.health_steps = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 1, 0]
        
        for percent in self.health_steps:
            # Assumes files are named '100.png', '90.png', etc.
            path = os.path.join(os.path.dirname(__file__), 'tree_health', f'hb{percent}.png')
            img = pygame.image.load(path).convert_alpha()
            # Scale it to a size that fits above your tree
            img = pygame.transform.scale(img, (int(img.get_width() * 0.7), int(img.get_height() * 0.7)))
            self.health_frames.append(img)
            
        # Initialize the tree health variable
        self.tree_health = 1000
    
    def initiate_blocks(self):
        scale_factor = 1.5
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
        self.spriteSize = (self.tiles["dark_grass"].get_width(), self.tiles["dark_grass"].get_height())
        self.h_tiles = {name : self.highlight_block(tile) for name, tile in self.tiles.items()}

    def initiate_towers(self):
        scale_factor = 1.5
        self.tower_data = {} # Stores frames: self.tower_data["bee"]["idle"] = [...]
        self.tower_states = {} # Stores cooldowns: self.tower_states[(i, j)] = last_attack_time

        for t_type in ["bee", "ladybug", "bush", "tree"]:
            self.tower_data[t_type] = {"idle": [], "attack": []}
            for state in ["idle", "attack"]:
                folder = os.path.join(TOWERS_DIR, t_type, state) # e.g., towers/bee/attack/
                if os.path.exists(folder):
                    files = sorted(os.listdir(folder))
                    for f in files:
                        img = pygame.image.load(os.path.join(folder, f)).convert_alpha()
                        scaled = pygame.transform.scale(img, (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor)))
                        self.tower_data[t_type][state].append(scaled)

    def initiate_clouds(self):
        self.clouds = {}
        self.cloud1 = self.load_world('cloud1.png')
        self.clouds["cloud1"] = self.cloud1 = pygame.transform.scale(self.cloud1,(int(self.cloud1.get_width() * 1), int(self.cloud1.get_height() *1)))
        self.cloud2 = self.load_world('cloud2.png')
        self.clouds["cloud2"] = self.temp_tile = pygame.transform.scale(self.cloud2,(int(self.cloud2.get_width() * 1), int(self.cloud2.get_height() * 1)))
        # Load and scale your images
        self.cloud_images = [
            pygame.transform.scale(self.load_world('cloud1.png'), (int(self.cloud1.get_width() * 1), int(self.cloud1.get_height() * 1))),
            pygame.transform.scale(self.load_world('cloud2.png'), (int(self.cloud2.get_width() * 1), int(self.cloud2.get_height() * 1)))
        ]
        
        # This list will hold dictionaries of active clouds
        self.active_clouds = []
        
        # Spawn a few initial clouds so the sky isn't empty at the start
        for _ in range(1):
            self.spawn_cloud(random.randint(0, 700))

    def update_and_draw_clouds(self):
        for cloud in self.active_clouds[:]: # Use [:] to safely remove items while looping
            # Move the cloud
            cloud["x"] += cloud["speed"]
            
            # Draw the cloud
            self.surface.blit(cloud["image"], (cloud["x"], cloud["y"]))
            
            # If the cloud goes off the right side of the screen, remove it and spawn a new one
            if cloud["x"] > 700:
                self.active_clouds.remove(cloud)
                self.spawn_cloud() # This spawns a new one at the default -300 x

    def spawn_cloud(self, x_pos=None):
        # If no x_pos is given, start it off-screen to the left
        if x_pos is None:
            x_pos = -300 
            
        new_cloud = {
            "image": random.choice(self.cloud_images),
            "x": x_pos,
            "y": random.randint(20, 50), # Random height in the sky
            "speed": random.uniform(0.2, 0.8) # Varied floating speeds
        }
        self.active_clouds.append(new_cloud)
        

    def run_app(self) -> None:
        pygame.init()
        pygame.display.set_caption("Power Offense")
        self.surface = pygame.display.set_mode((self.width,self.height))
        self.showing_start_screen = True
        self.showing_settings_screen = False
        self.showing_instructions_scene = False
        self.start_screen = StartScreen(self.surface)
        self.clock = pygame.time.Clock()
        self.initiate_blocks()
        self.initiate_towers()
        self.initiate_clouds()
        self.initiate_tree_health_bars()
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
        pivot_y = 125 * 2.6

        rel_x = self.x - pivot_x
        rel_y = self.y - pivot_y

        mouse_j = (rel_x / half_w + rel_y / half_h) / 2
        mouse_i = (rel_y / half_h - rel_x / half_w) / 2

        grid_i, grid_j = int(np.floor(mouse_i)), int(np.floor(mouse_j))

        self.hovered_tower_type = None 

        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):

                draw_x = pivot_x + (j - i) * half_w - half_w
                draw_y = pivot_y + (j + i) * half_h

                # Hover effect
                # For Towers
                if i == grid_i and j == grid_j:
                    tile_value = self.world_grid[i][j]
                    if tile_value in [-9, -8, "b2", "l1"]:
                        self.hovered_tower_type = tile_value
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
                        sprite = self.get_spawn_sprite(i, j)
                        self.surface.blit(sprite, (draw_x, draw_y))
                        valid_path = self.is_grid_valid(self.world_grid, GRID_SIZE)
                        if valid_path:
                            #Show a Space bar - Start Round
                            pass
                        else:
                            pass
                            #Disable a Space bar - Start Round
                else:
                    if self.world_grid[i][j] == 0:
                        self.surface.blit(self.tiles["dark_grass"], (draw_x, draw_y)) # Grass
                    elif self.world_grid[i][j] == 1:
                        sprite = self.get_path_sprite(i, j)
                        self.surface.blit(sprite, (draw_x, draw_y))
                    elif self.world_grid[i][j] == -1:
                        sprite = self.get_spawn_sprite(i, j)
                        self.surface.blit(sprite, (draw_x, draw_y))
                        valid_path = self.is_grid_valid(self.world_grid, GRID_SIZE)
                        if valid_path:
                            #Show a Space bar - Start Round
                            pass
                        else:
                            pass
                            #Disable a Space bar - Start Round
                    elif self.world_grid[i][j] == "l1" or self.world_grid[i][j] == "b2":
                        self.surface.blit(self.tiles["red"], (draw_x, draw_y)) # Red
                    elif self.world_grid[i][j] == -3:
                        self.surface.blit(self.tiles["white"], (draw_x, draw_y)) # White
                    elif self.world_grid[i][j] == -9:
                        self.surface.blit(self.tiles["red"], (draw_x, draw_y)) # Tree
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

        mapping = {
            "tltrblbr": "4way",

            "tltrbr":   "3waytl",
            "tltrbl":   "3waytr",
            "tlblbr":   "3waybr",
            "trblbr":   "3waybl",

            "tlbr":     "posdia",
            "trbl":     "negdia",
            "blbr":     "blbr",   
            "tltr":     "tltr",  
            "tlbl":     "trbr",   
            "trbr":     "tlbl",   

            "tl":       "endbl",
            "tr":       "endbr",
            "bl":       "endtl",
            "br":       "endtr"
        }

        tile_name = mapping.get(key, "path") 
        return self.tiles.get(tile_name, self.tiles["path"])
    
    def get_spawn_sprite(self, i, j):
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

        mapping = {
            "tl":       "grey_bl",
            "tr":       "grey_br",
            "bl":       "grey_tl",
            "br":       "grey_tr"
        }

        tile_name = mapping.get(key, "grey") 
        return self.tiles.get(tile_name, self.tiles["grey"])
    

    # Tower Mechanics
    def handle_tower_logic(self):
        now = pygame.time.get_ticks()
        stats = {"b2": [150, 5, 1000], "l1": [120, 3, 800]} 
        
        w, h = self.spriteSize
        half_w, half_h = w / 2, h / 4
        pivot_x, pivot_y = DEFAULT_WIDTH / 3, 125 * 2.6

        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                tile = self.world_grid[i][j]
                if tile in stats:
                    t_type = "bee" if tile == "b2" else "ladybug"
                    tower_key = (i, j)
                    
                    if tower_key not in self.tower_states:
                        # Added 'flip': False to the initial state
                        self.tower_states[tower_key] = {"last_atk": 0, "frame": 0, "status": "idle", "flip": False}

                    t_pos = pygame.Vector2(pivot_x + (j - i) * half_w, pivot_y + (j + i) * half_h - (h * 1.2))
                    in_range = [m for m in self.mobs if t_pos.distance_to(m.pos) <= stats[tile][0]]
                    
                    if in_range:
                        target = max(in_range, key=lambda m: m.target_idx)
                        
                        # --- NEW TRACKING LOGIC ---
                        # If mob's x is less than tower's x, it's on the left
                        if target.pos.x < t_pos.x:
                            self.tower_states[tower_key]["flip"] = False
                        else:
                            self.tower_states[tower_key]["flip"] = True
                        # --------------------------

                        if now - self.tower_states[tower_key]["last_atk"] > stats[tile][2]:
                            target.health -= stats[tile][1]
                            self.tower_states[tower_key]["last_atk"] = now
                            self.tower_states[tower_key]["status"] = "attack"
                            self.tower_states[tower_key]["frame"] = 0
                    
                    # Update animation frame
                    state = self.tower_states[tower_key]["status"]
                    self.tower_states[tower_key]["frame"] += 0.15
                    if self.tower_states[tower_key]["frame"] >= len(self.tower_data[t_type][state]):
                        self.tower_states[tower_key]["frame"] = 0
                        if state == "attack":
                            self.tower_states[tower_key]["status"] = "idle"
                            # pygame.draw.line(self.surface, (255, 255, 0), tower_pos, target_mob.pos, 2)
    
    def draw_UI(self) -> None: 
        #scale fix
        bookofevil = self.load_world('scriptofevilbutton.png')
        scale_fix_boe = pygame.transform.scale(bookofevil, (int(bookofevil.get_width() * 0.7), int(bookofevil.get_height() * 0.7)))
        bookoflife = self.load_world('bookoflifebutton.png')
        scale_fix_bol = pygame.transform.scale(bookoflife, (int(bookoflife.get_width() * 0.7), int(bookoflife.get_height() * 0.7)))
        scroll = self.load_world('emptyscroll.png')
        scale_fix_scroll = pygame.transform.scale(scroll, (int(scroll.get_width() * 0.35), int(scroll.get_height() * 0.35)))

        ##### UI PRESS #####
        boe_rect = scale_fix_boe.get_rect(topleft=(673, 525))
        self.ui_hitboxes['book_of_evil'] = boe_rect.inflate(-40, -40)

        bol_rect = scale_fix_bol.get_rect(topleft=(673, 350))
        self.ui_hitboxes['book_of_life'] = bol_rect.inflate(-20, -200)
        #########################

        self.font = pygame.font.Font(os.path.join(os.path.join(os.path.dirname(__file__), 'fonts'), "Dico.ttf"), 35)
        romanNumeral = self.intToRoman(self.wave)
        self.wave_text = self.font.render("Wave: " + romanNumeral, True, (0, 0, 0))
        self.mobs_text = self.font.render(f'Mobs: {self.mobs_to_spawn}', True, (0, 0, 0))
        #self.points_text = self.font.render(f'Points: {self.points}', True, (0, 0, 0))
        self.branches_text = self.font.render(f':  {self.current_branches}', True, (0, 0, 0))
        self.units_text = self.font.render(f'Units:', True, (0, 0, 0))
        self.surface.blit(self.wave_text, (50, 70))
        self.surface.blit(self.branches_text, (735, 45))
        self.surface.blit(self.units_text, (1130, 550))

        
        # self.settings = self.load_world('settings.png')
        # self.settings = pygame.transform.scale(self.settings, (int(self.settings.get_width() * 0.7), int(self.settings.get_height() * 0.7)))
        # self.surface.blit(self.settings, (760, 645))
        # self.surface.blit(scale_fix_boe, (673, 525))
        # self.surface.blit(scale_fix_bol, (673, 350))
        #self.surface.blit(scale_fix_scroll, (670, 230)) THIS IS THE SCROLL
    
    def ui_check_click(self, mouse_pos):
        if 'book_of_evil' in self.ui_hitboxes and self.ui_hitboxes['book_of_evil'].collidepoint(mouse_pos):
            return "BOOK_OF_EVIL"
        if 'book_of_life' in self.ui_hitboxes and self.ui_hitboxes['book_of_life'].collidepoint(mouse_pos):
            return "BOOK_OF_LIFE"
        return None

    def get_health_frame(self):
        current_pct = max(0, self.tree_health)
        
        for i, step in enumerate(self.health_steps):
            if current_pct >= step:
                return self.health_frames[i]
        
        return self.health_frames[-1]
    
    def draw_tree_of_life(self):
        if self.tree_health > 0 and self.wave <= 20:
            current_health_img = self.get_health_frame()
            self.surface.blit(current_health_img, (40, 630))
        else:
            print("Game Over")
            pass

    def intToRoman(self, num):
        Roman = ""
        storeIntRoman = [[1000, "M"], [900, "CM"], [500, "D"], [400, "CD"], [100, "C"], [90, "XC"], [50, "L"], [40, "XL"], [10, "X"], [9, "IX"], [5, "V"], [4, "IV"], [1, "I"]]
        for i in range(len(storeIntRoman)):
            while num >= storeIntRoman[i][0]:
                Roman += storeIntRoman[i][1]
                num -= storeIntRoman[i][0]
        return Roman

    def get_object_layers(self):
        w, h = self.spriteSize
        half_w, half_h = w / 2, h / 4
        pivot_x, pivot_y = DEFAULT_WIDTH / 3, 125 * 2.6

        rel_x, rel_y = self.x - pivot_x, self.y - pivot_y
        mouse_j = (rel_x / half_w + rel_y / half_h) / 2
        mouse_i = (rel_y / half_h - rel_x / half_w) / 2
        grid_i, grid_j = int(np.floor(mouse_i)), int(np.floor(mouse_j))        
        # Subtle Up/Down: Sine wave based on time
        # 5 is the pixel height of the bob, 0.005 is the speed
        bobbing_offset = np.sin(pygame.time.get_ticks() * 0.005) * 5

        tree_elements = []
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                # Inside get_object_layers loop for 'b2' (Bee) or 'l1' (Ladybug):
                tile_val = self.world_grid[i][j]
            
                if tile_val in ["b2", "l1"]:
                    draw_x = pivot_x + (j - i) * half_w - half_w
                    draw_y = pivot_y + (j + i) * half_h
                    
                    t_type = "bee" if tile_val == "b2" else "ladybug"
                    state_info = self.tower_states.get((i, j), {"frame": 0, "status": "idle", "flip": False})
                    
                    # Get the current frame
                    frames = self.tower_data[t_type][state_info["status"]]
                    if len(frames) > 0:
                        surf = frames[int(state_info["frame"]) % len(frames)].copy()
                        
                        # --- GLOBAL HIGHLIGHT LOGIC ---
                        # If this tower type is the one we are hovering over, dim ALL of them
                        if tile_val == self.hovered_tower_type:
                            surf.set_alpha(100) # Highlighted look
                        else:
                            surf.set_alpha(255) # Normal look
                        # ------------------------------

                        if state_info["flip"]:
                            surf = pygame.transform.flip(surf, True, False)

                        tree_elements.append({
                            'z': draw_y, 
                            'type': t_type, 
                            'surf': surf, 
                            'pos': (draw_x, (draw_y - h * 1.2) + bobbing_offset)
                        })
                if tile_val in [-8, -9]:
                    draw_x = pivot_x + (j - i) * half_w - half_w
                    draw_y = pivot_y + (j + i) * half_h
                    
                    t_type = "tree" if tile_val == -9 else "bush"
                    state_info = self.tower_states.get((i, j), {"frame": 0, "status": "idle", "flip": False})
                    
                    # Get the current frame
                    frames = self.tower_data[t_type][state_info["status"]]
                    if len(frames) > 0:
                        surf = frames[int(state_info["frame"]) % len(frames)].copy()

                        if tile_val == -9:
                            surf = pygame.transform.scale(surf,(int(surf.get_width() * 2), int(surf.get_height() * 2)))
                        
                        # --- GLOBAL HIGHLIGHT LOGIC ---
                        # If this tower type is the one we are hovering over, dim ALL of them
                        if tile_val == self.hovered_tower_type:
                            surf.set_alpha(100) # Highlighted look
                        else:
                            surf.set_alpha(255) # Normal look
                        # ------------------------------

                        if state_info["flip"]:
                            surf = pygame.transform.flip(surf, True, False)
                        pos = (draw_x - w * 0.5, (draw_y - h * 1.3)) if tile_val == -9 else (draw_x + 5, draw_y - h * 0.35)
                        tree_elements.append({
                            'z': draw_y, 
                            'type': t_type, 
                            'surf': surf, 
                            'pos': pos
                        })   
                # elif self.world_grid[i][j] == -8:
                #     draw_x = pivot_x + (j - i) * half_w - half_w
                #     draw_y = pivot_y + (j + i) * half_h
                #     tree_surf = self.towers["bush"].copy()
                    
                #     tree_elements.append({
                #         'z': draw_y, 
                #         'type': 'bush', 
                #         'surf': tree_surf, 
                #         
                #     })
        return tree_elements
    


    def draw_window(self) -> None:
        if self.showing_start_screen:
            self.start_screen.draw()
            self.start_screen.draw_buttons()
            if self.showing_settings_screen:
                self.start_screen.draw_settings()
                if self.showing_instructions_scene:
                    self.start_screen.draw_instructions()
            pygame.display.update()
        else:
            self.surface.fill(self.bgcolor)
            self.background = self.load_world("wbsky.png")
            self.bg_image = pygame.transform.scale(self.background,(int(self.background.get_width() * 0.7), int(self.background.get_height() * 0.75)))
            self.surface.blit(self.bg_image, (0, 0))
            self.update_and_draw_clouds()
            self.island = self.load_world("island.png")
            self.island_image = pygame.transform.scale(self.island,(int(self.island.get_width() * 1), int(self.island.get_height() * 1.2)))
            self.surface.blit(self.island_image, (-100, 0))
            self.background = self.load_world("UI_play.png")
            self.bg_image = pygame.transform.scale(self.background,(int(self.background.get_width() * 0.7), int(self.background.get_height() * 0.75)))
            self.surface.blit(self.bg_image, (0, 0))
            self.map_grid()
            self.tree_life = self.load_world("tree_of_life.png")
            self.tree_life_img = pygame.transform.scale(self.tree_life,(int(self.tree_life.get_width() * 1.5), int(self.tree_life.get_height() * 1.5)))
            self.surface.blit(self.tree_life_img, (210, 30))
            self.draw_tree_of_life()
            #self.surface.blit(self.load_image('red.png'), (800, 600))
            #self.surface.blit(self.load_image('purple.png'), (840, 600))
            #self.surface.blit(self.load_image('water.png'), (880, 600))

            layer_queue = []
            layer_queue.extend(self.get_object_layers())

            if self.round_active:
                self.mobs = [m for m in self.mobs if m.health > 0]
                
                finished_mobs = [m for m in self.mobs if m.at_end]
                for m in finished_mobs:
                    self.tree_health -= m.dmg
                
                self.mobs = [m for m in self.mobs if not m.at_end]
                
                for mob in self.mobs:
                    mob.update()
                    layer_queue.append({
                        'z': mob.pos.y, 
                        'type': 'mob', 
                        'obj': mob
                    })

                self.handle_tower_logic()

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

            self.font = pygame.font.Font(os.path.join(os.path.join(os.path.dirname(__file__), 'fonts'), "Dico.ttf"), 25)
            #self.surface.blit(self.path_icon, (50, 640))
            self.text = self.font.render(f'Tiles Remaining: {self.paths_remaining}', True, (0, 0, 0))
            self.surface.blit(self.text, (40, 120))
            
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
                if self.showing_start_screen:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        action = None
                        if not self.showing_settings_screen and not self.showing_instructions_scene:
                            action = self.start_screen.check_click(event.pos)
                            if action == "START":
                                self.showing_start_screen = False
                            if action == "SETTINGS":
                                self.showing_settings_screen = True
                        elif self.showing_settings_screen and not self.showing_instructions_scene:
                            action = self.start_screen.check_settings(event.pos)
                            if action == "INSTRUCTIONS":
                                self.showing_instructions_scene = True
                            if action == "CLOSE":
                                self.showing_instructions_scene = False
                                self.showing_settings_screen = False
                        elif self.showing_settings_screen and self.showing_instructions_scene:
                            action = self.start_screen.check_closing_instructions(event.pos)
                            if action == "CLOSE":
                                self.showing_instructions_scene = False
                                self.showing_settings_screen = True
                else:
                    if event.type == pygame.MOUSEMOTION:
                        self.x, self.y = event.pos
                    elif event.type == pygame.MOUSEBUTTONDOWN: # 1 is left, 3 is right
                        if event.button == 1:
                            ui_action = self.ui_check_click(event.pos)
                            if ui_action == "BOOK_OF_EVIL":
                                print("Book of evil was clicked")
                            elif ui_action == "BOOK_OF_LIFE":
                                print("Book of life was clicked")
                            else:
                                if self.build:
                                    self.set_path = True
                                else:
                                    self.rm_path = True
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1:
                            self.set_path = False
                            self.rm_path = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            if not self.round_active:
                                self.reset_grid()
                                self.edit_mode = True
                                self.round_active = False
                        if event.key == pygame.K_b:
                            self.build = not self.build
                        if event.key == pygame.K_1:
                            self.selected_mob_type = 0
                        if event.key == pygame.K_2:
                            if self.wave >= 2:
                                self.selected_mob_type = 1
                        if event.key == pygame.K_3:
                            if self.wave >= 4:
                                self.selected_mob_type = 2
                        if event.key == pygame.K_4:
                            if self.wave >= 8:
                                self.selected_mob_type = 3
                        if event.key == pygame.K_5:
                            if self.wave >= 12:
                                self.selected_mob_type = 4
                        if event.key == pygame.K_SPACE:
                            if self.is_grid_valid(self.world_grid, GRID_SIZE) and not self.round_active and self.round_ended:
                                self.edit_mode = False
                                self.round_active = True
                                self.round_ended = False
                                self.mobs_to_spawn = self.mob_spawn_number[self.wave-1]
                                pygame.time.set_timer(self.SPAWN_MOB_EVENT, 1000)

                    elif event.type == self.SPAWN_MOB_EVENT:
                        self.round_ended = False
                        if self.mobs_to_spawn > 0:
                            pts = self.get_path_waypoints()
                            new_mob = Mob(pts, self.spriteSize, DEFAULT_WIDTH/2, 50, self.selected_mob_type)
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
                self.wave += 1
                # Optional: self.paths_remaining = MAX_TILES # Reset tiles for next round?

            self.draw_window()
            if self.showing_start_screen:
                self.clock.tick(15)
                continue
            self.clock.tick(60)


# ========

if __name__ == "__main__":
    q = Game()
    q.run_app()

