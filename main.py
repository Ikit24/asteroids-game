import pygame
import sys
import os
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, 
    SCORE_VALUES, INITIAL_SCORE, 
    INITIAL_MULTIPLIER, DEFAULT_POINTS
)
from player import *
from asteroid import *
from asteroidfield import AsteroidField


# Add later:

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

def increase_multiplier(current_multiplier):
    return min(current_multiplier + MULTIPLIER_INCREASE, MAX_MULTIPLIER)

def decrease_multiplier(current_multiplier):
    return max(INITIAL_MULTIPLIER, current_multiplier - MULTIPLIER_DECREASE)

def main():
    print("Starting asteroids!")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")
    score = INITIAL_SCORE
    high_score = INITIAL_SCORE
    multiplier = INITIAL_MULTIPLIER
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

    pygame.font.init()
    font = pygame.font.Font(None, 36)

    while True:       
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
        updatable.update(dt)
        hit_occured = False

        for asteroid in asteroids:
            if asteroid.collisions(player):
                print("Game over!")
                multiplier = INITIAL_MULTIPLIER
                sys.exit()

            for shot in shots:
                if shot.collisions(asteroid):
                    shot.kill()
                    hit_occured = True
                    multiplier = increase_multiplier(multiplier)
                    points = SCORE_VALUES.get(asteroid.size, DEFAULT_POINTS)
                    score += int(points * multiplier)
                    high_score = max(score, high_score)
                    asteroid.split()

            for shot in shots:
                if (shot.position.x < 0 or shot.position.x > SCREEN_WIDTH or 
                    shot.position.y < 0 or shot.position.y > SCREEN_HEIGHT):
                    shot.kill()
                    multiplier = decrease_multiplier(multiplier)
                         
        screen.blit(image, (0, 0))
        score_text = font.render(f'Score: {score}', True, (255, 255, 255))
        high_score_text = font.render(f'High Score: {high_score}', True, (255, 255, 255))
        multiplier_text = font.render(f'Multiplier: x{multiplier}', True, (255, 255, 255))

        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (10, 50))
        screen.blit(multiplier_text, (10, 90))

        for sprite in drawable:
            sprite.draw(screen)
        pygame.display.flip()
        dt = clock.tick(60) / 1000


if __name__ == "__main__":    
    main()  