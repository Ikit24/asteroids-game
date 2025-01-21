import pygame
from circleshape import CircleShape
from constants import *
from asteroid import Shot
from utils import wrap_position

class Player(CircleShape, pygame.sprite.Sprite):
    images = {SPACESHIP: None}

    @classmethod
    def load_images(cls):
        if cls.images[SPACESHIP] is None:
             original = cls.images[SPACESHIP] = pygame.image.load("images/SPACESHIP.png").convert_alpha()
             cls.images[SPACESHIP] = pygame.transform.rotate(original, PLAYER_INITIAL_ROTATION)
        
    def __init__(self, x, y):
        CircleShape.__init__(self, x, y, PLAYER_RADIUS)
        pygame.sprite.Sprite.__init__(self)
        self.rotation = 0
        size = int(PLAYER_RADIUS * 3)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = self.position

        self.load_images()
        
        scaled_size = (PLAYER_RADIUS * 2, PLAYER_RADIUS * 2)
        self.original_image = pygame.transform.scale(self.images[SPACESHIP], scaled_size)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = self.position
        
        self.timer = 0

    def draw(self, screen):      
        self.rect.center = (int(self.position.x), int(self.position.y))
        self.image = pygame.transform.rotate(self.original_image, -self.rotation)
        self.rect = self.image.get_rect(center=self.rect.center)
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
        if keys[pygame.K_w]:
            self.move(dt)

        if keys[pygame.K_a]:
            self.rotate(dt * -1)

        if keys[pygame.K_s]:
            self.move(dt * -1)

        if keys[pygame.K_d]:
            self.rotate(dt)

        if keys[pygame.K_SPACE]:
            self.shoot()
        
        self.position.x, self.position.y = wrap_position(self.position.x, self.position.y)

    def move(self, dt):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        self.position += forward * PLAYER_SPEED * dt
        self.rect.center = self.position

    def shoot(self):
        if self.timer <= 0:
            forward = pygame.Vector2(0, 1).rotate(self.rotation)
            forward *= PLAYER_SHOOT_SPEED        
            Shot(self.position.x, self.position.y, forward)
            self.timer = PLAYER_SHOOT_COOLDOWN

    def get_world_vertices(self):
        # Convert local triangle points to world coordinates
        local_points = self.get_local_triangle()
        world_points = []
        for point in local_points:
            world_points.append((
                point.x - self.image.get_width()/2 + self.position.x,
                point.y - self.image.get_height()/2 + self.position.y
            ))
        return world_points
    
    def point_in_triangle(self, point, triangle):
        # Helper function to determine if a point is inside a triangle
        def sign(p1, p2, p3):
            return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

        d1 = sign(point, triangle[0], triangle[1])
        d2 = sign(point, triangle[1], triangle[2])
        d3 = sign(point, triangle[2], triangle[0])

        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

        return not (has_neg and has_pos)

    def collisions(self, other):
        if hasattr(other, 'radius'):
            vertices = self.get_world_vertices()
            
            circle_center = pygame.math.Vector2(other.position.x, other.position.y)
            
            for vertex in vertices:
                vertex_vec = pygame.math.Vector2(vertex)
                if vertex_vec.distance_to(circle_center) <= other.radius:
                    return True
                        
            if self.point_in_triangle((circle_center.x, circle_center.y), vertices):
                return True
            
            for i in range(3):
                p1 = pygame.math.Vector2(vertices[i])
                p2 = pygame.math.Vector2(vertices[(i + 1) % 3])
                
                # Find nearest point on line segment to circle center
                line_vec = p2 - p1
                line_length = line_vec.length()
                if line_length == 0:
                    continue
                    
                t = max(0, min(1, (circle_center - p1).dot(line_vec) / line_vec.dot(line_vec)))
                nearest = p1 + t * line_vec
                
                if nearest.distance_to(circle_center) <= other.radius:
                    return True
                    
        return False