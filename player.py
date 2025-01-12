import pygame
from circleshape import CircleShape
from constants import *
from asteroid import Shot

class Player(CircleShape, pygame.sprite.Sprite):
    def __init__(self, x, y):
        CircleShape.__init__(self, x, y, PLAYER_RADIUS)
        pygame.sprite.Sprite.__init__(self)
        self.rotation = 0
        size = int(PLAYER_RADIUS * 3)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = self.position
        self.timer = 0

    def draw(self, screen):
        self.image.fill((0, 0, 0, 0))
        local_points = self.get_local_triangle()
        pygame.draw.polygon(self.image, "white", local_points, 2)
        self.rect.center = self.position
        screen.blit(self.image, self.rect)

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
        if self.timer > 0:
            self.timer -= dt
            
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:  # Move forward
            self.move(dt)

        if keys[pygame.K_a]:  # Rotate counterclockwise
            self.rotate(dt * -1)

        if keys[pygame.K_s]:  # Move backward
            self.move(dt * -1)

        if keys[pygame.K_d]:  # Rotate clockwise
            self.rotate(dt)

        if keys[pygame.K_SPACE]:
            self.shoot()

    def move(self, dt):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        self.position += forward * PLAYER_SPEED * dt
        self.rect.center = self.position

    def shoot(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        forward *= PLAYER_SHOOT_SPEED        
        if self.timer <= 0:            
            shot = Shot(self.position.x, self.position.y, forward)
            self.timer = PLAYER_SHOOT_COOLDOWN