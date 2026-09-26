import pygame

class Bullet:
    def __init__(self, x, y, direction="up", speed=None, screen_height=600):
        self.width = 24
        self.height = 24
        self.image = pygame.image.load("assets/bullet.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = speed if speed is not None else (5 if direction == "up" else 3)
        self.vx = 0
        self.vy = -self.speed if direction == "up" else self.speed
        self.screen_height = screen_height
        self.is_active = True

    def update(self):
        self.x += self.vx
        self.y += self.vy

        if self.direction == "up":
            if self.y < -self.height:
                self.is_active = False
        else:
            if self.y > self.screen_height + self.height:
                self.is_active = False

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        if self.is_active:
            screen.blit(self.image, (self.x, self.y))
