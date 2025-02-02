import pygame
import math
import time
from circleshape import CircleShape
from constants import *
from asteroid import *
from utils import wrap_position

class Player(CircleShape, pygame.sprite.Sprite):
    images = {SPACESHIP: None}

    @classmethod
    def load_images(cls):
        if cls.images[SPACESHIP] is None:
             original = cls.images[SPACESHIP] = pygame.image.load("images/SPACESHIP.png").convert_alpha()
             cls.images[SPACESHIP] = pygame.transform.rotate(original, PLAYER_INITIAL_ROTATION)
        
    def __init__(self, x, y, shots, game):
        CircleShape.__init__(self, x, y, PLAYER_RADIUS)
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        # Shots setup
        self.shots = shots
        self.spread_shots = pygame.sprite.Group()
        self.torpedo_shots = pygame.sprite.Group()
        
        # Shield setup
        self.shield_active = False
        self.shield_timer = 0
        self.SHIELD_DURATION = 5000
        self.shield_state = "idle"
        self.shield_alpha = 255
        self.shield_image = pygame.image.load("images/shield.png").convert_alpha()
        self.shield_image = pygame.transform.scale(self.shield_image, 
                                        (PLAYER_RADIUS * 3, PLAYER_RADIUS * 3))
        
        # Boost setup
        self.should_draw = False
        self.boost_active = False
        self.boost_timer = 0
        self.boost_cooldown = 0
        self.boost_icon = pygame.image.load("images/boost.png").convert_alpha()
        self.boost_icon = pygame.transform.scale(self.boost_icon, (40, 40))
        self.boost_icon_rect = self.boost_icon.get_rect()
        self.boost_icon_rect.topleft = (1200, 40)
        
        # Weapon setup
        self.current_weapon = "normal"
        self.weapon_cooldown = 0
        self.last_shot_time = 0
        self.shot_cooldown = 0.25
        self.last_spread_shot_time = pygame.time.get_ticks()  # Keep this one
        self.spread_shot_cooldown = 2.0
        self.last_torpedo_shot_time = pygame.time.get_ticks()
        self.torpedo_shot_cooldown = 5.0

        # Spread_shot setup
        self.should_draw = False
        self.spread_shot_icon = pygame.image.load("images/spread_shot.png").convert_alpha()
        self.spread_shot_icon = pygame.transform.scale(self.spread_shot_icon, (40, 40))
        self.spread_shot_icon_rect = self.spread_shot_icon.get_rect()
        self.spread_shot_icon_rect.topleft = (1150, 40)

        #Torpedo setup
        self.should_draw =  False
        self.torpedo_icon = pygame.image.load("images/torpedo.png").convert_alpha()
        self.torpedo_icon = pygame.transform.scale(self.torpedo_icon, (40, 40))
        self.torpedo_icon_poly = self.torpedo_icon.get_rect()
        self.torpedo_icon_poly.topleft = (1100, 40)
        
        # Image and rotation setup
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
        # Draw player
        self.rect.center = (int(self.position.x), int(self.position.y))
        self.image = pygame.transform.rotate(self.original_image, -self.rotation)
        self.spread_shots.draw(screen)
        self.rect = self.image.get_rect(center=self.rect.center)
        screen.blit(self.image, self.rect)

        # Draw shield if active
        if self.shield_active:
            shield_pos = (self.position[0] - self.shield_image.get_width() // 2,
                          self.position[1] - self.shield_image.get_height() // 2)
            screen.blit(self.shield_image, shield_pos)
            shield_surface = self.shield_image.copy()
            shield_surface.set_alpha(self.shield_alpha)
            screen.blit(shield_surface, shield_pos)
        
        # Draw boost icon and its cooldown
        screen.blit(self.boost_icon, self.boost_icon_rect)
        if self.boost_active:
            progress = self.boost_timer / 10
            height = int(self.boost_icon_rect.height * progress)
            cooldown_rect = pygame.Rect(
                self.boost_icon_rect.x,
                self.boost_icon_rect.bottom - height,
                self.boost_icon_rect.width,
                height
            )
            pygame.draw.rect(screen, (128, 128, 128), cooldown_rect)
        elif self.boost_cooldown > 0:
            progress = self.boost_cooldown / 10
            height = int(self.boost_icon_rect.height * progress)
            cooldown_rect = pygame.Rect(
                self.boost_icon_rect.x,
                self.boost_icon_rect.bottom - height,
                self.boost_icon_rect.width,
                height
            )
            pygame.draw.rect(screen, (64, 64, 64), cooldown_rect)
        
        screen.blit(self.spread_shot_icon, self.spread_shot_icon_rect)

        cooldown_progress = self.get_spread_shot_cooldown_progress()
        if cooldown_progress < 1:
            cooldown_height = int(self.spread_shot_icon_rect.height * (1 - cooldown_progress))
            cooldown_rect = pygame.Rect(
                self.spread_shot_icon_rect.x,
                self.spread_shot_icon_rect.bottom - cooldown_height,
                self.spread_shot_icon_rect.width,
                cooldown_height
            )
            pygame.draw.rect(screen, (128, 0, 0), cooldown_rect)

        screen.blit(self.torpedo_icon, self.torpedo_icon_poly)

        torpedo_progress = self.get_torpedo_cooldown_progress()
        if torpedo_progress < 1:
            cd_height = int(self.torpedo_icon_poly.height * (1 - torpedo_progress))
            cd_rect = pygame.Rect(
                self.torpedo_icon_poly.x,
                self.torpedo_icon_poly.bottom - cd_height,
                self.torpedo_icon_poly.width,
                cd_height
            )
            pygame.draw.rect(screen, (128, 0, 0), cd_rect)

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
        self.torpedo_shots.update(dt)
        self.position.x, self.position.y = wrap_position(self.position.x, self.position.y)
        self.spread_shots.update(dt)

        self.update_shield()
        
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

        if keys[pygame.K_LSHIFT]:
            self.boost()
        
        if self.boost_active:
            self.boost_timer += dt
            if self.boost_timer >= 10:
                self.boost_active = False
                self.boost_timer = 0
                self.boost_cooldown = 10
        elif self.boost_cooldown > 0:
            self.boost_cooldown -= dt

        self.position.x, self.position.y = wrap_position(self.position.x, self.position.y)

    def activate_shield(self):
        self.shield_active = True        
        self.shield_timer = pygame.time.get_ticks()
        self.shield_state = "active"
        self.shield_alpha = 255
    
    def break_shield(self):
        self.shield_state = "popping"

    def update_shield(self):
        current_time = pygame.time.get_ticks()
        
        if self.shield_state == "active":
            if current_time - self.shield_timer >= self.SHIELD_DURATION:
                self.shield_state = "popping"
        
        elif self.shield_state == "popping":
            self.shield_alpha -= 5
            if self.shield_alpha <= 0:
                self.shield_state = "idle"
                self.shield_active = False
                self.shield_alpha = 255 

    def move(self, dt):                
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        speed = PLAYER_SPEED *2 if self.boost_active else PLAYER_SPEED
        self.position += forward * speed * dt
        self.rect.center = self.position

    def shoot(self):
        if self.timer <= 0:
            forward = pygame.Vector2(0, 1).rotate(self.rotation)
            forward *= PLAYER_SHOOT_SPEED        
            Shot(self.position.x, self.position.y, forward)
            self.timer = PLAYER_SHOOT_COOLDOWN

    def can_shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.shot_cooldown:
            self.last_shot_time = current_time
            return True
        return False
    
    def can_spread_shot(self):
        current_time = pygame.time.get_ticks()
        time_since_last = (current_time - self.last_spread_shot_time) / 1000
        return time_since_last >= self.spread_shot_cooldown

    def spread_shot(self):
        if self.can_spread_shot():
            num_pellets = 5
            total_spread = 45
            angle_between = total_spread / (num_pellets - 1)
            start_angle = -total_spread / 2
            base_speed = 300

            firing_angle = self.rotation + 90

            for i in range(num_pellets):
                current_angle = firing_angle + start_angle + (i * angle_between)
                angle_rad = math.radians(current_angle)
                new_velocity = pygame.math.Vector2(
                    base_speed * math.cos(angle_rad),
                    base_speed * math.sin(angle_rad)
                )
                new_shot = SpreadShot(self.position.x, self.position.y, new_velocity, current_angle)
                self.spread_shots.add(new_shot)

            self.last_spread_shot_time = pygame.time.get_ticks()

    def get_spread_shot_cooldown_progress(self):
        current_time = pygame.time.get_ticks()
        time_since_last = (current_time - self.last_spread_shot_time) / 1000
        return min(time_since_last / self.spread_shot_cooldown, 1)
        
    def can_torpedo(self):
        current_time = pygame.time.get_ticks()
        time_since_last = (current_time - self.last_torpedo_shot_time) / 1000
        return time_since_last >= self.torpedo_shot_cooldown
    
    def torpedo_shot(self):
        if self.can_torpedo():
            forward = pygame.Vector2(0, 1).rotate(self.rotation)
            forward *= (PLAYER_SHOOT_SPEED * 2)
            torpedo = TorpedoShot(self.position.x, self.position.y, forward, self.rotation)
            
            # Add to all necessary sprite groups
            self.game.torpedo_shots.add(torpedo)
            self.game.torpedo_shots.add(torpedo)
            self.game.drawable.add(torpedo)
            self.game.updatable.add(torpedo)
            
            self.last_torpedo_shot_time = pygame.time.get_ticks()
      
    def get_torpedo_cooldown_progress(self):
        current_time = pygame.time.get_ticks()
        time_since_last = (current_time - self.last_torpedo_shot_time) / 1000
        return min(time_since_last / self.torpedo_shot_cooldown, 1)

    def boost(self):
        if not self.boost_active and self.boost_cooldown <= 0:
            self.boost_active = True
            self.boost_timer = 0

    def get_world_vertices(self):
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
        if self.shield_active:
            shield_radius = self.radius * 1.4
            distance = pygame.math.Vector2(other.position).distance_to(self.position)
            if distance <= shield_radius + other.radius:
                self.shield_active = False
                return False
            
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