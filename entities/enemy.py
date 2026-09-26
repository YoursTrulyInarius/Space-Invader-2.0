import random
import pygame

class Enemy:
    def __init__(self, index, total_enemies, screen_width, screen_height=600):
        self.width = 60
        self.height = 60
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.image = pygame.image.load("assets/enemyship.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

        spacing = screen_width / (total_enemies + 1)
        self.target_mid_x = spacing * (index + 1) - (self.width // 2)

        # Alternate rows for a classic Space Invaders stagger
        self.target_mid_y = 100 + (60 if index % 2 == 0 else 0)

        self.x = self.target_mid_x
        self.y = -self.height  # start above screen

        self.state = "entering"
        self.speed = 4
        self.horizontal_speed = 1.1
        self.direction = 1
        self.vertical_step = 10
        self.max_bottom_y = min(self.screen_height - 120, int(self.screen_height * 0.62))
        self.min_top_y = 90
        self.turn_step = 16
        self.dx = 0
        self.dy = 0
        self.fire_cooldown = random.randint(80, 160)

    def start_drop(self, target_x, target_y):
        """Kept for compatibility, but enemies stay in the upper-middle zone."""
        self.state = "waiting"
        self.y = min(self.y, self.max_bottom_y - self.height)

    def update(self, direction=None):
        if direction is not None:
            self.direction = direction

        if self.state == "entering":
            if self.y < self.target_mid_y:
                self.y += 2
            else:
                self.y = self.target_mid_y
                self.state = "waiting"

        elif self.state == "waiting":
            self.x += self.direction * self.horizontal_speed

            if self.x <= 0 or self.x + self.width >= self.screen_width:
                self.x = max(0, min(self.x, self.screen_width - self.width))
                self.y += self.turn_step
                self.direction *= -1

            self.y = max(self.min_top_y, min(self.y, self.max_bottom_y - self.height))

            if self.y + self.height >= self.screen_height:
                self.state = "offscreen"

        elif self.state == "limit":
            self.x += self.direction * self.horizontal_speed

            if self.x <= 0 or self.x + self.width >= self.screen_width:
                self.x = max(0, min(self.x, self.screen_width - self.width))
                self.direction *= -1

            self.y = max(self.min_top_y, min(self.y, self.max_bottom_y - self.height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        if self.state != "offscreen":
            screen.blit(self.image, (self.x, self.y))
