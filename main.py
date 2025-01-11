import pygame
from constants import *
from player import*

def main():
    print("Starting asteroids!")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    all_sprites = pygame.sprite.Group()
    clock = pygame.time.Clock()
    dt = 0
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    all_sprites.add(player)
    updatable.add(player)
    drawable.add(player)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        updatable.update(dt)
        screen.fill((0, 0, 0))
        drawable.draw(screen)
        pygame.display.flip()
        dt = clock.tick(60) / 1000


if __name__ == "__main__":    
    main()  