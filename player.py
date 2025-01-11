import pygame
from circleshape import CircleShape
from constants import *

class Player(CircleShape, pygame.sprite.Sprite):
    def __init__(self, x, y):
        CircleShape.__init__(self, x, y, PLAYER_RADIUS)
        pygame.sprite.Sprite.__init__(self)
        self.rotation = 0
        size = int(PLAYER_RADIUS * 3)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.draw()

    def draw(self):
        self.image.fill((0, 0, 0, 0))
        local_points = self.get_local_triangle()
        pygame.draw.polygon(self.image, "white", local_points, 2)
        self.rect.center = self.position

    def get_local_triangle(self):
        center = pygame.Vector2(self.image.get_width() / 2, self.image.get_height() / 2)
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        
        a = center + forward * self.radius
        b = center - forward * self.radius - right
        c = center - forward * self.radius + right
        return [a, b, c]
    
    def rotate(self, dt):
        self.rotation += PLAYER_TURN_SPEED * dt

    def update(self, dt):
        keys = pygame.key.get_pressed()
        needs_redraw = False

        if keys[pygame.K_w]:
            self.move(dt)
            needs_redraw = True

        if keys[pygame.K_a]:
            self.rotate(dt * -1)
            needs_redraw = True

        if keys[pygame.K_s]:
            self.move(dt *-1)
            needs_redraw = True

        if keys[pygame.K_d]:
            self.rotate(dt)
            needs_redraw = True

        if needs_redraw:
            self.draw()

    def move(self, dt):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        self.position += forward * PLAYER_SPEED * dt
        self.rect.center = self.position