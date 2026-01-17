import sys
import pygame
import numpy as np

DEFAULT_BGCOLOR = (137, 207, 240)
DEFAULT_WIDTH   = 1280
DEFAULT_HEIGHT  = 720 # if you're wondering, 809x500 is roughly the golden ratio

# type synonym for convenience
rgb = tuple[int,int,int]

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

    def i_hat(self, x, w, h):
        return (x * w / 2, (x * h/2)/2)
    
    def j_hat(self,y, w, h):
        return ((-y * w) / 2, (y * h/2)/2)
    

    def run_app(self) -> None:
        pygame.init()
        pygame.display.set_caption("Quitter")
        self.surface = pygame.display.set_mode((self.width,self.height))
        self.clock = pygame.time.Clock()
        self.sprite = pygame.image.load('grass_cube.png').convert_alpha()
        scale_factor = 3
        self.ground = pygame.transform.scale(self.sprite,(int(self.sprite.get_width() * scale_factor), int(self.sprite.get_height() * scale_factor)))
        self.spriteSize = (self.ground.get_width(), self.ground.get_height())
        print(self.spriteSize)
        self.run_event_loop()

    def quit_app(self) -> None:
        pygame.quit()
        sys.exit()

    def draw_window(self) -> None:
        self.surface.fill(self.bgcolor)
        grid_size = 12
        for i in range(grid_size):
            for j in range(grid_size):
                x = self.i_hat(j, self.spriteSize[0], self.spriteSize[1])
                y = self.j_hat(i, self.spriteSize[0], self.spriteSize[1])
                
                self.surface.blit(self.ground, (DEFAULT_WIDTH/2 + x[0] + y[0] - self.spriteSize[0]/2, self.spriteSize[1]/2 + x[1] + y[1]))
        pygame.display.update()
        

    def run_event_loop(self) -> None:
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.quit_app()
                elif event.type == pygame.MOUSEMOTION:
                    pass
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pass
                elif event.type == pygame.MOUSEBUTTONUP:
                    pass
                elif event.type == pygame.KEYDOWN:
                    pass
                elif event.type == pygame.KEYUP:
                    pass
            self.draw_window()
            self.clock.tick(24) # throttle redraws at 24fps (frames per second)

# ========

if __name__ == "__main__":
    q = Quitter()
    q.run_app()

