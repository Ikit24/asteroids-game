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
        pygame.draw.polygon(self.image, "white", local_points, 2    )
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
    if hasattr(other, 'radius'):  # For circular objects like asteroids
        # Get triangle vertices in world coordinates
        vertices = self.get_world_vertices()
        
        # Check if any vertex of the triangle is within the circle
        circle_center = pygame.math.Vector2(other.position.x, other.position.y)
        
        # Check if any vertex is inside the circle
        for vertex in vertices:
            vertex_vec = pygame.math.Vector2(vertex)
            if vertex_vec.distance_to(circle_center) <= other.radius:
                return True
        
        # Check if circle center is inside triangle
        if self.point_in_triangle((circle_center.x, circle_center.y), vertices):
            return True
            
        # Check if circle intersects with any of the triangle's edges
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