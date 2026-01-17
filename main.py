import sys
import pygame

DEFAULT_BGCOLOR = (0,0,100)
DEFAULT_WIDTH   = 809
DEFAULT_HEIGHT  = 500 # if you're wondering, 809x500 is roughly the golden ratio

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

    def run_app(self) -> None:
        pygame.init()
        pygame.display.set_caption("Quitter")
        self.surface = pygame.display.set_mode((self.width,self.height))
        print(self.surface.get_width(), self.surface.get_height())
        self.clock = pygame.time.Clock()
        self.ground = pygame.image.load('grass_cube.png').convert_alpha()
        print("Hello")
        self.run_event_loop()
        

    def quit_app(self) -> None:
        pygame.quit()
        sys.exit()

    def draw_window(self) -> None:
        self.surface.fill(self.bgcolor)
        for i in range(10):
            for j in range(10):
                self.surface.blit(self.ground, (50 + 30*i,50 + 30*j))
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

