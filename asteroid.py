import pygame
import random
import time
from circleshape import CircleShape
from constants import *
from utils import wrap_position
from explosion import Explosion

class Asteroid(CircleShape, pygame.sprite.Sprite):
    images = {
        ASTEROID_SIZE_LARGE: None,
        ASTEROID_SIZE_MEDIUM: None,
        ASTEROID_SIZE_SMALL: None
    }

    @classmethod
    def load_images(cls):
        if cls.images[ASTEROID_SIZE_LARGE] is None:
            cls.images[ASTEROID_SIZE_LARGE] = pygame.image.load("images/ASTEROID_LARGE.png").convert_alpha()
            cls.images[ASTEROID_SIZE_MEDIUM] = pygame.image.load("images/ASTEROID_MEDIUM.png").convert_alpha()
            cls.images[ASTEROID_SIZE_SMALL] = pygame.image.load("images/ASTEROID_SMALL.png").convert_alpha()
  
    def __init__(self, x, y, radius):
        CircleShape.__init__(self, x, y, radius)
        pygame.sprite.Sprite.__init__(self, self.containers)

        self.load_images()

        self.size = self._determine_size()
        self.image = pygame.transform.scale(
            self.images[self.size],
            (self.radius * 2, self.radius * 2)
        )
        self.rect = self.image.get_rect()

        self.angle = random.randrange(360)
        self.original_image =  self.image

    def _determine_size(self):
        if self.radius >= ASTEROID_MAX_RADIUS:
            return ASTEROID_SIZE_LARGE
        elif self.radius >= ASTEROID_MAX_RADIUS - ASTEROID_MIN_RADIUS:
            return ASTEROID_SIZE_MEDIUM
        else:
            return ASTEROID_SIZE_SMALL

    def draw(self, screen):
        self.rect.center = (int(self.position.x), int(self.position.y))
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        screen.blit(self.image, self.rect)

    def update(self, dt):
        super().update(dt)
        self.angle = (self.angle + 1) % 360
        self.position += self.velocity * dt
        self.position.x, self.position.y = wrap_position(self.position.x, self.position.y)

    def split(self): 
        explosion = Explosion(self.position.x, self.position.y)
        if hasattr(self, 'containers') and self.containers:
            for container in self.containers:
                if hasattr(container, 'add'):
                    container.add(explosion)   

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

        return [asteroid1, asteroid2]

class Shot(CircleShape, pygame.sprite.Sprite):
    def __init__(self, x, y, velocity):
        CircleShape.__init__(self, x, y, 5)
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.velocity = velocity
        self.lifetime = 2.0
        self.birth_time = time.time()

    def draw(self, screen):
        pygame.draw.circle(
            screen, "white", (int(self.position.x), int(self.position.y)), self.radius, 2
        )

    def update(self, dt):
        self.position += self.velocity * dt
        if time.time() - self.birth_time > self.lifetime:
            self.kill()

class SpreadShot(pygame.sprite.Sprite):
    def __init__(self, x, y, velocity, angle, lifetime=1000):
        super().__init__()
        # Create the shot's image and rect
        self.image = pygame.Surface((5, 5))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.velocity = velocity
        self.position = pygame.math.Vector2(x, y)

        self.lifetime = lifetime
        self.start_time = pygame.time.get_ticks()

    def update(self, dt):
        self.position += self.velocity * dt
        self.rect.center = self.position

        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.lifetime:
            self.kill()

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def collisions(self, other):
        return self.rect.colliderect(other.rect)

class HomingShot(Shot):
    def __init__(self, x, y, velocity, target=None):
        super().__init__(x, y, velocity)
        self.target = target
        self.turn_rate = 0.1