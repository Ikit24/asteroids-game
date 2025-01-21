import pygame

class Explosion(pygame.sprite.Sprite):
    images = []

    @classmethod
    def load_images(cls):
        if not cls.images:
            for i in range(6):
                image = pygame.image.load(f"images/exp{i}.png").convert_alpha()
                cls.images.append(image)

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.load_images()
        self.frame = 0
        self.animation_speed = 0.1
        self.timer = 0
        self. position = pygame.math.Vector2(x, y)
        self.image = self.images[self.frame]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self, dt):
        self.timer += dt
        if self.timer >=self.animation_speed:                     
            self.frame +=1
            self.timer = 0
            if self.frame >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = (self.position.x, self.position.y)

    def draw(self, screen):
        screen.blit(self.image, self.rect)