import sys
import pygame
import numpy as np

DEFAULT_BGCOLOR = (137, 207, 240)
DEFAULT_WIDTH   = 1280
DEFAULT_HEIGHT  = 720
GRID_SIZE = 12

rgb = tuple[int,int,int]

world_grid = []
for i in range(GRID_SIZE):
    world_grid.append([])
    for j in range(GRID_SIZE):
        if i == 0 and j == 8 or i == GRID_SIZE - 1 and j == 3:
            world_grid[i].append(-1)
        else:
            world_grid[i].append(0)

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

    def x_transform(self, x, w, h):
        return (x * w / 2, (x * h/2)/2)
    
    def y_transform(self,y, w, h):
        return ((-y * w) / 2, (y * h/2)/2)
    
    def initiate_blocks(self):
        self.ground_sprite = pygame.image.load('grass_cube.png').convert_alpha()
        self.path_sprite = pygame.image.load('path.png').convert_alpha()
        self.water_sprite = pygame.image.load('Image.png').convert_alpha()
        scale_factor = 3
        self.ground = pygame.transform.scale(self.ground_sprite,(int(self.ground_sprite.get_width() * scale_factor), int(self.ground_sprite.get_height() * scale_factor)))
        self.path = pygame.transform.scale(self.path_sprite,(int(self.path_sprite.get_width() * scale_factor), int(self.path_sprite.get_height() * scale_factor)))
        self.water = pygame.transform.scale(self.water_sprite,(int(self.water_sprite.get_width() * scale_factor), int(self.water_sprite.get_height() * scale_factor)))
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

    def map_grid(self): 
        
        w, h = self.spriteSize

        half_w = w / 2
        half_h = h / 4

        pivot_x = DEFAULT_WIDTH / 2
        pivot_y = 100

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
                if i == grid_i and j == grid_j:
                    draw_y -= 10
                    if self.set_path and world_grid[i][j] != -1:
                        world_grid[i][j] = 1
                    elif self.rm_path and world_grid[i][j] != -1:
                        world_grid[i][j] = 0
                
                if world_grid[i][j] == 0:
                    self.surface.blit(self.ground, (draw_x, draw_y))
                elif world_grid[i][j] == 1:
                    self.surface.blit(self.path, (draw_x, draw_y))
                elif world_grid[i][j] == -1:
                    self.surface.blit(self.water, (draw_x, draw_y))

    def draw_window(self) -> None:
        self.surface.fill(self.bgcolor)
        self.map_grid()        
        pygame.display.update()

    def is_grid_valid(self, world_grid, grid_size):
        for i in range(grid_size):
            for j in range(grid_size):
                val = world_grid[i][j]
                
                if val == 0:
                    continue
                
                ones_around = 0
                neg_ones_around = 0
                
                for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < grid_size and 0 <= nj < grid_size:
                        neighbor_val = world_grid[ni][nj]
                        if neighbor_val == 1:
                            ones_around += 1
                        elif neighbor_val == -1:
                            neg_ones_around += 1
                
                if val == -1:
                    if ones_around != 1:
                        return False
                
                elif val == 1:
                    if ones_around < 1 or ones_around > 2:
                        return False
                    
                    if neg_ones_around > 0:
                        if ones_around > 1:
                            return False
                            
        return True
            

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
                    if event.key == pygame.K_y:
                        print(self.is_grid_valid(world_grid, GRID_SIZE))
                elif event.type == pygame.KEYUP:
                    pass
            self.draw_window()
            self.clock.tick(60) # throttle redraws at 60fps (frames per second)

# ========

if __name__ == "__main__":
    q = Quitter()
    q.run_app()

