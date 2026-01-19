class Mobs:
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
                        ['snail idle_0001.png', 'snail idle_0002.png', 'snail idle_0003.png', 'snail idle_0004.png']]
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
            # Draw a small red square as the 'runner'
        current_sprite = self.mobframes[self.current_frame]
        sprite_rect = current_sprite.get_rect()
        sprite_rect.center = (self.pos.x ,self.pos.y)
        surface.blit(current_sprite, sprite_rect)