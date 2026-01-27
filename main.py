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
ASSETS_UI_DIR = os.path.join(os.path.dirname(__file__), 'assets', 'ui')
ASSETS_MOBS_DIR = os.path.join(os.path.dirname(__file__), 'assets', 'mobs')

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
        self.mobcolor = [(200, 50, 50),(93, 63, 211),(0, 255, 255)]
        # Mob order: worm, butterfly, dragonfly, snail, beetle (matches script of evil order)
        # File names need to match what's in assets/mobs directories
        self.mobtype = [
            ['worm moving_0001.png', 'worm moving_0002.png', 'worm moving_0003.png', 'worm moving_0004.png'],  # 0: worm
            ['butterfly_0001.png', 'butterfly_0002.png', 'butterfly_0003.png', 'butterfly_0004.png'],  # 1: butterfly
            ['dragonfly flying_0001.png', 'dragonfly flying_0002.png', 'dragonfly flying_0003.png', 'dragonfly flying_0004.png'],  # 2: dragonfly
            ['snail idle_0001.png', 'snail idle_0002.png', 'snail idle_0003.png', 'snail idle_0004.png'],  # 3: snail
            ['beetle_0001.png', 'beetle_0002.png', 'beetle_0003.png', 'beetle_0004.png']  # 4: beetle
        ]
        # Health values in order: worm, butterfly, dragonfly, snail, beetle
        self.mob_health_values = [10, 50, 20, 100, 120]
        # Damage values in order: worm, butterfly, dragonfly, snail, beetle
        self.mob_dmg = [2, 4, 6, 3, 3]
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
        # Try assets directory first, then fall back to old mobs directory
        # Mob order: dragonfly, worm, butterfly, snail, beetle
        mob_folders = ['dragonfly', 'worm', 'butterfly', 'snail', 'beetle']
        mob_folder = None
        for folder in mob_folders:
            if folder in name.lower():
                mob_folder = folder
                break
        
        if mob_folder:
            # Try assets/mobs directory first
            assets_path = os.path.join(ASSETS_MOBS_DIR, mob_folder, name)
            if os.path.exists(assets_path):
                return pygame.image.load(assets_path).convert_alpha()
        
        # Fallback to old mobs directory
        path = os.path.join(MOBS_DIR, name)
        if os.path.exists(path):
            return pygame.image.load(path).convert_alpha()
        
        # If still not found, try assets/mobs with just the filename
        print(f"Warning: Could not find mob image {name}, trying direct path")
        return pygame.image.load(os.path.join(MOBS_DIR, name)).convert_alpha()

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
        #########
        self.showing_scroll = False
        self.showing_book = False
        self.scroll_page = 0  # Current page in script of evil (0-4 for 5 mobs)
        self.cached_mob_icons = {}  # Cache mob icons for spawn boxes
        self.showing_surrender = False  # Surrender screen
        self.debug_click_mode = True  # Print mouse positions on click for hitbox debugging
        ########
        self.set_path = False
        self.rm_path = False
        self.paths_remaining = MAX_TILES
        self.reset_grid()
        self.edit_mode = True
        self.build = True
        self.mob_spawn_number = [10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10]
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
        
        # Cache for rendered text surfaces to avoid re-rendering every frame
        self.cached_text_surfaces = {}
        self.last_wave = 0
        self.last_mobs_to_spawn = -1
        self.last_branches = -1
        self.last_paths_remaining = -1        

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
    
    def initiate_cutscenes(self):
        self.game_active = True
        self.cutscene_frame = 0
        self.cutscene_images = []
        self.cutscene_timer = 0
        self.animation_speed = 100 # Milliseconds per frame
        self.showing_cutscene = False
        self.cutscene_played_once = False  # For testing: track if win cutscene has been shown
        self.cutscene_skip_delay = 0  # Prevent immediate skipping
        self.cutscene_finished = False  # Track if cutscene has reached the last frame

    def load_cutscene(self, folder_name, return_to_start=False):
        # Prevent reloading if cutscene is already showing
        if self.showing_cutscene and len(self.cutscene_images) > 0:
            print("Cutscene already loaded, skipping reload")
            return
        
        # Reset all cutscene state before loading
        self.cutscene_images = []
        self.cutscene_frame = 1  # Start one frame ahead
        self.cutscene_finished = False
        
        # Don't set showing_cutscene until images are loaded to prevent showing stale frames
        self.game_active = False
        self.cutscene_return_to_start = return_to_start  # Track if we should return to start screen after cutscene
        path = os.path.join(os.path.dirname(__file__), 'cutscenes', folder_name)
        
        # Load all images in the folder sorted by name (natural sort for f1, f2, f10, etc.)
        try:
            import re
            def natural_sort_key(text):
                # Extract number from filename for proper sorting (f1, f2, f10 instead of f1, f10, f2)
                match = re.search(r'(\d+)', text)
                return int(match.group(1)) if match else 0
            files = sorted([f for f in os.listdir(path) if f.endswith('.png')], key=natural_sort_key)
            print(f"Loading cutscene from {folder_name}: found {len(files)} images")
            if len(files) == 0:
                print(f"ERROR: No PNG files found in {path}")
                self.showing_cutscene = False
                return
            
            for f in files:
                img_path = os.path.join(path, f)
                img = pygame.image.load(img_path).convert_alpha()
                # Scale to screen size
                img = pygame.transform.scale(img, (self.width, self.height))
                self.cutscene_images.append(img)
            
            # Now that all images are loaded, set showing_cutscene and initialize frame
            # Start from frame 1 (one frame ahead) if we have enough frames
            if len(self.cutscene_images) > 1:
                self.cutscene_frame = 1
            else:
                self.cutscene_frame = 0
            self.cutscene_timer = pygame.time.get_ticks()
            self.cutscene_skip_delay = pygame.time.get_ticks() + 500  # Prevent skipping for 500ms
            self.cutscene_finished = False  # Reset finished flag when loading new cutscene
            self.showing_cutscene = True  # Only set this after images are loaded
            print(f"Cutscene loaded: {len(self.cutscene_images)} frames, showing_cutscene={self.showing_cutscene}, showing_start_screen={self.showing_start_screen}")
        except Exception as e:
            print(f"ERROR loading cutscene: {e}")
            self.showing_cutscene = False

    def victory(self):
        if self.game_active: # Prevent reloading every frame
            print("Victory! Loading animation...")
            # Load victory cutscene and return to main menu when finished
            self.load_cutscene('victory', return_to_start=True)

    def defeat(self):
        if self.game_active:
            print("Defeat! Loading animation...")
            # Load defeat cutscene and return to main menu when finished
            self.load_cutscene('defeat', return_to_start=True)
    
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
        self.tree_health = 2500
    
    def initiate_cached_images(self):
        """Pre-load and cache all background images to avoid loading every frame"""
        try:
            # Background images
            background_raw = self.load_world("wbsky.png")
            self.cached_bg_image = pygame.transform.scale(background_raw, (int(background_raw.get_width() * 0.7), int(background_raw.get_height() * 0.75)))
            
            island_raw = self.load_world("island.png")
            self.cached_island_image = pygame.transform.scale(island_raw, (int(island_raw.get_width() * 1), int(island_raw.get_height() * 1.2)))
            
            ui_raw = self.load_world("UI_play.png")
            self.cached_ui_image = pygame.transform.scale(ui_raw, (int(ui_raw.get_width() * 0.7), int(ui_raw.get_height() * 0.75)))
            
            tree_life_raw = self.load_world("tree_of_life.png")
            self.cached_tree_life_image = pygame.transform.scale(tree_life_raw, (int(tree_life_raw.get_width() * 1.5), int(tree_life_raw.get_height() * 1.5)))
            
            # UI images - load from assets/ui
            bookofevil_raw = pygame.image.load(os.path.join(ASSETS_UI_DIR, 'buttons', 'scriptofevilbutton.png')).convert_alpha()
            self.cached_bookofevil = pygame.transform.scale(bookofevil_raw, (int(bookofevil_raw.get_width() * 0.7), int(bookofevil_raw.get_height() * 0.7)))
            
            bookoflife_raw = pygame.image.load(os.path.join(ASSETS_UI_DIR, 'buttons', 'bookoflifebutton.png')).convert_alpha()
            self.cached_bookoflife = pygame.transform.scale(bookoflife_raw, (int(bookoflife_raw.get_width() * 0.7), int(bookoflife_raw.get_height() * 0.7)))
            
            # Load scroll images for each mob type (script of evil) - order: worm, butterfly, dragonfly, snail, beetle
            self.cached_scrolls = {}
            scroll_names = ['scrollworm.png', 'scrollbutterfly.png', 'scrolldragonfly.png', 'scrollsnail.png', 'scrollbeetle.png']
            for i, scroll_name in enumerate(scroll_names):
                scroll_raw = pygame.image.load(os.path.join(ASSETS_UI_DIR, 'scroll', scroll_name)).convert_alpha()
                self.cached_scrolls[i] = pygame.transform.scale(scroll_raw, (int(scroll_raw.get_width() * 0.8), int(scroll_raw.get_height() * 0.8)))
            
            # Book of life - use book1.png from assets
            book_of_lifeopen_raw = pygame.image.load(os.path.join(ASSETS_UI_DIR, 'book', 'book1.png')).convert_alpha()
            self.cached_book_of_lifeopen = pygame.transform.scale(book_of_lifeopen_raw, (int(book_of_lifeopen_raw.get_width() * 0.55), int(book_of_lifeopen_raw.get_height() * 0.55)))
            
            # Surrender page
            surrender_raw = pygame.image.load(os.path.join(ASSETS_UI_DIR, 'surrenderpage.png')).convert_alpha()
            self.cached_surrender_page = pygame.transform.scale(surrender_raw, (int(surrender_raw.get_width() * 0.8), int(surrender_raw.get_height() * 0.8)))
            
            # Spawn box image
            woodbox_raw = self.load_world('woodbox.png')
            self.cached_woodbox = pygame.transform.scale(woodbox_raw, (int(woodbox_raw.get_width() * 0.8), int(woodbox_raw.get_height() * 0.8)))
            
            # Load hammer cursor images (for build mode)
            self.hammer_images = []
            hammer_dir = os.path.join(ASSETS_UI_DIR, 'hammer')
            if os.path.exists(hammer_dir):
                hammer_files = sorted([f for f in os.listdir(hammer_dir) if f.endswith('.png')])
                for hammer_file in hammer_files:
                    hammer_img = pygame.image.load(os.path.join(hammer_dir, hammer_file)).convert_alpha()
                    # Scale hammer to reasonable cursor size
                    self.hammer_images.append(pygame.transform.scale(hammer_img, (40, 40)))
            
            # Create pixel art style shovel cursor (for delete mode)
            # Make it match the pixel art style of the game
            shovel_surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            # Pixel art shovel - brown handle, gray metal head
            # Handle (vertical brown rectangle)
            for y in range(2, 18):
                for x in range(14, 18):
                    shovel_surf.set_at((x, y), (101, 67, 33))  # Brown handle
            
            # Shovel head (gray metal, angled)
            # Top edge
            for x in range(6, 22):
                shovel_surf.set_at((x, 18), (128, 128, 128))
            # Left edge
            for y in range(18, 26):
                shovel_surf.set_at((6, y), (128, 128, 128))
            # Right edge (curved)
            for y in range(18, 26):
                shovel_surf.set_at((21, y), (128, 128, 128))
            # Fill shovel head
            for y in range(19, 25):
                for x in range(7, 21):
                    shovel_surf.set_at((x, y), (192, 192, 192))
            # Shovel tip
            for x in range(8, 20):
                shovel_surf.set_at((x, 25), (160, 160, 160))
            
            # Scale up to match hammer size
            self.shovel_image = pygame.transform.scale(shovel_surf, (40, 40))
            
            # Initialize cursor animation variables
            self.cursor_animation_frame = 0
            self.cursor_animation_counter = 0
            self.hammer_animating = False
            self.hammer_animation_duration = 0
            self.tile_changed = False
            
            # Cache mob icons for spawn boxes - order: worm, butterfly, dragonfly, snail, beetle
            mob_names = ['worm', 'butterfly', 'dragonfly', 'snail', 'beetle']
            for i, mob_name in enumerate(mob_names):
                try:
                    mob_folder = os.path.join(ASSETS_MOBS_DIR, mob_name)
                    if os.path.exists(mob_folder):
                        mob_files = sorted([f for f in os.listdir(mob_folder) if f.endswith('.png') and 'flipped' not in f.lower()])
                        if mob_files:
                            mob_icon = pygame.image.load(os.path.join(mob_folder, mob_files[0])).convert_alpha()
                            # Scale to fit in box (woodbox is typically around 30x30)
                            self.cached_mob_icons[i] = pygame.transform.scale(mob_icon, (25, 25))
                except Exception as e:
                    print(f"Error caching mob icon for {mob_name}: {e}")
            
            print("Cached images initialized successfully")
        except Exception as e:
            print(f"Error initializing cached images: {e}")
            import traceback
            traceback.print_exc()
    
    def initiate_cached_fonts(self):
        """Pre-load fonts to avoid creating them every frame"""
        font_path = os.path.join(os.path.join(os.path.dirname(__file__), 'fonts'), "Dico.ttf")
        self.cached_font_large = pygame.font.Font(font_path, 35)
        self.cached_font_medium = pygame.font.Font(font_path, 25)
    
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
        self.initiate_cutscenes()
        self.initiate_blocks()
        self.initiate_towers()
        self.initiate_clouds()
        self.initiate_tree_health_bars()
        self.initiate_cached_images()  # Pre-load and cache background images
        self.initiate_cached_fonts()  # Pre-load fonts
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
                is_hovered = (i == grid_i and j == grid_j)
                if is_hovered:
                    tile_value = self.world_grid[i][j]
                    if tile_value in [-9, -8, "b2", "l1"]:
                        self.hovered_tower_type = tile_value
                
                # Handle path editing
                if self.edit_mode and type(self.world_grid[i][j]) == int and self.world_grid[i][j] >= 0 and is_hovered:
                    self.highlight = True
                    if self.set_path and self.paths_remaining > 0:
                        if  self.world_grid[i][j] != 1:
                            self.world_grid[i][j] = 1
                            self.paths_remaining -= 1
                            # Trigger hammer animation when tile changes
                            self.tile_changed = True
                            self.hammer_animating = True
                            self.hammer_animation_duration = 0.5  # Animation duration in seconds
                    elif self.rm_path:
                        if  self.world_grid[i][j] != 0:
                            self.world_grid[i][j] = 0
                            self.paths_remaining += 1
                            # Trigger hammer animation when tile changes
                            self.tile_changed = True
                            self.hammer_animating = True
                            self.hammer_animation_duration = 0.5  # Animation duration in seconds
                else:
                    self.highlight = False
                
                # Draw tiles with hover highlighting based on B key state
                # When B is pressed (build = False, delete mode): highlight path tiles on hover
                # When B is not pressed (build = True, build mode): highlight grass tiles on hover
                if self.world_grid[i][j] == 0:
                    # Grass tile - highlight on hover if in build mode (B not pressed)
                    if is_hovered and self.build:
                        self.surface.blit(self.h_tiles["dark_grass"], (draw_x, draw_y)) # Highlighted Grass
                    else:
                        self.surface.blit(self.tiles["dark_grass"], (draw_x, draw_y)) # Normal Grass
                elif self.world_grid[i][j] == 1:
                    # Path tile - highlight on hover if in delete mode (B pressed)
                    sprite = self.get_path_sprite(i, j)
                    if is_hovered and not self.build:
                        # Highlight path tiles when hovered in delete mode
                        highlighted_sprite = self.highlight_block(sprite)
                        self.surface.blit(highlighted_sprite, (draw_x, draw_y))
                    else:
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

    def find_all_ends(self):
        """Find all -1 positions (start and end points)"""
        ends = []
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if self.world_grid[i][j] == -1:
                    ends.append((i, j))
        return ends
    
    def can_reach_end(self, pos, target_end, visited_path, world_grid):
        """Check if a position can reach the target end without going through visited_path"""
        if pos == target_end:
            return True
        
        curr_i, curr_j = pos
        temp_visited = visited_path.copy()
        temp_visited.add(pos)
        
        # Try all neighbors
        for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            ni, nj = curr_i + di, curr_j + dj
            if 0 <= ni < GRID_SIZE and 0 <= nj < GRID_SIZE:
                val = world_grid[ni][nj]
                if (ni, nj) not in temp_visited and val in [1, -1]:
                    if self.can_reach_end((ni, nj), target_end, temp_visited, world_grid):
                        return True
        return False
    
    def get_path_waypoints(self):
        """Find path from start to end with smart intersection handling"""
        ends = self.find_all_ends()
        if len(ends) < 2:
            return []  # Need at least start and end
        
        # Sort ends by row (i coordinate) descending to get bottom-most first
        # Use bottom -1 as start (highest row index)
        ends_sorted = sorted(ends, key=lambda x: x[0], reverse=True)
        start_pos = ends_sorted[0]  # Bottom-most -1
        
        # Use top -1 as end (lowest row index) or furthest from start
        end_pos = ends_sorted[-1] if len(ends_sorted) > 1 else ends_sorted[0]
        
        # If multiple ends, find the one furthest from start as the target
        if len(ends) > 2:
            max_dist = 0
            for end in ends:
                if end != start_pos:
                    dist = abs(end[0] - start_pos[0]) + abs(end[1] - start_pos[1])
                    if dist > max_dist:
                        max_dist = dist
                        end_pos = end
        
        path_coords = [start_pos]
        visited = {start_pos}
        current = start_pos
        
        while current != end_pos:
            curr_i, curr_j = current
            
            # Find all valid neighbors (not visited, and are path tiles)
            valid_neighbors = []
            for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                ni, nj = curr_i + di, curr_j + dj
                if 0 <= ni < GRID_SIZE and 0 <= nj < GRID_SIZE:
                    val = self.world_grid[ni][nj]
                    if (ni, nj) not in visited and val in [1, -1]:
                        # Check if this path can reach the end (not a dead end)
                        if self.can_reach_end((ni, nj), end_pos, visited, self.world_grid):
                            # Calculate distance to end (heuristic)
                            dist_to_end = abs(ni - end_pos[0]) + abs(nj - end_pos[1])
                            valid_neighbors.append(((ni, nj), dist_to_end))
            
            if not valid_neighbors:
                # No valid path found, return what we have
                break
            
            # Sort by distance to end (closer is better)
            valid_neighbors.sort(key=lambda x: x[1])
            
            # Get all neighbors with the best (smallest) distance
            best_dist = valid_neighbors[0][1]
            best_neighbors = [n[0] for n in valid_neighbors if n[1] == best_dist]
            
            # If multiple best options, randomly choose one
            # Otherwise, take the best one
            if len(best_neighbors) > 1:
                # Randomly choose from best options (those closest to end)
                next_pos = random.choice(best_neighbors)
            else:
                next_pos = best_neighbors[0]
            
            path_coords.append(next_pos)
            visited.add(next_pos)
            current = next_pos
            
            # If we reached an end (-1), check if it's the target end
            if self.world_grid[current[0]][current[1]] == -1:
                if current == end_pos:
                    return path_coords
                # If it's a different end, we've reached a valid endpoint
                # Continue to see if we can reach the target end
        
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
                            # Mobs are invincible for debugging - damage disabled
                            # target.health -= stats[tile][1]
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
        # Show surrender screen if active
        if self.showing_surrender:
            if hasattr(self, 'cached_surrender_page'):
                # Center the surrender page on screen
                surrender_x = (self.width - self.cached_surrender_page.get_width()) // 2
                surrender_y = (self.height - self.cached_surrender_page.get_height()) // 2
                self.surface.blit(self.cached_surrender_page, (surrender_x, surrender_y))
                # Add close button hitbox (you may need to adjust this based on the surrender page design)
                self.ui_hitboxes['surrender_close'] = pygame.Rect(surrender_x + 200, surrender_y + 300, 100, 50)
                pygame.draw.rect(self.surface, (255, 0, 0), self.ui_hitboxes['surrender_close'], 2)  # Red outline
        
        # Use cached images instead of loading every frame
        if self.showing_scroll:
            # Show the scroll for the current page (script of evil navigation)
            if self.scroll_page in self.cached_scrolls:
                self.surface.blit(self.cached_scrolls[self.scroll_page], (20, 240))
                # Add click areas for page navigation (left and right sides of scroll)
                scroll_rect = self.cached_scrolls[self.scroll_page].get_rect(topleft=(20, 240))
                # Left side for previous page
                self.ui_hitboxes['scroll_left'] = pygame.Rect(20, 240, scroll_rect.width // 3, scroll_rect.height)
                # Right side for next page
                self.ui_hitboxes['scroll_right'] = pygame.Rect(20 + (scroll_rect.width * 2 // 3), 240, scroll_rect.width // 3, scroll_rect.height)
                # Draw red outlines for scroll navigation
                pygame.draw.rect(self.surface, (255, 0, 0), self.ui_hitboxes['scroll_left'], 2)
                pygame.draw.rect(self.surface, (255, 0, 0), self.ui_hitboxes['scroll_right'], 2)

        if self.showing_book:
            self.surface.blit(self.cached_book_of_lifeopen, (-40, 230))
        
        # Draw spawn boxes with mobs in order (dragonfly, worm, butterfly, snail, beetle)
        self.draw_spawn_boxes()

        ##### UI PRESS #####
        # Use hitboxes that match the buttons already in the background image (UI_play.png)
        # Script of evil (scroll) button is on top, book of life button is on bottom
        # Use the actual button image dimensions to create precise hitboxes
        # Buttons are scaled by 0.7, so positions need to match where they appear in background
        
        # Script of Evil button (top) - coordinates from user clicks
        # Top-left: (700, 475), Bottom-right: (922, 539)
        # Calculated: x=700, y=475, width=222, height=64
        self.ui_hitboxes['book_of_evil'] = pygame.Rect(700, 475, 222, 64)
        
        # Book of Life button (bottom) - coordinates from user clicks
        # Top-left: (701, 554), Bottom-right: (925, 615)
        # Calculated: x=701, y=554, width=224, height=61
        self.ui_hitboxes['book_of_life'] = pygame.Rect(701, 554, 224, 61)
        
        # Settings button - coordinates from user clicks
        # Top-left: (849, 692), Bottom-right: (945, 709)
        # Calculated: x=849, y=692, width=96, height=17
        self.ui_hitboxes['settings'] = pygame.Rect(849, 692, 96, 17)
        
        # Draw red outlines for debugging hitboxes - these should exactly match the buttons/text
        pygame.draw.rect(self.surface, (255, 0, 0), self.ui_hitboxes['book_of_evil'], 2)  # Red outline, 2px thick
        pygame.draw.rect(self.surface, (255, 0, 0), self.ui_hitboxes['book_of_life'], 2)  # Red outline, 2px thick
        pygame.draw.rect(self.surface, (255, 0, 0), self.ui_hitboxes['settings'], 2)  # Red outline, 2px thick
        #########################

        # Cache text rendering - only re-render if values changed
        if self.last_wave != self.wave:
            romanNumeral = self.intToRoman(self.wave)
            self.cached_text_surfaces['wave'] = self.cached_font_large.render("Wave: " + romanNumeral, True, (0, 0, 0))
            self.last_wave = self.wave
        
        if self.last_mobs_to_spawn != self.mobs_to_spawn:
            self.cached_text_surfaces['mobs'] = self.cached_font_large.render(f'Mobs: {self.mobs_to_spawn}', True, (0, 0, 0))
            self.last_mobs_to_spawn = self.mobs_to_spawn
        
        if self.last_branches != self.current_branches:
            self.cached_text_surfaces['branches'] = self.cached_font_large.render(f':  {self.current_branches}', True, (0, 0, 0))
            self.last_branches = self.current_branches
        
        # Initialize text surfaces if they don't exist
        if 'wave' not in self.cached_text_surfaces:
            romanNumeral = self.intToRoman(self.wave)
            self.cached_text_surfaces['wave'] = self.cached_font_large.render("Wave: " + romanNumeral, True, (0, 0, 0))
        if 'mobs' not in self.cached_text_surfaces:
            self.cached_text_surfaces['mobs'] = self.cached_font_large.render(f'Mobs: {self.mobs_to_spawn}', True, (0, 0, 0))
        if 'branches' not in self.cached_text_surfaces:
            self.cached_text_surfaces['branches'] = self.cached_font_large.render(f':  {self.current_branches}', True, (0, 0, 0))
        if 'units' not in self.cached_text_surfaces:
            self.cached_text_surfaces['units'] = self.cached_font_large.render(f'Units:', True, (0, 0, 0))
        
        self.surface.blit(self.cached_text_surfaces['wave'], (50, 70))
        self.surface.blit(self.cached_text_surfaces['branches'], (735, 45))
        self.surface.blit(self.cached_text_surfaces['units'], (1130, 550))

        
        # self.settings = self.load_world('settings.png')
        # self.settings = pygame.transform.scale(self.settings, (int(self.settings.get_width() * 0.7), int(self.settings.get_height() * 0.7)))
        #self.surface.blit(self.settings, (760, 645))
        #self.surface.blit(scale_fix_boe, (673, 525))
        #self.surface.blit(scale_fix_bol, (673, 350))
        #self.surface.blit(scale_fix_scroll, (670, 230)) THIS IS THE SCROLL
    
    def draw_spawn_boxes(self):
        """Draw spawn boxes showing mobs in the correct order - 2 rows of 3 boxes"""
        # Spawn box positions - 2 rows, 3 columns
        spawn_box_x_start = 1130  # X position for spawn boxes
        spawn_box_y_start = 580  # Starting Y position
        spawn_box_spacing_x = 35  # Horizontal spacing between boxes
        spawn_box_spacing_y = 35  # Vertical spacing between boxes
        
        # Mob order: 0=worm, 1=butterfly, 2=dragonfly, 3=snail, 4=beetle (matches script of evil order)
        mob_names = ['worm', 'butterfly', 'dragonfly', 'snail', 'beetle']
        
        for i, mob_name in enumerate(mob_names):
            # Calculate position: 2 rows, 3 columns
            row = i // 3
            col = i % 3
            x_pos = spawn_box_x_start + (col * spawn_box_spacing_x)
            y_pos = spawn_box_y_start + (row * spawn_box_spacing_y)
            
            # Draw woodbox background
            if hasattr(self, 'cached_woodbox'):
                self.surface.blit(self.cached_woodbox, (x_pos, y_pos))
            
            # Draw mob icon in the box using cached icon
            if i in self.cached_mob_icons:
                mob_icon = self.cached_mob_icons[i]
                # Center the icon in the box
                box_center_x = x_pos + self.cached_woodbox.get_width() // 2
                box_center_y = y_pos + self.cached_woodbox.get_height() // 2
                icon_rect = mob_icon.get_rect(center=(box_center_x, box_center_y))
                self.surface.blit(mob_icon, icon_rect)
                
                # Store hitbox for clicking - use exact woodbox dimensions
                spawn_hitbox = pygame.Rect(x_pos, y_pos, self.cached_woodbox.get_width(), self.cached_woodbox.get_height())
                self.ui_hitboxes[f'spawn_box_{i}'] = spawn_hitbox
                
                # Highlight selected mob
                if i == self.selected_mob_type:
                    # Draw highlight border
                    highlight_rect = pygame.Rect(x_pos, y_pos, self.cached_woodbox.get_width(), self.cached_woodbox.get_height())
                    pygame.draw.rect(self.surface, (255, 255, 0), highlight_rect, 3)
                
                # Draw red outline for spawn box hitbox (debug) - exactly matches the woodbox
                pygame.draw.rect(self.surface, (255, 0, 0), spawn_hitbox, 2)
                
                # Draw red outline for spawn box hitbox (debug)
                if f'spawn_box_{i}' in self.ui_hitboxes:
                    pygame.draw.rect(self.surface, (255, 0, 0), self.ui_hitboxes[f'spawn_box_{i}'], 1)
    
    def ui_check_click(self, mouse_pos):
        # Check surrender close button
        if self.showing_surrender and 'surrender_close' in self.ui_hitboxes and self.ui_hitboxes['surrender_close'].collidepoint(mouse_pos):
            return "SURRENDER_CLOSE"
        
        # Check spawn box clicks
        for i in range(5):  # 5 mob types
            box_key = f'spawn_box_{i}'
            if box_key in self.ui_hitboxes and self.ui_hitboxes[box_key].collidepoint(mouse_pos):
                return f"SPAWN_BOX_{i}"
        
        # Check scroll page navigation
        if 'scroll_left' in self.ui_hitboxes and self.ui_hitboxes['scroll_left'].collidepoint(mouse_pos):
            return "SCROLL_LEFT"
        if 'scroll_right' in self.ui_hitboxes and self.ui_hitboxes['scroll_right'].collidepoint(mouse_pos):
            return "SCROLL_RIGHT"
        
        # Check settings button
        if 'settings' in self.ui_hitboxes and self.ui_hitboxes['settings'].collidepoint(mouse_pos):
            return "SETTINGS"
        
        # Check book buttons
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
        if self.showing_cutscene:
            # Draw cutscene (check this first so it takes priority)
            if self.cutscene_images and len(self.cutscene_images) > 0:
                # Clear screen first to prevent any flickering
                self.surface.fill((0, 0, 0))
                
                # Only advance frames if cutscene hasn't finished
                if not self.cutscene_finished:
                    now = pygame.time.get_ticks()
                    if now - self.cutscene_timer >= self.animation_speed:
                        self.cutscene_timer = now
                        self.cutscene_frame += 1
                        # Check if we've reached the last frame
                        if self.cutscene_frame >= len(self.cutscene_images):
                            self.cutscene_frame = len(self.cutscene_images) - 1  # Stay on last frame
                            self.cutscene_finished = True
                
                # Ensure frame index is valid and display the current frame
                if 0 <= self.cutscene_frame < len(self.cutscene_images):
                    self.surface.blit(self.cutscene_images[self.cutscene_frame], (0, 0))
                else:
                    # Fallback: show first frame if index is invalid
                    self.cutscene_frame = 0
                    self.surface.blit(self.cutscene_images[0], (0, 0))
            else:
                # If no images loaded, fill with black and show error
                self.surface.fill((0, 0, 0))
                print("WARNING: Cutscene is showing but no images loaded!")
            pygame.display.update()
        elif self.showing_start_screen:
            self.start_screen.draw()
            self.start_screen.draw_buttons()
            if self.showing_settings_screen:
                self.start_screen.draw_settings()
                if self.showing_instructions_scene:
                    self.start_screen.draw_instructions()
            pygame.display.update()
        else:
            self.surface.fill(self.bgcolor)
            # Use cached images instead of loading every frame (with fallback if not initialized)
            if hasattr(self, 'cached_bg_image'):
                self.surface.blit(self.cached_bg_image, (0, 0))
            else:
                # Fallback: load and scale on the fly if cache not initialized
                background_raw = self.load_world("wbsky.png")
                bg_img = pygame.transform.scale(background_raw, (int(background_raw.get_width() * 0.7), int(background_raw.get_height() * 0.75)))
                self.surface.blit(bg_img, (0, 0))
            
            self.update_and_draw_clouds()
            
            if hasattr(self, 'cached_island_image'):
                self.surface.blit(self.cached_island_image, (-100, 0))
            else:
                island_raw = self.load_world("island.png")
                island_img = pygame.transform.scale(island_raw, (int(island_raw.get_width() * 1), int(island_raw.get_height() * 1.2)))
                self.surface.blit(island_img, (-100, 0))
            
            if hasattr(self, 'cached_ui_image'):
                self.surface.blit(self.cached_ui_image, (0, 0))
            else:
                ui_raw = self.load_world("UI_play.png")
                ui_img = pygame.transform.scale(ui_raw, (int(ui_raw.get_width() * 0.7), int(ui_raw.get_height() * 0.75)))
                self.surface.blit(ui_img, (0, 0))
            
            self.map_grid()
            
            if hasattr(self, 'cached_tree_life_image'):
                self.surface.blit(self.cached_tree_life_image, (210, 30))
            else:
                tree_life_raw = self.load_world("tree_of_life.png")
                tree_img = pygame.transform.scale(tree_life_raw, (int(tree_life_raw.get_width() * 1.5), int(tree_life_raw.get_height() * 1.5)))
                self.surface.blit(tree_img, (210, 30))
            
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

            # Cache text rendering for tiles remaining - only re-render if value changed
            if self.last_paths_remaining != self.paths_remaining:
                self.cached_text_surfaces['tiles'] = self.cached_font_medium.render(f'Tiles Remaining: {self.paths_remaining}', True, (0, 0, 0))
                self.last_paths_remaining = self.paths_remaining
            
            if 'tiles' not in self.cached_text_surfaces:
                self.cached_text_surfaces['tiles'] = self.cached_font_medium.render(f'Tiles Remaining: {self.paths_remaining}', True, (0, 0, 0))
            
            self.surface.blit(self.cached_text_surfaces['tiles'], (40, 120))
            
            self.draw_UI()
            
            # Draw cursor icon (hammer for build mode, shovel for delete mode)
            if self.edit_mode:
                # Hide default cursor in edit mode
                pygame.mouse.set_visible(False)
                
                # Update hammer animation timer
                if self.hammer_animating:
                    # Use delta time from clock (get_time returns milliseconds since last tick)
                    delta_time = self.clock.get_time() / 1000.0  # Convert to seconds
                    self.hammer_animation_duration -= delta_time
                    if self.hammer_animation_duration <= 0:
                        self.hammer_animating = False
                        self.cursor_animation_counter = 0
                        self.cursor_animation_frame = 0
                
                if self.build and self.hammer_images:
                    # Animate hammer only when tile changes
                    if self.hammer_animating:
                        self.cursor_animation_counter += 0.3  # Faster animation when active
                        self.cursor_animation_frame = int(self.cursor_animation_counter) % len(self.hammer_images)
                    else:
                        # Show first frame when not animating
                        self.cursor_animation_frame = 0
                    
                    cursor_img = self.hammer_images[self.cursor_animation_frame]
                    # Draw at mouse position with offset to center
                    self.surface.blit(cursor_img, (self.x - cursor_img.get_width() // 2, self.y - cursor_img.get_height() // 2))
                elif not self.build and self.shovel_image:
                    # Show shovel when deleting paths
                    self.surface.blit(self.shovel_image, (self.x - self.shovel_image.get_width() // 2, self.y - self.shovel_image.get_height() // 2))
            else:
                # Show default cursor when not in edit mode
                pygame.mouse.set_visible(True)
            
            pygame.display.update()

    #Optimize This
    def is_grid_valid(self, world_grid, grid_size):
        all_path_coords = []
        end_nodes = []  # All -1 positions (start and end)

        for i in range(grid_size):
            for j in range(grid_size):
                val = world_grid[i][j]
                
                if val not in [1, -1]:
                    continue
                
                all_path_coords.append((i, j))
                
                if val == -1:
                    end_nodes.append((i, j))
                    # Check that -1 has at least one edge touching a path (1 or -1)
                    has_path_neighbor = False
                    for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < grid_size and 0 <= nj < grid_size:
                            neighbor = world_grid[ni][nj]
                            if neighbor in [1, -1]:
                                has_path_neighbor = True
                                break
                    if not has_path_neighbor:
                        return False  # -1 must have at least one path neighbor

        # Must have at least one start (-1) and one end (-1)
        if len(end_nodes) < 2:
            return len(all_path_coords) == 0  # Empty grid is valid
        
        # Check that all path tiles are connected
        if not all_path_coords:
            return True
        
        visited = set()
        stack = [end_nodes[0]]  # Start from first -1
        
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
                if self.showing_cutscene:
                    # Allow skipping cutscene with mouse click or any key (after delay)
                    current_time = pygame.time.get_ticks()
                    if (event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN) and current_time > self.cutscene_skip_delay:
                        print("Cutscene skipped by user")
                        self.showing_cutscene = False
                        self.game_active = True
                        # If cutscene was victory/defeat, return to start screen
                        if self.cutscene_return_to_start:
                            self.showing_start_screen = True
                            # Reset game state when returning to start
                            self.reset_grid()
                            self.wave = 1
                            self.tree_health = 2500
                            self.round_active = False
                            self.round_ended = True
                            self.edit_mode = True
                            self.mobs = []
                            self.mobs_to_spawn = 0
                        # For test cutscene: continue to game
                        elif not self.showing_start_screen:
                            # Already in game, just continue
                            pass
                        else:
                            # Test cutscene finished, now start the game
                            self.showing_start_screen = False
                elif self.showing_start_screen:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        action = None
                        if not self.showing_settings_screen and not self.showing_instructions_scene:
                            action = self.start_screen.check_click(event.pos)
                            if action == "START":
                                # Start the game normally
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
                            # Debug: Print mouse position for hitbox calibration
                            print(f"DEBUG: Mouse click position: ({event.pos[0]}, {event.pos[1]})")
                            
                            ui_action = self.ui_check_click(event.pos)
################################################################################################################
                            if ui_action == "BOOK_OF_EVIL":
                                print("Book of evil was clicked")
                                self.showing_scroll = not self.showing_scroll
                                if self.showing_scroll:
                                    self.scroll_page = self.selected_mob_type  # Start on current mob's page
                                if self.showing_book is True:
                                    self.showing_book = not self.showing_book
                            elif ui_action == "BOOK_OF_LIFE":
                                print("Book of life was clicked")
                                self.showing_book = not self.showing_book
                                if self.showing_scroll is True:
                                    self.showing_scroll = not self.showing_scroll
                            elif ui_action and ui_action.startswith("SPAWN_BOX_"):
                                # Clicked on a spawn box - select that mob type
                                mob_index = int(ui_action.split("_")[2])
                                self.selected_mob_type = mob_index
                                print(f"Selected mob type: {mob_index}")
                            elif ui_action == "SCROLL_LEFT":
                                # Navigate to previous page
                                self.scroll_page = (self.scroll_page - 1) % 5
                                print(f"Scroll page: {self.scroll_page}")
                            elif ui_action == "SCROLL_RIGHT":
                                # Navigate to next page
                                self.scroll_page = (self.scroll_page + 1) % 5
                                print(f"Scroll page: {self.scroll_page}")
                            elif ui_action == "SETTINGS":
                                # Show surrender screen
                                self.showing_surrender = not self.showing_surrender
                                print("Settings/Surrender clicked")
                            elif ui_action == "SURRENDER_CLOSE":
                                # Close surrender screen
                                self.showing_surrender = False
                                print("Surrender screen closed")
                            elif ui_action == "SURRENDER_CLOSE":
                                # Close surrender screen
                                self.showing_surrender = False
                                print("Surrender screen closed")
################################################################################################################
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
                                # Reset branches for the current wave
                                if self.wave <= len(self.branches):
                                    self.current_branches = self.branches[self.wave-1]
                                    self.last_branches = -1  # Force update of cached text
                                pygame.time.set_timer(self.SPAWN_MOB_EVENT, 1000)

                    elif event.type == self.SPAWN_MOB_EVENT:
                        self.round_ended = False
                        if self.mobs_to_spawn > 0 and self.current_branches > 0:
                            pts = self.get_path_waypoints()
                            new_mob = Mob(pts, self.spriteSize, DEFAULT_WIDTH/2, 50, self.selected_mob_type)
                            self.mobs_to_spawn -= 1
                            self.mobs.append(new_mob)
                            # Reduce branches cost (1 branch per mob spawn)
                            self.current_branches = max(0, self.current_branches - 1)
                            # Update cached text surface for branches
                            self.last_branches = -1  # Force update
                        else:
                            pygame.time.set_timer(self.SPAWN_MOB_EVENT, 0)
                    elif event.type == pygame.KEYUP:
                        pass
            # Check win condition: completed all waves (wave > 20)
            if self.wave > 20 and self.tree_health > 0:
                if self.game_active:
                    self.victory()
            
            # Check lose condition: tree health depleted
            if self.tree_health <= 0:
                if self.game_active:
                    self.defeat()
            
            if self.round_active and self.mobs_to_spawn == 0 and len(self.mobs) == 0:
                self.round_active = False
                self.round_ended = True
                self.edit_mode = True
                self.wave += 1
                # Reset branches for new wave
                if self.wave <= len(self.branches):
                    self.current_branches = self.branches[self.wave-1]
                    self.last_branches = -1  # Force update of cached text
                # Optional: self.paths_remaining = MAX_TILES # Reset tiles for next round?

            self.draw_window()
            if self.showing_start_screen:
                self.clock.tick(15)
                continue
            elif self.showing_cutscene:
                self.clock.tick(30)  # Slower frame rate for cutscenes
                continue
            self.clock.tick(60)


# ========

if __name__ == "__main__":
    q = Game()
    q.run_app()

