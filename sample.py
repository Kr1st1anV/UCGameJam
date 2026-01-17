import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen setup
screen = pygame.display.set_mode((500, 400))
pygame.display.set_caption("Modify Sprite get_rect Example")

# Load an image (replace with your own)
sprite = pygame.image.load('grass_cube.png').convert_alpha()
sprite2 = pygame.Surface((50, 50))
sprite2.fill((255, 0, 0))  # Red square for demo

# Create a rect from the image
sprite_rect = sprite.get_rect()

# Modify rect position
sprite_rect.topleft = (100, 150)  # Move to x=100, y=150

# You can also modify other attributes:
# sprite_rect.center = (250, 200)
# sprite_rect.x += 10
# sprite_rect.width = 60  # Changes collision box size

# Main loop
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Clear screen
    screen.fill((30, 30, 30))

    # Draw sprite at modified rect position
    screen.blit(sprite, sprite_rect)

    pygame.display.flip()
    clock.tick(60)
