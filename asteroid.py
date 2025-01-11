import pygame
from circleshape import CircleShape


class Asteroid(CircleShape, pygame.sprite.Sprite):
    def __init__(self, x, y, radius):
        # Initialize CircleShape with position and radius
        CircleShape.__init__(self, x, y, radius)

        # Initialize pygame sprite for sprite group functionalities
        pygame.sprite.Sprite.__init__(self, self.containers)

    def draw(self, screen):
        # Use self.position.x and self.position.y instead of self.x and self.y
        pygame.draw.circle(
            screen, (255, 0, 0), (int(self.position.x), int(self.position.y)), self.radius, 2
        )

    def update(self, dt):
        self.position += self.velocity * dt  # Move asteroid by its velocity