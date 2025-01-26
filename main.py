import pygame
import sys
import os
from explosion import Explosion
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, 
    SCORE_VALUES, INITIAL_SCORE, 
    INITIAL_MULTIPLIER, DEFAULT_POINTS
)
from player import *
from asteroid import *
from asteroidfield import AsteroidField
from shieldpowerup import Shield_Power_up

# Add later:
    # Add bombs that can be dropped

def spawn_shield_powerup():
    x = random.randrange(SCREEN_WIDTH)
    y = random.randrange(SCREEN_HEIGHT)
    return Shield_Power_up(x, y)

def increase_multiplier(current_multiplier):
    return min(current_multiplier + MULTIPLIER_INCREASE, MAX_MULTIPLIER)

def decrease_multiplier(current_multiplier):
    return max(INITIAL_MULTIPLIER, current_multiplier - MULTIPLIER_DECREASE)

class Game:
    def __init__(self):
        print("Starting asteroids!")
        print(f"Screen width: {SCREEN_WIDTH}")
        print(f"Screen height: {SCREEN_HEIGHT}")
        self.lives = 3
        self.score = INITIAL_SCORE
        self.high_score = INITIAL_SCORE
        self.multiplier = INITIAL_MULTIPLIER
        pygame.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.all_sprites = pygame.sprite.Group()
        self.clock = pygame.time.Clock()
        self.explosions = pygame.sprite.Group()
        self.shield_powerups = pygame.sprite.Group()
        self.dt = 0

        try:
            self.image = pygame.image.load(os.path.join('images', 'ASTEROID.png'))
            self.image = pygame.transform.scale(self.image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except pygame.error as e:
            print(f"Couldn't load background image: {e}")
            self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.image.fill((0, 0, 0))

        self.updatable = pygame.sprite.Group()
        self.drawable = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.shots = pygame.sprite.Group()

        self.shield_powerups = pygame.sprite.Group()
        Shield_Power_up.containers = (self.shield_powerups, self.updatable, self.drawable)
        
        Shot.containers = (self.shots, self.updatable, self.drawable)
        SpreadShot.containers = (self.shots, self.updatable, self.drawable)
        Asteroid.containers = (self.asteroids, self.updatable, self.drawable)
        AsteroidField.containers = (self.updatable)
        asteroid_field = AsteroidField()

        self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, self.shots)
        self.player.activate_shield()
        self.player.shield_timer = pygame.time.get_ticks()

        
        self.updatable.add(asteroid_field)
        self.all_sprites.add(self.player)
        self.updatable.add(self.player)
        self.drawable.add(self.player)
        self.shield_powerups.update(self.dt)

        pygame.font.init()
        self.font = pygame.font.Font(None, 36)

    def handle_shot_collision(self, shot, asteroid):
            shot.kill()
            explosion = Explosion(asteroid.position.x, asteroid.position.y)
            self.explosions.add(explosion)
            self.updatable.add(explosion)
            self.drawable.add(explosion)

            self.multiplier = increase_multiplier(self.multiplier)
            points = SCORE_VALUES.get(asteroid.size, DEFAULT_POINTS)
            self.score += int(points * self.multiplier)
            self.high_score = max(self.score, self.high_score)
            asteroid.split()
            return True           

    def respawn_player(self):
        new_player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, self.shots)
        new_player.activate_shield()
        new_player.shield_timer = pygame.time.get_ticks()
        self.all_sprites.add(new_player)
        self.updatable.add(new_player)
        self.drawable.add(new_player)
        return new_player
    
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3:  # Right click
                        print("Right click detected")
                        if self.player.can_spread_shot():
                            print("Spreading!")
                            self.player.spread_shot()
                        else:
                            print("Spread shot not ready")
                
            self.updatable.update(self.dt)
            self.player.update_shield()
            hit_occured = False

            for asteroid in self.asteroids:
                # Check player collision with asteroid
                if isinstance(asteroid, Asteroid) and asteroid.collisions(self.player):
                    if self.player.shield_active:
                        self.player.shield_active = True
                    else:
                        self.lives -= 1
                        if self.lives > 0:
                            self.player.kill()
                            self.player = self.respawn_player()
                            self.multiplier = INITIAL_MULTIPLIER
                        else:
                            print("Gameover!")
                            sys.exit()
                    break

                # Check regular shots
                for shot in self.shots:
                    if (shot.position.x < 0 or shot.position.x > SCREEN_WIDTH or 
                        shot.position.y < 0 or shot.position.y > SCREEN_HEIGHT):
                        shot.kill()
                        self.multiplier = decrease_multiplier(self.multiplier)
                    elif isinstance(asteroid, Asteroid) and shot.collisions(asteroid):
                        hit_occurred = self.handle_shot_collision(shot, asteroid)  # Note the self.

                # Check spread shots
                for spread_shot in self.player.spread_shots:
                    if (spread_shot.position.x < 0 or spread_shot.position.x > SCREEN_WIDTH or 
                        spread_shot.position.y < 0 or spread_shot.position.y > SCREEN_HEIGHT):
                        spread_shot.kill()
                        self.multiplier = decrease_multiplier(self.multiplier)
                    elif isinstance(asteroid, Asteroid) and spread_shot.collisions(asteroid):
                        hit_occurred = self.handle_shot_collision(spread_shot, asteroid)

            if pygame.time.get_ticks() % 30000 < 50:
                spawn_shield_powerup()
                new_powerup = spawn_shield_powerup()
                self.shield_powerups.add(new_powerup)
                self.drawable.add(new_powerup)
                self.updatable.add(new_powerup)

            for powerup in self.shield_powerups:
                if powerup.collisions(self.player):
                    self.player.activate_shield()
                    self.player.shield_timer = pygame.time.get_ticks()
                    powerup.kill()

            self.screen.blit(self.image, (0, 0))
            score_text = self.font.render(f'Score: {self.score}', True, (255, 255, 255))
            high_score_text = self.font.render(f'High Score: {self.high_score}', True, (255, 255, 255))
            multiplier_text = self.font.render(f'Multiplier: x{self.multiplier}', True, (255, 255, 255))
            lives_text = self.font.render(f'Lives: {self.lives}', True, (255, 255, 255))
            self.screen.blit(lives_text, (10, 130))

            self.screen.blit(score_text, (10, 10))
            self.screen.blit(high_score_text, (10, 50))
            self.screen.blit(multiplier_text, (10, 90))

            for sprite in self.drawable:
                sprite.draw(self.screen)
            pygame.display.flip()
            self.dt = self.clock.tick(60) / 1000

def main():
    game = Game()
    game.run()

if __name__ == "__main__":    
    main()  