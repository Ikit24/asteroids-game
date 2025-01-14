import pygame
import sys
import os
from constants import *
from player import *
from asteroid import *
from asteroidfield import AsteroidField

# Add later:

    # Add a scoring system
    # Implement multiple lives and respawning
    # Add an explosion effect for the asteroids
    # Add acceleration to the player movement
    # Make the objects wrap around the screen instead of disappearing
    # Create different weapon types
    # Make the asteroids lumpy instead of perfectly round
    # Make the ship have a triangular hit box instead of a circular one
    # Add a shield power-up
    # Add a speed power-up
    # Add bombs that can be dropped

def main():
    print("Starting asteroids!")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    all_sprites = pygame.sprite.Group()
    clock = pygame.time.Clock()
    dt = 0
    try:
        image = pygame.image.load(os.path.join('images', 'ASTEROID.webp'))
        image = pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error as e:
        print(f"Couldn't load background image: {e}")
        image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        image.fill((0, 0, 0))  # Black color

    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()

    Shot.containers = (shots, updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = (updatable,)
    asteroid_field = AsteroidField()

    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    
    updatable.add(asteroid_field)
    all_sprites.add(player)
    updatable.add(player)
    drawable.add(player)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        updatable.update(dt)
        for asteroid in asteroids:
            if asteroid.collisions(player):
                print("Game over!")
                sys.exit()

            for shot in shots:
                if shot.collisions(asteroid):
                    shot.kill()
                    asteroid.split()
                         
        screen.blit(image, (0, 0))
        for sprite in drawable:
            sprite.draw(screen)
        pygame.display.flip()
        dt = clock.tick(60) / 1000


if __name__ == "__main__":    
    main()  