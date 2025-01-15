import pygame
import random
from circleshape import CircleShape
from constants import *

class Asteroid(CircleShape, pygame.sprite.Sprite):
    def __init__(self, x, y, radius):
        # Initialize CircleShape with position and radius
        CircleShape.__init__(self, x, y, radius)

        # Initialize pygame sprite for sprite group functionalities
        pygame.sprite.Sprite.__init__(self, self.containers)

        self.size = self._determine_size()

    def _determine_size(self):
        if self.radius >= ASTEROID_MAX_RADIUS:
            return ASTEROID_SIZE_LARGE
        elif self.radius >= ASTEROID_MAX_RADIUS - ASTEROID_MIN_RADIUS:
            return ASTEROID_SIZE_MEDIUM
        else:
            return ASTEROID_SIZE_SMALL

    def draw(self, screen):
        # Use self.position.x and self.position.y instead of self.x and self.y
        pygame.draw.circle(
            screen, (255, 0, 0), (int(self.position.x), int(self.position.y)), self.radius, 2
        )

    def update(self, dt):
        self.position += self.velocity * dt  # Move asteroid by its velocity

    def split(self):
        
        self.kill()

        if self.radius <= ASTEROID_MIN_RADIUS:
            return
        
        r_angle = random.uniform(20, 50)

        new_velocity1 = self.velocity.rotate(r_angle)
        new_velocity2 = self.velocity.rotate(-r_angle)

        new_radius = self.radius - ASTEROID_MIN_RADIUS
        asteroid1 = Asteroid(self.position.x, self.position.y, new_radius)
        asteroid1.velocity = new_velocity1 *1.2
        asteroid2 = Asteroid(self.position.x, self.position.y, new_radius)
        asteroid2.velocity = new_velocity2 *1.2

class Shot(CircleShape, pygame.sprite.Sprite):
    def __init__(self, x, y, velocity):
        CircleShape.__init__(self, x, y, 5)
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.velocity = velocity

    def draw(self, screen):
        pygame.draw.circle(
            screen, "white", (int(self.position.x), int(self.position.y)), self.radius, 2
        )

    def update(self, dt):
        self.position += self.velocity * dt