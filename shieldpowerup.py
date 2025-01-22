import pygame
import random
from circleshape import CircleShape
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

class Shield_Power_up(CircleShape, pygame.sprite.Sprite):
    def __init__(self, x, y):
        CircleShape.__init__(self, x, y, 15)
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.velocity.x = random.uniform(-1, 1)
        self.velocity.y = random.uniform(-1, 1)

    def draw(self, screen):
        pygame.draw.circle(screen, "cyan",
                           (int(self.position.x), int(self.position.y)),
                           self.radius, 2)
        
        pygame.draw.circle(screen, "blue",
                           (int(self.position.x), int(self.position.y)),
                           self.radius -5, 1)
        
    def update(self, dt):
        self.position += self.velocity * dt