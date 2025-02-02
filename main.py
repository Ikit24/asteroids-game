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
        self.torpedo_shots = pygame.sprite.Group()

        self.shield_powerups = pygame.sprite.Group()
        Shield_Power_up.containers = (self.shield_powerups, self.updatable, self.drawable)
        
        Shot.containers = (self.shots, self.updatable, self.drawable)
        SpreadShot.containers = (self.shots, self.updatable, self.drawable)
        TorpedoShot.containers = (self.torpedo_shots, self.updatable, self.drawable)
        Asteroid.containers = (self.asteroids, self.updatable, self.drawable)
        AsteroidField.containers = (self.updatable)
        asteroid_field = AsteroidField()

        self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, self.shots, self)
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

    def handle_shot_collision(self, shot, asteroid):
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
        new_player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, self.shots, self)
        new_player.activate_shield()
        new_player.shield_timer = pygame.time.get_ticks()
        self.all_sprites.add(new_player)
        self.updatable.add(new_player)
        self.drawable.add(new_player)
        return new_player
    
    def run(self):
        while True:
            self.handle_events()

            self.updatable.update(self.dt)
            self.player.update_shield()
            
            self.check_player_asteroid_collisions()
            self.check_projectile_collisions()
            self.handle_torpedo_collisions()
            
            self.update_powerups()
            
            self.draw()
            
            pygame.display.flip()
            self.dt = self.clock.tick(60) / 1000

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3 and self.player.can_spread_shot():
                    self.player.spread_shot()
                elif event.button == 1 and self.player.can_torpedo():  # Left-click
                    self.player.torpedo_shot()

    def check_player_asteroid_collisions(self):
        for asteroid in self.asteroids:
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

    def check_projectile_collisions(self):
        for shot in self.shots:
            if self.is_out_of_bounds(shot.position):
                shot.kill()
                self.multiplier = decrease_multiplier(self.multiplier)
            else:
                for asteroid in self.asteroids:
                    if isinstance(asteroid, Asteroid) and shot.collisions(asteroid):
                        self.handle_shot_collision(shot, asteroid)

        for spread_shot in self.player.spread_shots:
            if self.is_out_of_bounds(spread_shot.position):
                spread_shot.kill()
                self.multiplier = decrease_multiplier(self.multiplier)
            else:
                for asteroid in self.asteroids:
                    if isinstance(asteroid, Asteroid) and spread_shot.collisions(asteroid):
                        self.handle_shot_collision(spread_shot, asteroid)

    def handle_torpedo_collisions(self):
        hits = pygame.sprite.groupcollide(self.torpedo_shots, self.asteroids, True, True)
        for torpedo, hit_asteroids in hits.items():
            for asteroid in hit_asteroids:
                pos_x = asteroid.position.x
                pos_y = asteroid.position.y

                self.multiplier = increase_multiplier(self.multiplier)
                points = SCORE_VALUES.get(asteroid.size, DEFAULT_POINTS)
                self.score += int(points * self.multiplier)
                self.high_score = max(self.score, self.high_score)

                asteroid.split()

                explosion = Explosion(pos_x, pos_y)
                self.explosions.add(explosion)
                self.updatable.add(explosion)
                self.drawable.add(explosion)

    def update_powerups(self):
        if pygame.time.get_ticks() % 30000 < 50:
            new_powerup = spawn_shield_powerup()
            self.shield_powerups.add(new_powerup)
            self.drawable.add(new_powerup)
            self.updatable.add(new_powerup)

        for powerup in self.shield_powerups:
            if powerup.collisions(self.player):
                self.player.activate_shield()
                self.player.shield_timer = pygame.time.get_ticks()
                powerup.kill()

    def draw(self):
        self.screen.blit(self.image, (0, 0))
       
        score_text = self.font.render(f'Score: {self.score}', True, (255, 255, 255))
        high_score_text = self.font.render(f'High Score: {self.high_score}', True, (255, 255, 255))
        multiplier_text = self.font.render(f'Multiplier: x{self.multiplier}', True, (255, 255, 255))
        lives_text = self.font.render(f'Lives: {self.lives}', True, (255, 255, 255))
        
        # Position UI elements
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(high_score_text, (10, 50))
        self.screen.blit(multiplier_text, (10, 90))
        self.screen.blit(lives_text, (10, 130))
        
        for sprite in self.drawable:
            sprite.draw(self.screen)

    def is_out_of_bounds(self, position):
        return (position.x < 0 or position.x > SCREEN_WIDTH or 
                position.y < 0 or position.y > SCREEN_HEIGHT)

def main():
    game = Game()
    game.run()

if __name__ == "__main__":    
    main()