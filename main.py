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
REFERENCE_GRID_SIZE = Maps.REFERENCE_GRID_SIZE
BASE_MAX_TILES = 25
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'tiles')
BGROUND_DIR = os.path.join(os.path.dirname(__file__), 'bground')
TOWERS_DIR = os.path.join(os.path.dirname(__file__), 'towers')
BUTTONS_DIR = os.path.join(os.path.dirname(__file__), 'buttons')
MOBS_DIR = os.path.join(os.path.dirname(__file__), 'mobs')
ASSETS_UI_DIR = os.path.join(os.path.dirname(__file__), 'assets', 'ui')
ASSETS_MOBS_DIR = os.path.join(os.path.dirname(__file__), 'assets', 'mobs')
ASSETS_BG_DIR = os.path.join(os.path.dirname(__file__), 'assets', 'bg')

MAX_WAVES = 20
CAVE_WAVE_MAX = 10
STAGE_CAVE = "cave"
STAGE_SUNSHINE = "sunshine"
# Background art filenames (place cave files in bground/ or assets/bg/cave/)
STAGE_BACKGROUNDS = {
    STAGE_CAVE: ("cave_sky.png", "cave_island.png"),
    STAGE_SUNSHINE: ("wbsky.png", "island.png"),
}
STAGE_UI_PLAY = {
    STAGE_CAVE: "cave_UI_play.png",
    STAGE_SUNSHINE: "UI_play.png",
}
STAGE_SETTINGS_PAGE = {
    STAGE_CAVE: "cave_settingsmain.png",
    STAGE_SUNSHINE: "settingsmain.png",
}
STAGE_BG_FALLBACK = STAGE_BACKGROUNDS[STAGE_SUNSHINE]
SETTINGS_PAGE_SCALE = 0.8
INGAME_SETTINGS_PAGE_POS = (250, 130)
# Sunshine sky uses 0.7×0.75 on its source art; all skies scale to that display size.
SKY_SCALE = (0.7, 0.75)
ISLAND_SCALE = (1.0, 1.2)
CURSOR_TOOL_SIZE = (40, 40)
SHOVEL_CURSOR_SIZE = (46, 46)
# Offset from centered blit so shovel tip lines up with the mouse hotspot (x, y up)
SHOVEL_CURSOR_OFFSET = (0, -12)
WAVE_COMBAT_SECONDS = 30
TILE_DRAW_SCALE = 1.75  # larger isometric tiles (reference layout was 1.5)


worm = {
    "health": 10,
    "damage": 3,
    "speed": 2,
    "cost": 1
}

dragonfly = {
    "health": 6,
    "damage": 2,
    "speed": 4,
    "cost": 2
}

snail = {
    "health": 45,
    "damage": 10,
    "speed": 1,
    "cost": 6
}

butterfly = {
    "health": 20,
    "damage": 6,
    "speed": 3,
    "cost": 5
}

beetle = {
    "health": 90,
    "damage": 8,
    "speed": 2,
    "cost": 8,
}
# Maximum Branchs and Maximum Tiles per level
tiles  = [20, 20, 21, 21, 21, 21, ]
branches = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 45]
treehealth = [18, 21, 25, 30, 36, 42, 48, 55, 63, 72, 82, 93, 105, 118, 132, 147, 163, 180, 198, 220]

# Mob index: 0 spider (worm art), 1 butterfly, 2 dragonfly, 3 snail, 4 beetle
MOB_HEALTH = [20, 50, 20, 100, 50]
MOB_DAMAGE = [3, 7, 3, 40, 9]
MOB_SPEED = [6, 3, 4, 1, 3]  # design speeds; scaled in Mob.__init__
MOB_SPEED_SCALE = 0.42
MOB_BRANCH_COSTS = [1, 5, 10, 20, 50]  # worm, butterfly, dragonfly, snail, beetle
MOB_SPAWN_COOLDOWN_MS = 650

# Towers: [range in grid tiles, damage, cooldown ms] — cooldown = 1000 / attack_speed
TOWER_BEE = {"attack": 20, "attack_speed": 2, "range_tiles": 2}
TOWER_LADYBUG = {"attack": 10, "attack_speed": 4, "range_tiles": 1}
TOWER_BUSH = {"attack": 30, "attack_speed": 1, "range_tiles": 3}
TOWER_TILE_TYPES = {
    "b2": ("bee", TOWER_BEE),
    "l1": ("ladybug", TOWER_LADYBUG),
    "-8": ("bush", TOWER_BUSH),
}

# ---------------------------------------------------------------------------
# HUD layout (see bground/UI_play.png — branch + clock icons are baked into that image)
#
# TO MOVE ICONS UP/DOWN (change art position):
#   Edit bground/UI_play.png in an image editor. Approx. regions on the 1400×1000 source:
#     • Branch (twig):  x≈998–1043, y≈70–100
#     • Timer (watch):  x≈1003–1049, y≈132–189
#   On screen, icon Y ≈ (pixel Y in PNG) × 0.75  (UI is scaled 0.7×0.75 at blit 0,0).
#
# TO MOVE THE NUMBERS UP/DOWN (keep icons where they are in the PNG):
#   Change the Y value in the anchors below (smaller Y = higher, larger Y = lower).
#   X is the left edge of the number, just to the right of each icon.
# ---------------------------------------------------------------------------
UI_PLAY_SCALE = (0.7, 0.75)
HUD_WAVE_POS = (700, 60)
HUD_TILES_POS = (700, 100)
# Default Y aligns with baked-in icons at ~y=63 (branch) and ~y=120 (timer) on screen.
HUD_BRANCH_TEXT_ANCHOR = (740, 158)
HUD_TIMER_TEXT_ANCHOR = (755, 220)

# Mob index: 0 worm, 1 butterfly, 2 dragonfly, 3 snail, 4 beetle
MOB_UNLOCK_WAVES = (1, 2, 4, 7, 10)
# 2×3 Spawn grid on UI_play.png (screen coords @ UI_PLAY_SCALE)
MOB_GRID_COLS = 3
MOB_GRID_ROWS = 2
MOB_GRID_SLOT_W = 56
MOB_GRID_SLOT_H = 56
SCRIPT_OF_EVIL_PAGE_COUNT = 5  # worm → beetle scroll pages
SFX_VOLUME_MAX = 10
DEBUG_UI_OUTLINES = False
OBSTACLE_SEE_THROUGH_ALPHA = 0
TOWER_HOVER_ALPHA = 100
UI_BORDER_BROWN = (255, 200, 80)
HUD_TEXT_BROWN = (85, 58, 28)
HUD_TEXT_BROWN_DARK = (58, 40, 18)
HUD_TEXT_BROWN_LIGHT = (120, 85, 45)
HUD_TEXT_BROWN_ACCENT = (200, 145, 55)
# Temporary poison VFX until dedicated UI (grid -8 = bush)
POISON_OUTLINE_COLOR = (40, 220, 70)
POISON_OUTLINE_WIDTH = 3
# Surrender popup (coords relative to scaled surrenderpage blit top-left, scale 0.8)
SURRENDER_HITBACK = pygame.Rect(69, 67, 21, 22)
SURRENDER_HIT_NO = pygame.Rect(125, 200, 80, 58)
SURRENDER_HIT_YES = pygame.Rect(330, 200, 100, 58)
# Slot center (x, y) per cell, row-major — tweak Y to move the whole grid up/down
MOB_GRID_CENTERS = (
    (735, 340), (812, 340), (889, 340),
    (735, 408), (812, 408), (889, 408),
)

rgb = tuple[int,int,int]
num = random.randint(1, 5)


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
        self.mobcolor = [(200, 50, 50),(93, 63, 211),(0, 255, 255)]
        # Mob order: spider(worm sprites), butterfly, dragonfly, snail, beetle
        self.mobtype = [
            ['worm moving_0001.png', 'worm moving_0002.png', 'worm moving_0003.png', 'worm moving_0004.png'],  # 0: spider
            ['butterfly_0001.png', 'butterfly_0002.png', 'butterfly_0003.png', 'butterfly_0004.png'],
            ['dragonfly flying_0001.png', 'dragonfly flying_0002.png', 'dragonfly flying_0003.png', 'dragonfly flying_0004.png'],
            ['snail idle_0001.png', 'snail idle_0002.png', 'snail idle_0003.png', 'snail idle_0004.png'],
            ['beetle_0001.png', 'beetle_0002.png', 'beetle_0003.png', 'beetle_0004.png'],
        ]
        self.mob_health_values = list(MOB_HEALTH)
        self.mob_dmg = list(MOB_DAMAGE)
        if mob_type is not None:
            self.randmob = mob_type
        else:
            self.randmob = random.randint(0, len(self.mobtype) - 1)
        self.health = self.mob_health_values[self.randmob]
        self.dmg = self.mob_dmg[self.randmob]
        self.speed = MOB_SPEED_SCALE * MOB_SPEED[self.randmob]

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
        self.at_end = False
        self.poisoned = False

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

    def advance_animation(self):
        """Advance only the animation frames without moving the mob."""
        self.animation_counter += self.animaton_speed
        if self.animation_counter >= 1:
            self.animation_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.mobframes)

    def reset_animation(self):
        """Reset the mob animation to the first frame."""
        self.current_frame = 0
        self.animation_counter = 0

    def draw(self, surface):
        current_sprite = self.mobframes[self.current_frame]
        
        if self.target_idx < len(self.waypoints):
            target = self.waypoints[self.target_idx]
            if target.x < self.pos.x:
                current_sprite = self.mobframes_left[self.current_frame]
            else:
                current_sprite = self.mobframes_right[self.current_frame]

        # Offset mob slightly downward to align with shadows
        sprite_rect = current_sprite.get_rect(center=(self.pos.x, self.pos.y + 8))
        surface.blit(current_sprite, sprite_rect)
        if self.poisoned:
            pygame.draw.rect(
                surface,
                POISON_OUTLINE_COLOR,
                sprite_rect.inflate(8, 8),
                POISON_OUTLINE_WIDTH,
            )

        if self.health > 0:
            bar_width = 40
            health_pct = self.health / self.mob_health_values[self.randmob]
            pygame.draw.rect(surface, (255, 0, 0), (self.pos.x - 20, self.pos.y - 32, bar_width, 5))
            pygame.draw.rect(surface, (0, 255, 0), (self.pos.x - 20, self.pos.y - 32, bar_width * health_pct, 5))

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
        self.SPAWN_MOB_EVENT = pygame.USEREVENT + 1
        #########
        self.showing_scroll = False
        self.showing_book = False
        self.scroll_page = 0  # Current page in script of evil (0-4 for 5 mobs)
        self.cached_mob_icons = {}  # Cache mob icons for spawn boxes
        self.showing_surrender = False
        self.showing_ingame_settings = False
        self.showing_ingame_instructions = False
        self.showing_ingame_credits = False
        self.cached_ui_by_stage: dict = {}
        self.cached_settings_by_stage: dict = {}
        self._ui_play_display_px = None
        self._settings_page_display_px = None
        self._ingame_settings_hitboxes: dict = {}
        self.debug_click_mode = False  # Demo build: keep console clean

        # Presentation / juice (hackathon polish)
        self.mission_briefing_active = False
        self.see_through_obstacles = False
        self.current_stage = STAGE_CAVE
        self._sky_display_px = None
        self._island_display_px = None
        self._floating_text = []  # {text, x, y, vy, life, color}
        self._last_tower_sound_ms = 0
        self._feel_audio_ready = False
        self.sfx_volume_level = SFX_VOLUME_MAX
        self.settings_volume_label = ""
        ########
        self.set_path = False
        self.rm_path = False
        self.current_level_id = 1
        self.grid_rows = REFERENCE_GRID_SIZE
        self.grid_cols = REFERENCE_GRID_SIZE
        self.grid_size = REFERENCE_GRID_SIZE
        self.map_scale = 1.0
        self.paths_remaining = BASE_MAX_TILES
        self.edit_mode = True
        self.build = True
        self.highlight = True

        self.round_active = False
        self.round_ended = True
        
        self.mobs = []
        self.selected_mob_type = 0
        self.points = 0

        # Branches buy mobs during the wave; quota caps how many can be deployed
        self.current_branches = 0
        self.mob_costs = list(MOB_BRANCH_COSTS)
        self.mob_spawn_cooldown_until = {i: 0 for i in range(5)}
        self._tree_kill_handled = False
        self.poison_bush_cells: set[tuple[int, int]] = set()
        
        self.wave = 1
        self.begin_wave_setup()

        pygame.font.init()
        
        # Cache for rendered text surfaces to avoid re-rendering every frame
        self.cached_text_surfaces = {}
        self.last_wave = 0
        self.last_branches = -1
        self.last_active_mobs = -1
        self.wave_deadline_ms = None
        self.last_timer_second = -1
        self.last_paths_remaining = -1        

    def x_transform(self, x, w, h):
        return (x * w / 2, (x * h/2)/2)
    
    def y_transform(self,y, w, h):
        return ((-y * w) / 2, (y * h/2)/2)
    
    def load_image(self, name):
        path = os.path.join(ASSETS_DIR, name)
        return pygame.image.load(path).convert_alpha()

    def load_world(self, name):
        path = self._resolve_bground_path(name)
        return pygame.image.load(path).convert_alpha()

    def _resolve_bground_path(self, name: str, *, fallback: str | None = None) -> str:
        """bground/ first, then assets/bg/ and assets/bg/cave/, then optional fallback name."""
        candidates = [
            os.path.join(BGROUND_DIR, name),
            os.path.join(ASSETS_BG_DIR, name),
            os.path.join(ASSETS_BG_DIR, "cave", name),
        ]
        for path in candidates:
            if os.path.isfile(path):
                return path
        if fallback:
            for path in (
                os.path.join(BGROUND_DIR, fallback),
                os.path.join(ASSETS_BG_DIR, fallback),
            ):
                if os.path.isfile(path):
                    return path
        return candidates[0]

    def stage_for_wave(self, wave: int) -> str:
        return Maps.stage_for_wave(wave)

    def _ui_blocks_round_start(self) -> bool:
        return (
            self.showing_scroll
            or self.showing_book
            or self.showing_surrender
            or self.showing_ingame_settings
            or self.showing_ingame_instructions
            or self.showing_ingame_credits
        )

    def _ingame_menu_open(self) -> bool:
        return (
            self.showing_ingame_settings
            or self.showing_ingame_instructions
            or self.showing_ingame_credits
            or self.showing_surrender
        )

    def _can_start_wave_combat(self) -> bool:
        return (
            self.is_grid_valid(self.world_grid)
            and not self.round_active
            and self.round_ended
            and not self._ui_blocks_round_start()
            and not self._game_input_locked()
        )

    def _sky_display_size(self) -> tuple[int, int]:
        """Target sky size from sunshine art (same on-screen footprint for every stage)."""
        if self._sky_display_px is None:
            ref_name = STAGE_BACKGROUNDS[STAGE_SUNSHINE][0]
            ref = self.load_world(ref_name)
            sx, sy = SKY_SCALE
            self._sky_display_px = (
                int(ref.get_width() * sx),
                int(ref.get_height() * sy),
            )
        return self._sky_display_px

    def _island_display_size(self) -> tuple[int, int]:
        if self._island_display_px is None:
            ref_name = STAGE_BACKGROUNDS[STAGE_SUNSHINE][1]
            ref = self.load_world(ref_name)
            sx, sy = ISLAND_SCALE
            self._island_display_px = (
                int(ref.get_width() * sx),
                int(ref.get_height() * sy),
            )
        return self._island_display_px

    def _scale_sky_to_display(self, surf: pygame.Surface) -> pygame.Surface:
        return pygame.transform.scale(surf, self._sky_display_size())

    def _scale_island_to_display(self, surf: pygame.Surface) -> pygame.Surface:
        return pygame.transform.scale(surf, self._island_display_size())

    def _apply_stage_visuals(self, stage: str) -> None:
        """Swap sky + island (and cloud visibility) for cave vs sunshine."""
        self.current_stage = stage
        sky_name, island_name = STAGE_BACKGROUNDS.get(stage, STAGE_BG_FALLBACK)
        fb_sky, fb_island = STAGE_BG_FALLBACK
        try:
            background_raw = self.load_world(sky_name)
        except (pygame.error, FileNotFoundError):
            background_raw = self.load_world(fb_sky)
        try:
            island_raw = self.load_world(island_name)
        except (pygame.error, FileNotFoundError):
            island_raw = self.load_world(fb_island)
        self.cached_bg_image = self._scale_sky_to_display(background_raw)
        self.cached_island_image = self._scale_island_to_display(island_raw)
        if hasattr(self, "cached_ui_by_stage") and stage in self.cached_ui_by_stage:
            self.cached_ui_image = self.cached_ui_by_stage[stage]
        if stage == STAGE_CAVE:
            self.active_clouds = []
        elif stage == STAGE_SUNSHINE and hasattr(self, "cloud_images"):
            if not self.active_clouds:
                for _ in range(1):
                    self.spawn_cloud(random.randint(0, 700))
    
    def load_buttons(self, name: str) -> pygame.Surface:
        path = os.path.join(BUTTONS_DIR, name)
        return pygame.image.load(path).convert_alpha()

    def load_towers(self, name):
        path = os.path.join(TOWERS_DIR, name)
        return pygame.image.load(path).convert_alpha()

    def _ui_play_display_size(self) -> tuple[int, int]:
        if self._ui_play_display_px is None:
            ref = self.load_world(STAGE_UI_PLAY[STAGE_SUNSHINE])
            sx, sy = UI_PLAY_SCALE
            self._ui_play_display_px = (
                int(ref.get_width() * sx),
                int(ref.get_height() * sy),
            )
        return self._ui_play_display_px

    def _settings_page_display_size(self) -> tuple[int, int]:
        if self._settings_page_display_px is None:
            ref = self.load_buttons(STAGE_SETTINGS_PAGE[STAGE_SUNSHINE])
            self._settings_page_display_px = (
                int(ref.get_width() * SETTINGS_PAGE_SCALE),
                int(ref.get_height() * SETTINGS_PAGE_SCALE),
            )
        return self._settings_page_display_px

    def _scale_ui_play_image(self, surf: pygame.Surface) -> pygame.Surface:
        return pygame.transform.scale(surf, self._ui_play_display_size())

    def _scale_settings_page_image(self, surf: pygame.Surface) -> pygame.Surface:
        return pygame.transform.scale(surf, self._settings_page_display_size())

    def _load_all_stage_ui_caches(self) -> None:
        for stage, ui_file in STAGE_UI_PLAY.items():
            try:
                raw = self.load_world(ui_file)
            except (pygame.error, FileNotFoundError):
                raw = self.load_world(STAGE_UI_PLAY[STAGE_SUNSHINE])
            self.cached_ui_by_stage[stage] = self._scale_ui_play_image(raw)
        for stage, page_file in STAGE_SETTINGS_PAGE.items():
            try:
                raw = self.load_buttons(page_file)
            except (pygame.error, FileNotFoundError):
                raw = self.load_buttons(STAGE_SETTINGS_PAGE[STAGE_SUNSHINE])
            self.cached_settings_by_stage[stage] = self._scale_settings_page_image(raw)
        if not hasattr(self, "cached_instr_page"):
            instr_raw = self.load_buttons("instr_man.png")
            self.cached_instr_page = pygame.transform.scale(
                instr_raw,
                self._settings_page_display_size(),
            )

    def _refresh_ingame_settings_hitboxes(self) -> None:
        spx, spy = INGAME_SETTINGS_PAGE_POS
        self._ingame_settings_hitboxes = {
            "close": pygame.Rect(spx + 81, spy + 88, 21, 22).inflate(16, 14),
            "sound_left": pygame.Rect(spx + 306, spy + 185, 20, 28).inflate(12, 10),
            "sound_right": pygame.Rect(spx + 425, spy + 185, 20, 28).inflate(12, 10),
            "surrender": pygame.Rect(spx + 80, spy + 248, 400, 55),
        }
        if self.current_stage == STAGE_CAVE:
            self._ingame_settings_hitboxes["credits"] = pygame.Rect(spx + 80, spy + 195, 280, 42)
        else:
            self._ingame_settings_hitboxes["instructions"] = pygame.Rect(spx + 80, spy + 220, 400, 42)

    def _draw_ingame_settings_overlay(self) -> None:
        veil = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        veil.fill((8, 12, 28, 160))
        self.surface.blit(veil, (0, 0))
        page = self.cached_settings_by_stage.get(
            self.current_stage,
            self.cached_settings_by_stage.get(STAGE_SUNSHINE),
        )
        if page:
            self.surface.blit(page, INGAME_SETTINGS_PAGE_POS)
        if self.settings_volume_label:
            label = self.cached_font_small.render(
                self.settings_volume_label, True, HUD_TEXT_BROWN
            )
            lr = self._ingame_settings_hitboxes.get("sound_left")
            rr = self._ingame_settings_hitboxes.get("sound_right")
            if lr and rr:
                cx = (lr.centerx + rr.centerx) // 2
                cy = (lr.centery + rr.centery) // 2
                self.surface.blit(label, label.get_rect(center=(cx, cy)))

    def _draw_ingame_subpage_overlay(self, page_surf: pygame.Surface) -> None:
        veil = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        veil.fill((8, 12, 28, 160))
        self.surface.blit(veil, (0, 0))
        pos = (
            (self.width - page_surf.get_width()) // 2,
            (self.height - page_surf.get_height()) // 2,
        )
        self.surface.blit(page_surf, pos)
        close = pygame.Rect(pos[0] + 81, pos[1] + 88, 21, 22).inflate(16, 14)
        self._ingame_subpage_close_rect = close

    def _ingame_settings_click(self, mouse_pos) -> str | None:
        hb = self._ingame_settings_hitboxes
        if hb.get("close") and hb["close"].collidepoint(mouse_pos):
            return "CLOSE"
        if hb.get("sound_left") and hb["sound_left"].collidepoint(mouse_pos):
            return "SOUND_DOWN"
        if hb.get("sound_right") and hb["sound_right"].collidepoint(mouse_pos):
            return "SOUND_UP"
        if hb.get("instructions") and hb["instructions"].collidepoint(mouse_pos):
            return "INSTRUCTIONS"
        if hb.get("credits") and hb["credits"].collidepoint(mouse_pos):
            return "CREDITS"
        if hb.get("surrender") and hb["surrender"].collidepoint(mouse_pos):
            return "SURRENDER"
        return None
    
    def initiate_cutscenes(self):
        self.game_active = True
        self.cutscene_frame = 0
        self.cutscene_images = []
        self.cutscene_timer = 0
        self.animation_speed = 50 # Milliseconds per frame (2x faster)
        self.showing_cutscene = False
        self.cutscene_played_once = False  # For testing: track if win cutscene has been shown
        self.cutscene_skip_delay = 0  # Prevent immediate skipping
        self.cutscene_finished = False  # Track if cutscene has reached the last frame

    def load_cutscene(self, folder_name, return_to_start=False):
        # Prevent reloading if cutscene is already showing
        if self.showing_cutscene and len(self.cutscene_images) > 0:
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
            if len(files) == 0:
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
        except Exception as e:
            self.showing_cutscene = False

    def victory(self):
        if self.game_active: # Prevent reloading every frame
            pygame.mouse.set_visible(True)
            # Load victory cutscene and return to main menu when finished
            self.load_cutscene('victory', return_to_start=True)

    def defeat(self):
        if self.game_active:
            pygame.mouse.set_visible(True)
            # Load defeat cutscene and return to main menu when finished
            self.load_cutscene('defeat', return_to_start=True)

    def return_to_main_menu(self) -> None:
        """Return to the start screen without playing a cutscene."""
        pygame.mouse.set_visible(True)
        self.showing_cutscene = False
        self.showing_surrender = False
        self.showing_ingame_settings = False
        self.showing_ingame_instructions = False
        self.showing_ingame_credits = False
        self.showing_scroll = False
        self.showing_book = False
        self.mission_briefing_active = False
        self.showing_settings_screen = False
        self.showing_instructions_scene = False
        self.game_active = True
        self.showing_start_screen = True
        self.wave = 1
        self.begin_wave_setup()
        self.tower_states = {}
    
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
            
        self.tree_health_max = Maps.tree_health_for_wave(1)
        self.tree_health = self.tree_health_max

    def _init_feel_audio(self) -> None:
        if self._feel_audio_ready:
            return
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self._snd_spawn = self._make_tone_sound(520, 45, 0.12)
            self._snd_tower_hit = self._make_tone_sound(180, 55, 0.1)
            self._snd_tree_hit = self._make_tone_sound(95, 160, 0.22)
            self._feel_audio_ready = True
            self._apply_sfx_volume()
        except Exception:
            self._feel_audio_ready = False

    def _sfx_volume_float(self) -> float:
        return self.sfx_volume_level / float(SFX_VOLUME_MAX)

    def _apply_sfx_volume(self) -> None:
        if not self._feel_audio_ready:
            return
        vol = self._sfx_volume_float()
        for snd in (self._snd_spawn, self._snd_tower_hit, self._snd_tree_hit):
            if snd:
                snd.set_volume(vol)

    def _change_sfx_volume(self, delta: int) -> None:
        self.sfx_volume_level = max(0, min(SFX_VOLUME_MAX, self.sfx_volume_level + delta))
        self._apply_sfx_volume()
        if self.sfx_volume_level > 0:
            self._play_spawn_chirp()

    def _update_settings_volume_label(self) -> None:
        self.settings_volume_label = str(self.sfx_volume_level)
        if hasattr(self, "start_screen"):
            self.start_screen.set_settings_volume_label(self.settings_volume_label)

    def _make_tone_sound(self, freq: float, duration_ms: int, volume: float):
        sr = 22050
        n = max(1, int(sr * duration_ms / 1000))
        t = np.arange(n, dtype=np.float64) / sr
        env = np.linspace(0.35, 0.0, n, dtype=np.float64) ** 0.8 + 0.15
        wave = (volume * 32767.0 * env * np.sin(2 * np.pi * freq * t)).astype(np.int16)
        stereo = np.column_stack((wave, wave))
        return pygame.sndarray.make_sound(stereo)

    def _play_spawn_chirp(self) -> None:
        if self.sfx_volume_level <= 0:
            return
        self._init_feel_audio()
        if self._feel_audio_ready and self._snd_spawn:
            self._snd_spawn.play()

    def _play_tower_hit(self, now_ms: int) -> None:
        if self.sfx_volume_level <= 0:
            return
        if now_ms - self._last_tower_sound_ms < 90:
            return
        self._last_tower_sound_ms = now_ms
        self._init_feel_audio()
        if self._feel_audio_ready and self._snd_tower_hit:
            self._snd_tower_hit.play()

    def _play_tree_damage(self) -> None:
        if self.sfx_volume_level <= 0:
            return
        self._init_feel_audio()
        if self._feel_audio_ready and self._snd_tree_hit:
            self._snd_tree_hit.play()

    def _push_floating_text(self, text: str, x: float, y: float, color: rgb, vy: float = -28.0, life: float = 0.9) -> None:
        self._floating_text.append({
            "text": text, "x": x, "y": y, "vy": vy, "life": life, "color": color,
        })

    def _update_feel(self) -> None:
        dt = max(0.001, self.clock.get_time() / 1000.0)
        for ft in self._floating_text:
            ft["y"] += ft["vy"] * dt
            ft["life"] -= dt
        self._floating_text = [f for f in self._floating_text if f["life"] > 0]

    def _draw_floating_text(self) -> None:
        for ft in self._floating_text:
            surf = self.cached_font_large.render(ft["text"], True, ft["color"])
            self.surface.blit(surf, (int(ft["x"] - surf.get_width() // 2), int(ft["y"])))

    def _tree_of_life_float_pos(self) -> tuple[int, int]:
        """Screen center of the Tree of Life portrait (tree_of_life.png)."""
        origin = (210, 30)
        if hasattr(self, "cached_tree_life_image"):
            rect = self.cached_tree_life_image.get_rect(topleft=origin)
            return rect.centerx, rect.centery
        return origin[0] + 80, origin[1] + 90

    def _on_tree_damage(self, finished_mobs: list) -> None:
        if not finished_mobs:
            return
        self._play_tree_damage()
        cx, cy = self._tree_of_life_float_pos()
        for i, mob in enumerate(finished_mobs):
            dmg = int(mob.dmg)
            if dmg <= 0:
                continue
            self._push_floating_text(
                f"-{dmg}",
                cx + random.randint(-14, 14),
                cy - 10 - i * 24,
                (230, 45, 35),
            )

    def _draw_mission_briefing(self) -> None:
        veil = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        veil.fill((8, 12, 28, 210))
        self.surface.blit(veil, (0, 0))
        title = self.cached_font_large.render("You are the infestation.", True, UI_BORDER_BROWN)
        sub = self.cached_font_medium.render("Drain the Tree of Life. Be careful of where you step...", True, HUD_TEXT_BROWN_LIGHT)
        c1 = self.cached_font_small.render("Build tiles spawn to the tree. SPACE starts a 30-second assault.", True, HUD_TEXT_BROWN_LIGHT)
        c2 = self.cached_font_small.render("Spend branches to buy bugs before time runs out.", True, HUD_TEXT_BROWN_LIGHT)
        c3 = self.cached_font_small.render("Kill the tree before the timer hits zero!", True, HUD_TEXT_BROWN_ACCENT)
        block_w = max(title.get_width(), sub.get_width(), c1.get_width(), c2.get_width(), c3.get_width()) + 48
        block_h = title.get_height() + sub.get_height() + c1.get_height() + c2.get_height() + c3.get_height() + 70
        bx = (self.width - block_w) // 2
        by = (self.height - block_h) // 2
        panel = pygame.Surface((block_w, block_h), pygame.SRCALPHA)
        panel.fill((30, 40, 70, 230))
        pygame.draw.rect(panel, UI_BORDER_BROWN, panel.get_rect(), 2)
        self.surface.blit(panel, (bx, by))
        y = by + 20
        self.surface.blit(title, (bx + 24, y))
        y += title.get_height() + 8
        self.surface.blit(sub, (bx + 24, y))
        y += sub.get_height() + 8
        self.surface.blit(c1, (bx + 24, y))
        y += c1.get_height() + 6
        self.surface.blit(c2, (bx + 24, y))
        y += c2.get_height() + 8
        self.surface.blit(c3, (bx + 24, y))

    def get_available_mobs_for_wave(self) -> list[int]:
        return [i for i in range(5) if self.is_mob_unlocked(i)]

    def _mob_grid_slot_index(self, mob_index: int) -> int:
        """Map mob type to fixed slot in the 2×3 grid (row-major)."""
        return mob_index

    def _mob_grid_slot_center(self, slot: int) -> tuple[int, int]:
        return MOB_GRID_CENTERS[slot]

    def _mob_grid_slot_rect(self, slot: int) -> pygame.Rect:
        cx, cy = self._mob_grid_slot_center(slot)
        return pygame.Rect(
            cx - MOB_GRID_SLOT_W // 2,
            cy - MOB_GRID_SLOT_H // 2,
            MOB_GRID_SLOT_W,
            MOB_GRID_SLOT_H,
        )

    def _draw_mob_slot_frame(self, rect: pygame.Rect, *, selected: bool = False) -> None:
        """Border aligned to the full slot rect (UI slots are already drawn underneath)."""
        pygame.draw.rect(self.surface, (58, 42, 30), rect, 1)
        if selected:
            pygame.draw.rect(self.surface, (255, 220, 0), rect, 3)

    def _refresh_wave_and_branch_hud(self) -> None:
        """Keep wave + branch labels in sync when a new wave starts or branches change."""
        roman = self.intToRoman(self.wave)
        self.cached_text_surfaces['wave'] = self.cached_font_large.render(
            "Wave: " + roman, True, HUD_TEXT_BROWN_DARK
        )
        self.cached_text_surfaces['branches'] = self.cached_font_large.render(
            f": {self.current_branches}", True, HUD_TEXT_BROWN
        )
        self.last_wave = self.wave
        self.last_branches = self.current_branches

    def begin_wave_setup(self) -> None:
        """New wave: map, branch budget, and fresh tree HP (grows each wave)."""
        stage = self.stage_for_wave(self.wave)
        if stage != getattr(self, "current_stage", None):
            self._apply_stage_visuals(stage)
        self._refresh_ingame_settings_hitboxes()
        self.current_level_id = Maps.level_for_wave(self.wave)
        self.reset_grid(self.current_level_id)
        self.current_branches = Maps.branches_for_wave(self.wave)
        self.tree_health_max = Maps.tree_health_for_wave(self.wave)
        self.tree_health = self.tree_health_max
        self.mobs = []
        self.round_active = False
        self.round_ended = True
        self.edit_mode = True
        self.last_wave = -1
        self.last_branches = -1
        self.wave_deadline_ms = None
        self.last_timer_second = -1
        self._tree_kill_handled = False
        self.mob_spawn_cooldown_until = {i: 0 for i in range(5)}
        if hasattr(self, 'cached_font_large'):
            self._refresh_wave_and_branch_hud()
            self._refresh_timer_hud(force=True)

    def _tower_range_pixels(self, radius_tiles: float) -> float:
        w, h = self.spriteSize
        cell = (w / 2 + h / 4) / 1.15
        return radius_tiles * cell

    def _tower_combat_stats(self) -> dict:
        """Map grid tile -> [range_px, damage, cooldown_ms]."""
        out = {}
        for tile, (_t_type, spec) in TOWER_TILE_TYPES.items():
            cooldown = int(1000 / spec["attack_speed"])
            out[tile] = [
                self._tower_range_pixels(spec["range_tiles"]),
                spec["attack"],
                cooldown,
            ]
        return out

    def _on_tree_destroyed(self) -> None:
        """Tree HP hit zero: advance to next wave (or win on final wave)."""
        if self._tree_kill_handled or not self.game_active:
            return
        self._tree_kill_handled = True
        self.mobs = []
        self.round_active = False
        self.wave_deadline_ms = None
        pygame.mouse.set_visible(True)

        if self.wave >= MAX_WAVES:
            self.victory()
            return

        self.wave += 1
        if self.wave > MAX_WAVES:
            self.defeat()
            return
        self.begin_wave_setup()
        if hasattr(self, "cached_font_large"):
            self._refresh_wave_and_branch_hud()

    def _start_wave_combat(self) -> None:
        """Begin the timed combat phase for this wave."""
        self.edit_mode = False
        self.round_active = True
        self.round_ended = False
        now = pygame.time.get_ticks()
        self.wave_deadline_ms = now + WAVE_COMBAT_SECONDS * 1000
        self.last_timer_second = -1

    def _wave_time_remaining_seconds(self) -> int:
        if self.wave_deadline_ms is None:
            return WAVE_COMBAT_SECONDS
        remaining_ms = self.wave_deadline_ms - pygame.time.get_ticks()
        return max(0, int((remaining_ms + 999) // 1000))

    def _refresh_timer_hud(self, force: bool = False) -> None:
        sec = self._wave_time_remaining_seconds()
        if not force and sec == self.last_timer_second:
            return
        in_combat = (
            self.round_active
            and not self.edit_mode
            and self.wave_deadline_ms is not None
        )
        color = HUD_TEXT_BROWN_ACCENT if in_combat and sec <= 10 else HUD_TEXT_BROWN
        unit = "sec"
        self.cached_text_surfaces['timer'] = self.cached_font_large.render(
            f"{sec} {unit}", True, color
        )
        self.last_timer_second = sec

    def _blit_hud_midleft(self, surface_key: str, anchor: tuple[int, int]) -> None:
        surf = self.cached_text_surfaces.get(surface_key)
        if surf is None:
            return
        dest = surf.get_rect(midleft=anchor)
        self.surface.blit(surf, dest)

    def _draw_hud_branch_and_timer(self) -> None:
        """Draw branch count + countdown beside icons in UI_play.png (text anchors only)."""
        self._blit_hud_midleft('branches', HUD_BRANCH_TEXT_ANCHOR)
        self._refresh_timer_hud()
        self._blit_hud_midleft('timer', HUD_TIMER_TEXT_ANCHOR)

    def _mob_spawn_on_cooldown(self, mob_index: int) -> bool:
        return pygame.time.get_ticks() < self.mob_spawn_cooldown_until.get(mob_index, 0)

    def _mob_spawn_cooldown_remaining(self, mob_index: int) -> float:
        """0.0 = ready, 1.0 = cooldown just started."""
        until = self.mob_spawn_cooldown_until.get(mob_index, 0)
        remaining_ms = until - pygame.time.get_ticks()
        if remaining_ms <= 0:
            return 0.0
        return remaining_ms / float(MOB_SPAWN_COOLDOWN_MS)

    def _start_mob_spawn_cooldown(self, mob_index: int) -> None:
        self.mob_spawn_cooldown_until[mob_index] = pygame.time.get_ticks() + MOB_SPAWN_COOLDOWN_MS

    def _draw_spawn_cooldown_overlay(self, x_pos: int, y_pos: int, box_w: int, box_h: int, mob_index: int) -> None:
        """Semi-transparent square shrinking toward the bottom as cooldown ends."""
        frac = self._mob_spawn_cooldown_remaining(mob_index)
        if frac <= 0:
            return
        overlay_h = max(1, int(box_h * frac))
        overlay = pygame.Surface((box_w, overlay_h), pygame.SRCALPHA)
        overlay.fill((30, 35, 45, 155))
        self.surface.blit(overlay, (x_pos, y_pos))

    def _spawn_mob_on_path(self, mob_index: int) -> bool:
        """Spawn one mob if the path is valid and the player can afford it."""
        if self._mob_spawn_on_cooldown(mob_index):
            return False
        if self.current_branches < self.mob_costs[mob_index]:
            return False
        pts = self.get_path_waypoints()
        if len(pts) < 2:
            return False
        px, py = self.get_map_pivot()
        self.mobs.append(Mob(pts, self.spriteSize, px, py, mob_index))
        self._start_mob_spawn_cooldown(mob_index)
        self._play_spawn_chirp()
        return True

    def _can_player_spawn_anything(self) -> bool:
        if len(self.get_path_waypoints()) < 2:
            return False
        for i in self.get_available_mobs_for_wave():
            if self.is_mob_unlocked(i) and self.current_branches >= self.mob_costs[i]:
                return True
        return False

    def _round_failed(self) -> None:
        """Combat ended but the tree is still alive."""
        if not self.round_active or not self.game_active or self.tree_health <= 0:
            return
        self.mobs = []
        self.round_active = False
        self.wave_deadline_ms = None
        pygame.mouse.set_visible(True)
        self.defeat()

    def _dev_skip_wave(self) -> None:
        """Hidden dev shortcut: advance wave (works during build — path not required)."""
        if self.showing_start_screen or self.showing_cutscene:
            return
        self.mission_briefing_active = False
        self.mobs = []
        self.round_active = False
        self.wave_deadline_ms = None
        self._tree_kill_handled = False
        self.tree_health = 0
        self._on_tree_destroyed()

    def initiate_cached_images(self):
        """Pre-load and cache all background images to avoid loading every frame"""
        try:
            self._load_all_stage_ui_caches()
            self.current_stage = self.stage_for_wave(self.wave)
            self._apply_stage_visuals(self.current_stage)
            self._refresh_ingame_settings_hitboxes()
            self._update_settings_volume_label()

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
                scroll_path = os.path.join(BGROUND_DIR, scroll_name)
                if not os.path.isfile(scroll_path):
                    scroll_path = os.path.join(ASSETS_UI_DIR, 'scroll', scroll_name)
                scroll_raw = pygame.image.load(scroll_path).convert_alpha()
                self.cached_scrolls[i] = pygame.transform.scale(scroll_raw, (int(scroll_raw.get_width() * 0.8), int(scroll_raw.get_height() * 0.8)))
            
            # Book of life - use book1.png from assets
            book_of_lifeopen_raw = pygame.image.load(os.path.join(ASSETS_UI_DIR, 'book', 'book1.png')).convert_alpha()
            self.cached_book_of_lifeopen = pygame.transform.scale(book_of_lifeopen_raw, (int(book_of_lifeopen_raw.get_width() * 0.55), int(book_of_lifeopen_raw.get_height() * 0.55)))
            
            # Surrender page
            surrender_raw = pygame.image.load(os.path.join(ASSETS_UI_DIR, 'surrenderpage.png')).convert_alpha()
            self.cached_surrender_page = pygame.transform.scale(surrender_raw, (int(surrender_raw.get_width() * 0.8), int(surrender_raw.get_height() * 0.8)))
            
            # Load hammer / shovel cursor animations
            self.hammer_images = []
            hammer_dir = os.path.join(ASSETS_UI_DIR, 'hammer')
            if os.path.exists(hammer_dir):
                hammer_files = sorted([f for f in os.listdir(hammer_dir) if f.endswith('.png')])
                for hammer_file in hammer_files:
                    hammer_img = pygame.image.load(os.path.join(hammer_dir, hammer_file)).convert_alpha()
                    self.hammer_images.append(pygame.transform.scale(hammer_img, CURSOR_TOOL_SIZE))

            self.shovel_images = []
            shovel_dir = os.path.join(ASSETS_UI_DIR, 'shovel')
            if os.path.exists(shovel_dir):
                shovel_files = sorted([f for f in os.listdir(shovel_dir) if f.endswith('.png')])
                for shovel_file in shovel_files:
                    shovel_img = pygame.image.load(os.path.join(shovel_dir, shovel_file)).convert_alpha()
                    self.shovel_images.append(pygame.transform.scale(shovel_img, SHOVEL_CURSOR_SIZE))

            self.cursor_animation_frame = 0
            self.cursor_animation_counter = 0
            self.shovel_animation_counter = 0
            self.shovel_animation_frame = 0
            self.hammer_animating = False
            self.hammer_animation_duration = 0
            self.shovel_animating = False
            self.shovel_animation_duration = 0
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
                    pass
            
        except Exception as e:
            import traceback
            traceback.print_exc()
    
    def initiate_cached_fonts(self):
        """Pre-load fonts to avoid creating them every frame"""
        font_path = os.path.join(os.path.join(os.path.dirname(__file__), 'fonts'), "Dico.ttf")
        self.cached_font_large = pygame.font.Font(font_path, 35)
        self.cached_font_medium = pygame.font.Font(font_path, 25)
        self.cached_font_small = pygame.font.Font(font_path, 20)
    
    def get_map_pivot(self) -> tuple[float, float]:
        return self.width / 3, 125 * 2.6

    def _game_input_locked(self) -> bool:
        """True while intro overlay is up — no map/UI interaction."""
        return self.mission_briefing_active

    def _path_edit_locked(self) -> bool:
        """True while overlays block hammer/shovel path editing."""
        return self._game_input_locked() or self.showing_scroll or self.showing_book or self._ingame_menu_open()

    def _clear_path_editing(self) -> None:
        self.set_path = False
        self.rm_path = False
        self.hammer_animating = False
        self.shovel_animating = False

    def _is_v_path_tile(self, tile_val) -> bool:
        """Walkable path tiles (not towers or bushes)."""
        return tile_val in (1, -1)

    def _is_v_bush_tile(self, tile_val) -> bool:
        return tile_val == -8

    def _obstacle_draw_alpha(self, tile_val, i: int, j: int) -> int:
        """Hold V: hide towers/trees (alpha 0). Hover still dims one tower type."""
        if self.see_through_obstacles:
            if tile_val in ("b2", "l1", -9):
                return OBSTACLE_SEE_THROUGH_ALPHA
            return 255
        if tile_val == self.hovered_tower_type:
            return TOWER_HOVER_ALPHA
        return 255

    def _world_to_grid(self, world_x: float, world_y: float) -> tuple[int, int]:
        pivot_x, pivot_y = self.get_map_pivot()
        w, h = self.spriteSize
        half_w, half_h = w / 2, h / 4
        rel_x, rel_y = world_x - pivot_x, world_y - pivot_y
        grid_j = (rel_x / half_w + rel_y / half_h) / 2
        grid_i = (rel_y / half_h - rel_x / half_w) / 2
        return int(np.floor(grid_i)), int(np.floor(grid_j))

    def _rebuild_poison_bush_cells(self) -> None:
        """Bush tiles (-8) and path placed on them stay poison sources."""
        cells: set[tuple[int, int]] = set()
        for i in range(self.grid_rows):
            for j in range(self.grid_cols):
                if self.world_grid[i][j] == -8:
                    cells.add((i, j))
        for ij in self.poison_bush_cells:
            i, j = ij
            if 0 <= i < self.grid_rows and 0 <= j < self.grid_cols:
                if self.world_grid[i][j] == 1:
                    cells.add(ij)
        self.poison_bush_cells = cells

    def _update_mob_poison_status(self) -> None:
        for mob in self.mobs:
            if mob.at_end or mob.health <= 0:
                continue
            gi, gj = self._world_to_grid(mob.pos.x, mob.pos.y)
            if (gi, gj) in self.poison_bush_cells:
                mob.poisoned = True

    def sync_map_layout(self) -> None:
        """Match loop bounds and tile scale to the active Maps.py level size."""
        self.grid_rows, self.grid_cols = Maps.grid_dimensions(self.world_grid)
        self.grid_size = max(self.grid_rows, self.grid_cols)
        self.map_scale = REFERENCE_GRID_SIZE / float(self.grid_size)

    def tile_scale_factor(self) -> float:
        return TILE_DRAW_SCALE * self.map_scale

    def initiate_blocks(self):
        scale_factor = self.tile_scale_factor()
        self.tiles = {}
        for root, dir, files in os.walk(ASSETS_DIR):
            all_tiles = sorted(files)
            for tile in all_tiles:
                name = tile.split(".")[0]
                if tile == "path.png":
                    self.path_icon = self.load_image(tile)
                    ps = self.tile_scale_factor()
                    self.path_icon = pygame.transform.scale(
                        self.path_icon,
                        (int(self.path_icon.get_width() * ps), int(self.path_icon.get_height() * ps)),
                    )
                temp_sprite = self.load_image(tile)
                self.temp_tile = pygame.transform.scale(temp_sprite,(int(temp_sprite.get_width() * scale_factor), int(temp_sprite.get_height() * scale_factor)))
                self.tiles[name] = self.temp_tile
        self.spriteSize = (self.tiles["dark_grass"].get_width(), self.tiles["dark_grass"].get_height())
        self.h_tiles = {name : self.highlight_block(tile) for name, tile in self.tiles.items()}

    def initiate_towers(self):
        scale_factor = self.tile_scale_factor()
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
        pygame.display.set_caption("Heliosylva: Power Offense — you are the wave")
        self.surface = pygame.display.set_mode((self.width,self.height))
        self.showing_start_screen = True
        self.showing_settings_screen = False
        self.showing_instructions_scene = False
        self.start_screen = StartScreen(self.surface)
        self.clock = pygame.time.Clock()
        self.initiate_cutscenes()
        self.rebuild_map_scaled_assets()
        self.initiate_clouds()
        self.initiate_tree_health_bars()
        self.initiate_cached_images()  # Pre-load and cache background images
        self.initiate_cached_fonts()  # Pre-load fonts
        self._refresh_wave_and_branch_hud()
        self._refresh_timer_hud(force=True)
        self.run_event_loop()

    def quit_app(self) -> None:
        pygame.quit()
        sys.exit()

    #Optimize This
    def map_grid(self): 
        
        w, h = self.spriteSize

        half_w = w / 2
        half_h = h / 4

        pivot_x, pivot_y = self.get_map_pivot()

        rel_x = self.x - pivot_x
        rel_y = self.y - pivot_y

        mouse_j = (rel_x / half_w + rel_y / half_h) / 2
        mouse_i = (rel_y / half_h - rel_x / half_w) / 2

        grid_i, grid_j = int(np.floor(mouse_i)), int(np.floor(mouse_j))

        self.hovered_tower_type = None
        if self._game_input_locked():
            grid_i, grid_j = -1, -1

        for i in range(self.grid_rows):
            for j in range(self.grid_cols):

                draw_x = pivot_x + (j - i) * half_w - half_w
                draw_y = pivot_y + (j + i) * half_h

                # Hover effect
                # For Towers
                is_hovered = (i == grid_i and j == grid_j) and not self._game_input_locked()
                if is_hovered:
                    tile_value = self.world_grid[i][j]
                    if tile_value in [-9, -8, "b2", "l1"]:
                        self.hovered_tower_type = tile_value
                
                # Handle path editing (grass, path, and bush -8)
                tile_int = self.world_grid[i][j]
                can_edit_path = (
                    self.edit_mode
                    and not self._path_edit_locked()
                    and is_hovered
                    and (
                        (type(tile_int) == int and tile_int >= 0)
                        or tile_int == -8
                    )
                )
                if can_edit_path:
                    self.highlight = True
                    if self.set_path and self.paths_remaining > 0:
                        if tile_int != 1:
                            if tile_int == -8:
                                self.poison_bush_cells.add((i, j))
                            self.world_grid[i][j] = 1
                            self.paths_remaining -= 1
                            self.tile_changed = True
                            self.hammer_animating = True
                            self.hammer_animation_duration = 0.5
                    elif self.rm_path:
                        if tile_int == 1:
                            if (i, j) in self.poison_bush_cells:
                                self.world_grid[i][j] = -8
                            else:
                                self.world_grid[i][j] = 0
                            self.paths_remaining += 1
                            self.tile_changed = True
                            self.shovel_animating = True
                            self.shovel_animation_duration = 0.5
                else:
                    self.highlight = False
                
                # Draw tiles with hover highlighting based on B key state
                # When B is pressed (build = False, delete mode): highlight path tiles on hover
                # When B is not pressed (build = True, build mode): highlight grass tiles on hover
                if self.world_grid[i][j] == 0:
                    if self.see_through_obstacles:
                        self.surface.blit(self.h_tiles["dark_grass"], (draw_x, draw_y))
                    elif is_hovered and self.build and not self._path_edit_locked():
                        self.surface.blit(self.h_tiles["dark_grass"], (draw_x, draw_y))
                    else:
                        self.surface.blit(self.tiles["dark_grass"], (draw_x, draw_y))
                elif self.world_grid[i][j] == 1:
                    sprite = self.get_path_sprite(i, j)
                    if self.see_through_obstacles and self._is_v_path_tile(1):
                        self.surface.blit(self.highlight_block(sprite), (draw_x, draw_y))
                    elif is_hovered and not self.build and not self._path_edit_locked():
                        self.surface.blit(self.highlight_block(sprite), (draw_x, draw_y))
                    else:
                        self.surface.blit(sprite, (draw_x, draw_y))
                elif self.world_grid[i][j] == -1:
                    sprite = self.get_spawn_sprite(i, j)
                    if self.see_through_obstacles and self._is_v_path_tile(-1):
                        self.surface.blit(self.highlight_block(sprite), (draw_x, draw_y))
                    else:
                        self.surface.blit(sprite, (draw_x, draw_y))
                    valid_path = self.is_grid_valid(self.world_grid)
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
                    if (
                        self.see_through_obstacles and self._is_v_bush_tile(-8)
                    ) or (
                        is_hovered and self.build and not self._path_edit_locked()
                    ):
                        self.surface.blit(self.h_tiles["dark_grass"], (draw_x, draw_y))
                    else:
                        self.surface.blit(self.tiles["dark_grass"], (draw_x, draw_y))

    def find_all_ends(self):
        """Find all -1 positions (start and end points)"""
        ends = []
        for i in range(self.grid_rows):
            for j in range(self.grid_cols):
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
            if 0 <= ni < self.grid_rows and 0 <= nj < self.grid_cols:
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
                if 0 <= ni < self.grid_rows and 0 <= nj < self.grid_cols:
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
        bl = j < self.grid_cols - 1 and self.world_grid[i][j+1] in [1, -1]
        br = i < self.grid_rows - 1 and self.world_grid[i+1][j] in [1, -1]

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
        bl = j < self.grid_cols - 1 and self.world_grid[i][j+1] in [1, -1]
        br = i < self.grid_rows - 1 and self.world_grid[i+1][j] in [1, -1]

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
    def update_tower_animations(self):
        """Update tower idle animations without combat logic."""
        for tower_key in self.tower_states:
            state = self.tower_states[tower_key]["status"]
            # For towers, we need to know the tower type
            # Find which tower this key belongs to
            i, j = tower_key
            tile = self.world_grid[i][j] if i < self.grid_rows and j < self.grid_cols else None
            if tile in TOWER_TILE_TYPES:
                t_type = TOWER_TILE_TYPES[tile][0]
                # Always animate idle towers
                self.tower_states[tower_key]["frame"] += 0.15
                if self.tower_states[tower_key]["frame"] >= len(self.tower_data[t_type][state]):
                    self.tower_states[tower_key]["frame"] = 0

    def handle_tower_logic(self):
        """Handle tower combat logic only (no animation)."""
        now = pygame.time.get_ticks()
        stats = self._tower_combat_stats()
        
        w, h = self.spriteSize
        half_w, half_h = w / 2, h / 4
        pivot_x, pivot_y = self.get_map_pivot()

        for i in range(self.grid_rows):
            for j in range(self.grid_cols):
                tile = self.world_grid[i][j]
                if tile in stats:
                    t_type = TOWER_TILE_TYPES[tile][0]
                    tower_key = (i, j)
                    
                    if tower_key not in self.tower_states:
                        self.tower_states[tower_key] = {"last_atk": 0, "frame": 0, "status": "idle", "flip": False}

                    t_pos = pygame.Vector2(pivot_x + (j - i) * half_w, pivot_y + (j + i) * half_h - (h * 1.2))
                    in_range = [m for m in self.mobs if t_pos.distance_to(m.pos) <= stats[tile][0]]
                    
                    if in_range:
                        target = max(in_range, key=lambda m: m.target_idx)
                        
                        # Track mob direction for flipping
                        if target.pos.x < t_pos.x:
                            self.tower_states[tower_key]["flip"] = False
                        else:
                            self.tower_states[tower_key]["flip"] = True

                        if now - self.tower_states[tower_key]["last_atk"] > stats[tile][2]:
                            target.health -= stats[tile][1]
                            self._play_tower_hit(now)
                            self.tower_states[tower_key]["last_atk"] = now
                            self.tower_states[tower_key]["status"] = "attack"
                            self.tower_states[tower_key]["frame"] = 0

    def _draw_ui_debug_outlines(self) -> None:
        if not DEBUG_UI_OUTLINES:
            return
        for rect in self.ui_hitboxes.values():
            pygame.draw.rect(self.surface, (255, 0, 0), rect, 2)

    def _surrender_panel_pos(self) -> tuple[int, int]:
        if not hasattr(self, 'cached_surrender_page'):
            return (0, 0)
        x = (self.width - self.cached_surrender_page.get_width()) // 2
        y = (self.height - self.cached_surrender_page.get_height()) // 2
        return x, y

    def draw_UI(self) -> None:
        self.ui_hitboxes = {}

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

        if self.showing_book:
            self.surface.blit(self.cached_book_of_lifeopen, (-40, 230))
        
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
        
        # Settings button (slightly larger than baked UI label for easier clicks)
        self.ui_hitboxes['settings'] = pygame.Rect(835, 685, 120, 35)

        # Dev-only: unlabeled skip control (top-left corner, no in-game label)
        dev_skip_rect = pygame.Rect(6, 6, 16, 16)
        self.ui_hitboxes['dev_skip_wave'] = dev_skip_rect
        pygame.draw.rect(self.surface, (120, 145, 165), dev_skip_rect)
        pygame.draw.rect(self.surface, (90, 110, 130), dev_skip_rect, 1)

        if self.round_active and not self.edit_mode:
            spawn_button_rect = pygame.Rect(700, 650, 180, 45)
            self.ui_hitboxes['spawn_wave'] = spawn_button_rect
            can_spawn = (
                self.current_branches >= self.mob_costs[self.selected_mob_type]
                and not self._mob_spawn_on_cooldown(self.selected_mob_type)
            )
            button_color = (0, 160, 0) if can_spawn else (100, 100, 100)
            pygame.draw.rect(self.surface, button_color, spawn_button_rect)
            pygame.draw.rect(self.surface, (255, 255, 255), spawn_button_rect, 2)
            spawn_text = self.cached_font_medium.render('SPAWN MOB', True, (255, 255, 255))
            spawn_text_rect = spawn_text.get_rect(center=spawn_button_rect.center)
            self.surface.blit(spawn_text, spawn_text_rect)

        if (
            self.last_wave != self.wave
            or self.last_branches != self.current_branches
            or 'wave' not in self.cached_text_surfaces
            or 'branches' not in self.cached_text_surfaces
        ):
            self._refresh_wave_and_branch_hud()

        if self.last_paths_remaining != self.paths_remaining:
            self.cached_text_surfaces['tiles'] = self.cached_font_medium.render(
                f'Tiles: {self.paths_remaining}', True, HUD_TEXT_BROWN_DARK
            )
            self.last_paths_remaining = self.paths_remaining
        elif 'tiles' not in self.cached_text_surfaces:
            self.cached_text_surfaces['tiles'] = self.cached_font_medium.render(
                f'Tiles: {self.paths_remaining}', True, HUD_TEXT_BROWN_DARK
            )

        active = len(self.mobs)
        if self.last_active_mobs != active:
            self.cached_text_surfaces['units'] = self.cached_font_large.render(
                f'On field: {active}', True, HUD_TEXT_BROWN
            )
            self.last_active_mobs = active
        elif 'units' not in self.cached_text_surfaces:
            self.cached_text_surfaces['units'] = self.cached_font_large.render(
                f'On field: {active}', True, HUD_TEXT_BROWN
            )

        self.surface.blit(self.cached_text_surfaces['wave'], HUD_WAVE_POS)
        self.surface.blit(self.cached_text_surfaces['tiles'], HUD_TILES_POS)
        self._draw_hud_branch_and_timer()
        self.surface.blit(self.cached_text_surfaces['units'], (1130, 550))

        if self.showing_surrender and hasattr(self, 'cached_surrender_page'):
            surrender_x, surrender_y = self._surrender_panel_pos()
            self.surface.blit(self.cached_surrender_page, (surrender_x, surrender_y))
            self.ui_hitboxes['surrender_back'] = SURRENDER_HITBACK.move(
                surrender_x, surrender_y
            ).inflate(16, 14)
            self.ui_hitboxes['surrender_no'] = SURRENDER_HIT_NO.move(
                surrender_x, surrender_y
            )
            self.ui_hitboxes['surrender_yes'] = SURRENDER_HIT_YES.move(
                surrender_x, surrender_y
            )

        if self.showing_ingame_settings:
            self._draw_ingame_settings_overlay()
        elif self.showing_ingame_instructions and hasattr(self, "cached_instr_page"):
            self._draw_ingame_subpage_overlay(self.cached_instr_page)
        elif self.showing_ingame_credits:
            page = self.cached_settings_by_stage.get(
                self.current_stage,
                self.cached_settings_by_stage.get(STAGE_SUNSHINE),
            )
            if page:
                self._draw_ingame_subpage_overlay(page)

        self._draw_ui_debug_outlines()

        
        # self.settings = self.load_world('settings.png')
        # self.settings = pygame.transform.scale(self.settings, (int(self.settings.get_width() * 0.7), int(self.settings.get_height() * 0.7)))
        #self.surface.blit(self.settings, (760, 645))
        #self.surface.blit(scale_fix_boe, (673, 525))
        #self.surface.blit(scale_fix_bol, (673, 350))
        #self.surface.blit(scale_fix_scroll, (670, 230)) THIS IS THE SCROLL
    
    def draw_spawn_boxes(self):
        """Mob buttons in the 2×3 Spawn grid on UI_play.png (5 mobs + 1 empty slot)."""
        for slot in range(MOB_GRID_COLS * MOB_GRID_ROWS):
            slot_rect = self._mob_grid_slot_rect(slot)
            cx, cy = slot_rect.centerx, slot_rect.centery

            if slot < 5:
                mob_index = slot
                unlocked = self.is_mob_unlocked(mob_index)
                selected = mob_index == self.selected_mob_type

                if not unlocked:
                    dim = pygame.Surface(slot_rect.size, pygame.SRCALPHA)
                    dim.fill((20, 15, 10, 140))
                    self.surface.blit(dim, slot_rect.topleft)

                if unlocked and mob_index in self.cached_mob_icons:
                    mob_icon = self.cached_mob_icons[mob_index]
                    icon_rect = mob_icon.get_rect(
                        center=(cx, cy - 6),
                    )
                    self.surface.blit(mob_icon, icon_rect)
                    cost = self.mob_costs[mob_index]
                    affordable = self.current_branches >= cost
                    cost_color = (0, 200, 0) if affordable else (200, 0, 0)
                    cost_text = self.cached_font_small.render(str(cost), True, cost_color)
                    cost_rect = cost_text.get_rect(
                        midbottom=(cx, slot_rect.bottom - 3),
                    )
                    self.surface.blit(cost_text, cost_rect)
                    self.ui_hitboxes[f'spawn_box_{mob_index}'] = slot_rect
                    self._draw_mob_slot_frame(slot_rect, selected=selected)
                    self._draw_spawn_cooldown_overlay(
                        slot_rect.x, slot_rect.y, slot_rect.width, slot_rect.height, mob_index
                    )
                else:
                    lock_txt = self.cached_font_small.render(
                        f"W{self.get_unlock_wave(mob_index)}", True, HUD_TEXT_BROWN_LIGHT
                    )
                    self.surface.blit(lock_txt, lock_txt.get_rect(center=slot_rect.center))
                    self._draw_mob_slot_frame(slot_rect, selected=False)
            else:
                self._draw_mob_slot_frame(slot_rect, selected=False)
    
    def ui_check_click(self, mouse_pos):
        if self.showing_ingame_settings or self.showing_ingame_instructions or self.showing_ingame_credits:
            return None
        if self.showing_surrender:
            if 'surrender_back' in self.ui_hitboxes and self.ui_hitboxes['surrender_back'].collidepoint(mouse_pos):
                return "SURRENDER_BACK"
            if 'surrender_no' in self.ui_hitboxes and self.ui_hitboxes['surrender_no'].collidepoint(mouse_pos):
                return "SURRENDER_NO"
            if 'surrender_yes' in self.ui_hitboxes and self.ui_hitboxes['surrender_yes'].collidepoint(mouse_pos):
                return "SURRENDER_YES"
            return None

        if 'dev_skip_wave' in self.ui_hitboxes and self.ui_hitboxes['dev_skip_wave'].collidepoint(mouse_pos):
            return "DEV_SKIP_WAVE"

        # Check spawn box clicks (2×3 mob grid)
        for i in range(5):  # 5 mob types
            box_key = f'spawn_box_{i}'
            if box_key in self.ui_hitboxes and self.ui_hitboxes[box_key].collidepoint(mouse_pos):
                return f"SPAWN_BOX_{i}"
        
        # Check scroll page navigation (only while script of evil is open)
        if self.showing_scroll:
            if 'scroll_left' in self.ui_hitboxes and self.ui_hitboxes['scroll_left'].collidepoint(mouse_pos):
                return "SCROLL_LEFT"
            if 'scroll_right' in self.ui_hitboxes and self.ui_hitboxes['scroll_right'].collidepoint(mouse_pos):
                return "SCROLL_RIGHT"
        
        # Check settings button
        if 'settings' in self.ui_hitboxes and self.ui_hitboxes['settings'].collidepoint(mouse_pos):
            return "SETTINGS"

        # Check spawn wave button while round is active
        if 'spawn_wave' in self.ui_hitboxes and self.ui_hitboxes['spawn_wave'].collidepoint(mouse_pos):
            return "SPAWN_WAVE"
        
        # Check book buttons
        if 'book_of_evil' in self.ui_hitboxes and self.ui_hitboxes['book_of_evil'].collidepoint(mouse_pos):
            return "BOOK_OF_EVIL"
        if 'book_of_life' in self.ui_hitboxes and self.ui_hitboxes['book_of_life'].collidepoint(mouse_pos):
            return "BOOK_OF_LIFE"
        return None

    def get_health_frame(self):
        if self.tree_health <= 0:
            return self.health_frames[-1]
        max_hp = getattr(self, "tree_health_max", 1) or 1
        pct = max(0.0, min(1.0, self.tree_health / float(max_hp)))
        n = len(self.health_frames)
        if n <= 1:
            return self.health_frames[0]
        idx = int((1.0 - pct) * (n - 1))
        return self.health_frames[min(max(0, idx), n - 1)]
    
    def draw_tree_of_life(self):
        if self.tree_health > 0:
            current_health_img = self.get_health_frame()
            self.surface.blit(current_health_img, (40, 630))
            if hasattr(self, "cached_font_small"):
                hp_txt = self.cached_font_small.render(
                    f"{int(self.tree_health)} / {int(getattr(self, 'tree_health_max', 1))}",
                    True, HUD_TEXT_BROWN,
                )
                self.surface.blit(hp_txt, (44, 608))
        else:
            pass

    def is_mob_unlocked(self, mob_index: int) -> bool:
        if 0 <= mob_index < len(MOB_UNLOCK_WAVES):
            return self.wave >= MOB_UNLOCK_WAVES[mob_index]
        return False

    def get_unlock_wave(self, mob_index: int) -> int:
        if 0 <= mob_index < len(MOB_UNLOCK_WAVES):
            return MOB_UNLOCK_WAVES[mob_index]
        return 999

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
        pivot_x, pivot_y = self.get_map_pivot()

        rel_x, rel_y = self.x - pivot_x, self.y - pivot_y
        mouse_j = (rel_x / half_w + rel_y / half_h) / 2
        mouse_i = (rel_y / half_h - rel_x / half_w) / 2
        grid_i, grid_j = int(np.floor(mouse_i)), int(np.floor(mouse_j))        
        # Subtle Up/Down: Sine wave based on time
        # 5 is the pixel height of the bob, 0.005 is the speed
        bobbing_offset = np.sin(pygame.time.get_ticks() * 0.005) * 5

        tree_elements = []
        for i in range(self.grid_rows):
            for j in range(self.grid_cols):
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
                        
                        surf.set_alpha(self._obstacle_draw_alpha(tile_val, i, j))

                        if state_info["flip"]:
                            surf = pygame.transform.flip(surf, True, False)

                        tree_elements.append({
                            'z': draw_y, 
                            'type': t_type, 
                            'surf': surf, 
                            'pos': (draw_x, (draw_y - h * 1.2) + bobbing_offset)
                        })
                is_bush = tile_val == -8 or (
                    tile_val == 1 and (i, j) in self.poison_bush_cells
                )
                if tile_val == -9 or is_bush:
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
                        
                        bush_tile = -8 if is_bush else tile_val
                        surf.set_alpha(self._obstacle_draw_alpha(bush_tile, i, j))

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
            pygame.mouse.set_visible(True)
            pygame.display.update()
        elif self.showing_start_screen:
            self.start_screen.draw()
            self.start_screen.draw_buttons()
            if self.showing_settings_screen:
                self._update_settings_volume_label()
                self.start_screen.draw_settings()
                if self.showing_instructions_scene:
                    self.start_screen.draw_instructions()
            pygame.mouse.set_visible(True)
            pygame.display.update()
        else:
            self._update_feel()
            self.surface.fill(self.bgcolor)
            # Use cached images instead of loading every frame (with fallback if not initialized)
            if hasattr(self, 'cached_bg_image'):
                self.surface.blit(self.cached_bg_image, (0, 0))
            else:
                # Fallback: load and scale on the fly if cache not initialized
                background_raw = self.load_world("wbsky.png")
                bg_img = self._scale_sky_to_display(background_raw)
                self.surface.blit(bg_img, (0, 0))
            
            if getattr(self, "current_stage", STAGE_SUNSHINE) == STAGE_SUNSHINE:
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
                ui_raw = self.load_world(STAGE_UI_PLAY.get(self.current_stage, "UI_play.png"))
                self.surface.blit(self._scale_ui_play_image(ui_raw), (0, 0))
            
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
                alive_mobs = [m for m in self.mobs if m.health > 0]
                self.mobs = alive_mobs
                
                # When mobs reach the end, they damage the tree
                finished_mobs = [m for m in self.mobs if m.at_end]
                for m in finished_mobs:
                    self.tree_health -= m.dmg
                    if self.tree_health < 0:
                        self.tree_health = 0
                if finished_mobs:
                    self._on_tree_damage(finished_mobs)
                if self.tree_health <= 0:
                    self._on_tree_destroyed()
                
                self.mobs = [m for m in self.mobs if not m.at_end]
                
                self._update_mob_poison_status()
                for mob in self.mobs:
                    mob.update()
                    layer_queue.append({
                        'z': mob.pos.y, 
                        'type': 'mob', 
                        'obj': mob
                    })

                self.handle_tower_logic()
                self.handle_tower_logic()

            else:
                # When the round is not active, keep mobs on their first frame
                # so they look like the initial spawn pose instead of frozen mid-air.
                for mob in self.mobs:
                    layer_queue.append({
                        'z': mob.pos.y,
                        'type': 'mob',
                        'obj': mob
                    })
            
            # Always animate towers every frame, regardless of round state
            self.update_tower_animations()
            
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

            self.draw_UI()
            
            # Draw cursor icon (hammer for build mode, shovel for delete mode)
            if self.edit_mode and not self._game_input_locked():
                # Hide default cursor in edit mode
                pygame.mouse.set_visible(False)
                
                delta_time = self.clock.get_time() / 1000.0
                if self.hammer_animating:
                    self.hammer_animation_duration -= delta_time
                    if self.hammer_animation_duration <= 0:
                        self.hammer_animating = False
                        self.cursor_animation_counter = 0
                        self.cursor_animation_frame = 0
                if self.shovel_animating:
                    self.shovel_animation_duration -= delta_time
                    if self.shovel_animation_duration <= 0:
                        self.shovel_animating = False
                        self.shovel_animation_counter = 0
                        self.shovel_animation_frame = 0

                if self.build and self.hammer_images:
                    if self.hammer_animating:
                        self.cursor_animation_counter += 0.3
                        self.cursor_animation_frame = int(self.cursor_animation_counter) % len(self.hammer_images)
                    else:
                        self.cursor_animation_frame = 0
                    cursor_img = self.hammer_images[self.cursor_animation_frame]
                    self.surface.blit(cursor_img, (self.x - cursor_img.get_width() // 2, self.y - cursor_img.get_height() // 2))
                elif not self.build and self.shovel_images:
                    if self.shovel_animating:
                        self.shovel_animation_counter += 0.3
                        self.shovel_animation_frame = int(self.shovel_animation_counter) % len(self.shovel_images)
                    else:
                        self.shovel_animation_frame = 0
                    cursor_img = self.shovel_images[self.shovel_animation_frame]
                    ox, oy = SHOVEL_CURSOR_OFFSET
                    self.surface.blit(
                        cursor_img,
                        (
                            self.x - cursor_img.get_width() // 2 + ox,
                            self.y - cursor_img.get_height() // 2 + oy,
                        ),
                    )
            else:
                pygame.mouse.set_visible(True)
            
            self._draw_floating_text()
            if self.mission_briefing_active:
                self._draw_mission_briefing()
            
            pygame.display.update()

    #Optimize This
    def is_grid_valid(self, world_grid):
        grid_rows, grid_cols = Maps.grid_dimensions(world_grid)
        all_path_coords = []
        end_nodes = []  # All -1 positions (start and end)

        for i in range(grid_rows):
            for j in range(grid_cols):
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
                        if 0 <= ni < grid_rows and 0 <= nj < grid_cols:
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
    
    def reset_grid(self, level_id: int | None = None):
        if level_id is not None:
            self.current_level_id = level_id
        maps_data = Maps()
        self.world_grid = copy.deepcopy(maps_data.levels[self.current_level_id])
        self.sync_map_layout()
        self._rebuild_poison_bush_cells()
        area_ratio = (self.grid_size / REFERENCE_GRID_SIZE) ** 2
        self.paths_remaining = max(5, int(BASE_MAX_TILES * area_ratio))
        if pygame.display.get_surface() is not None:
            self.rebuild_map_scaled_assets()

    def rebuild_map_scaled_assets(self) -> None:
        """Re-scale tiles/towers when grid size changes (e.g. 10x10 -> 11x11)."""
        self.initiate_blocks()
        self.initiate_towers()
        self.tower_states = {}

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
                        self.showing_cutscene = False
                        self.game_active = True
                        # If cutscene was victory/defeat, return to start screen
                        if self.cutscene_return_to_start:
                            self.showing_start_screen = True
                            # Reset game state when returning to start
                            self.wave = 1
                            self.begin_wave_setup()
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
                                self.mission_briefing_active = True
                                self._clear_path_editing()
                                self.see_through_obstacles = False
                            if action == "SETTINGS":
                                self.showing_settings_screen = True
                        elif self.showing_instructions_scene:
                            action = self.start_screen.check_closing_instructions(event.pos)
                            if action == "CLOSE":
                                self.showing_instructions_scene = False
                        elif self.showing_settings_screen:
                            action = self.start_screen.check_settings(event.pos)
                            if action == "CLOSE":
                                self.showing_settings_screen = False
                            elif action == "INSTRUCTIONS":
                                self.showing_instructions_scene = True
                            elif action == "SOUND_DOWN":
                                self._change_sfx_volume(-1)
                            elif action == "SOUND_UP":
                                self._change_sfx_volume(1)
                else:
                    if event.type == pygame.MOUSEMOTION:
                        self.x, self.y = event.pos
                    if self.mission_briefing_active:
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_F9:
                            self._dev_skip_wave()
                            continue
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            self.mission_briefing_active = False
                            continue
                        continue
                    if self.showing_ingame_instructions or self.showing_ingame_credits:
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            close = getattr(self, "_ingame_subpage_close_rect", None)
                            if close is None or close.collidepoint(event.pos):
                                self.showing_ingame_instructions = False
                                self.showing_ingame_credits = False
                        continue
                    if self.showing_ingame_settings:
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            action = self._ingame_settings_click(event.pos)
                            if action == "CLOSE":
                                self.showing_ingame_settings = False
                            elif action == "SOUND_DOWN":
                                self._change_sfx_volume(-1)
                                self._update_settings_volume_label()
                            elif action == "SOUND_UP":
                                self._change_sfx_volume(1)
                                self._update_settings_volume_label()
                            elif action == "INSTRUCTIONS":
                                self.showing_ingame_instructions = True
                            elif action == "CREDITS":
                                self.showing_ingame_credits = True
                            elif action == "SURRENDER":
                                self.showing_ingame_settings = False
                                self.showing_surrender = True
                                self._clear_path_editing()
                        continue
                    if self.showing_surrender:
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            ui_action = self.ui_check_click(event.pos)
                            if ui_action in ("SURRENDER_BACK", "SURRENDER_NO"):
                                self.showing_surrender = False
                                self._clear_path_editing()
                            elif ui_action == "SURRENDER_YES":
                                self.showing_surrender = False
                                self.return_to_main_menu()
                        continue
                    if event.type == pygame.MOUSEBUTTONDOWN: # 1 is left, 3 is right
                        if event.button == 1:
                            ui_action = self.ui_check_click(event.pos)
################################################################################################################
                            if ui_action == "BOOK_OF_EVIL":
                                self.showing_scroll = not self.showing_scroll
                                if self.showing_scroll:
                                    self.scroll_page = 0
                                if self.showing_book is True:
                                    self.showing_book = not self.showing_book
                                self._clear_path_editing()
                            elif ui_action == "BOOK_OF_LIFE":
                                self.showing_book = not self.showing_book
                                if self.showing_scroll is True:
                                    self.showing_scroll = not self.showing_scroll
                                self._clear_path_editing()
                            elif ui_action and ui_action.startswith("SPAWN_BOX_"):
                                mob_index = int(ui_action.split("_")[2])
                                if not self.is_mob_unlocked(mob_index):
                                    pass
                                elif self.round_active and not self.edit_mode:
                                    self.selected_mob_type = mob_index
                                    if (
                                        self.current_branches >= self.mob_costs[mob_index]
                                        and not self._mob_spawn_on_cooldown(mob_index)
                                    ):
                                        cost = self.mob_costs[mob_index]
                                        if self._spawn_mob_on_path(mob_index):
                                            self.current_branches -= cost
                                else:
                                    self.selected_mob_type = mob_index
                            elif ui_action == "SPAWN_WAVE":
                                if self.round_active and not self.edit_mode:
                                    available_mobs = self.get_available_mobs_for_wave()
                                    if (
                                        self.selected_mob_type in available_mobs
                                        and self.current_branches >= self.mob_costs[self.selected_mob_type]
                                        and not self._mob_spawn_on_cooldown(self.selected_mob_type)
                                    ):
                                        cost = self.mob_costs[self.selected_mob_type]
                                        if self._spawn_mob_on_path(self.selected_mob_type):
                                            self.current_branches -= cost
                            elif ui_action == "SCROLL_LEFT":
                                if self.scroll_page > 0:
                                    self.scroll_page -= 1
                            elif ui_action == "SCROLL_RIGHT":
                                last = SCRIPT_OF_EVIL_PAGE_COUNT - 1
                                if self.scroll_page < last:
                                    self.scroll_page += 1
                            elif ui_action == "DEV_SKIP_WAVE":
                                self._dev_skip_wave()
                            elif ui_action == "SETTINGS":
                                self.showing_ingame_settings = True
                                self._refresh_ingame_settings_hitboxes()
                                self._update_settings_volume_label()
                                self._clear_path_editing()
################################################################################################################
                            elif not self._path_edit_locked():
                                if self.build:
                                    self.set_path = True
                                else:
                                    self.rm_path = True
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1:
                            self.set_path = False
                            self.rm_path = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_F9:
                            self._dev_skip_wave()
                        if event.key == pygame.K_r:
                            if not self.round_active:
                                self.reset_grid()
                                self.edit_mode = True
                                self.round_active = False
                        if event.key == pygame.K_b:
                            self.build = not self.build
                        if event.key == pygame.K_v:
                            self.see_through_obstacles = True
                        if event.key == pygame.K_1 and self.is_mob_unlocked(0):
                            self.selected_mob_type = 0
                        if event.key == pygame.K_2 and self.is_mob_unlocked(1):
                            self.selected_mob_type = 1
                        if event.key == pygame.K_3 and self.is_mob_unlocked(2):
                            self.selected_mob_type = 2
                        if event.key == pygame.K_4 and self.is_mob_unlocked(3):
                            self.selected_mob_type = 3
                        if event.key == pygame.K_5 and self.is_mob_unlocked(4):
                            self.selected_mob_type = 4
                        if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                            if self._can_start_wave_combat():
                                self._start_wave_combat()
                            elif self.round_active and not self.edit_mode:
                                available_mobs = self.get_available_mobs_for_wave()
                                if (
                                    self.selected_mob_type in available_mobs
                                    and self.current_branches >= self.mob_costs[self.selected_mob_type]
                                    and not self._mob_spawn_on_cooldown(self.selected_mob_type)
                                ):
                                    cost = self.mob_costs[self.selected_mob_type]
                                    if self._spawn_mob_on_path(self.selected_mob_type):
                                        self.current_branches -= cost

                    elif event.type == self.SPAWN_MOB_EVENT:
                        # Automatic spawning disabled - player controls spawning
                        pass
                    elif event.type == pygame.KEYUP:
                        if event.key == pygame.K_v:
                            self.see_through_obstacles = False
            # Tree kill is handled in combat update via _on_tree_destroyed()

            # Check lose condition: failed to kill the tree within the wave limit
            if self.wave > MAX_WAVES and self.tree_health > 0:
                if self.game_active:
                    self.defeat()
            
            # Timed wave: must kill the tree before time runs out
            if (
                self.round_active
                and not self.edit_mode
                and self.wave_deadline_ms is not None
                and pygame.time.get_ticks() >= self.wave_deadline_ms
                and self.tree_health > 0
            ):
                self._round_failed()

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

