import pygame

class Bullet:
    def __init__(self, x, y):
        self.width = 32
        self.height = 32
        self.image = pygame.image.load("assets/bullet.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.x = x
        self.y = y
        self.speed = 7
        self.is_active = True

    def update(self):
        self.y -= self.speed
        if self.y < -self.height:
            self.is_active = False

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        if self.is_active:
            screen.blit(self.image, (self.x, self.y))
