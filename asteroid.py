import pygame
import random
from circleshape import CircleShape
from constants import *
from utils import wrap_position

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

    def draw(self, screen):
        pygame.draw.circle(
            screen, "white", (int(self.position.x), int(self.position.y)), self.radius, 2
        )

    def update(self, dt):
        self.position += self.velocity * dt