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

        self.image = pygame.image.load("images/shield.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = (int(self.position.x), int(self.position.y))

    def draw(self, screen):
        self.rect.center = (int(self.position.x), int(self.position.y))
        screen.blit(self.image, self.rect)
        
    def update(self, dt):
        self.position += self.velocity * dt
        self.rect.center = (int(self.position.x), int(self.position.y))