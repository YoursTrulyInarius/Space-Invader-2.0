import pygame

class Player:
    def __init__(self, screen_width, screen_height):
        self.width = 80
        self.height = 80
        self.speed = 5
        self.image = pygame.image.load("assets/myship.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.x = screen_width // 2 - self.width // 2
        self.y = screen_height - 100
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.is_blinking = False
        self.blink_timer = 0
        self.visible = True

    def move_left(self):
        if not self.is_blinking:
            self.x -= self.speed

    def move_right(self):
        if not self.is_blinking:
            self.x += self.speed

    def keep_inside_screen(self):
        self.x = max(0, min(self.x, self.screen_width - self.width))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update_blink(self):
        if self.is_blinking:
            self.blink_timer += 1
            
            if self.blink_timer % 10 == 0:
                self.visible = not self.visible
        else:
            self.visible = True

    def draw(self, screen):
        if self.visible:
            screen.blit(self.image, (self.x, self.y))
