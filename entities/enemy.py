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
        self.horizontal_speed = 2.0
        self.direction = 1
        self.vertical_step = 14
        self.max_bottom_y = self.screen_height - 160
        self.min_top_y = 80
        self.dx = 0
        self.dy = 0
        self.fire_cooldown = random.randint(80, 160)

    def start_drop(self, target_x, target_y):
        """Dive toward the player's current position."""
        self.state = "dropping"

        distance_x = target_x - (self.x + self.width // 2)
        distance_y = target_y - self.y
        distance = (distance_x ** 2 + distance_y ** 2) ** 0.5

        if distance > 0:
            self.dx = (distance_x / distance) * self.speed
            self.dy = (distance_y / distance) * self.speed
        else:
            self.dx = 0
            self.dy = self.speed

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
                self.y += self.vertical_step
                self.direction *= -1

            if self.y + self.height >= self.max_bottom_y:
                self.y = self.max_bottom_y - self.height
                self.state = "limit"

            if self.y + self.height >= self.screen_height:
                self.state = "offscreen"

        elif self.state == "limit":
            self.x += self.direction * self.horizontal_speed

            if self.x <= 0 or self.x + self.width >= self.screen_width:
                self.x = max(0, min(self.x, self.screen_width - self.width))
                self.direction *= -1

            if self.y < self.min_top_y:
                self.y = self.min_top_y

        elif self.state == "dropping":
            self.x += self.dx
            self.y += self.dy

            if self.y + self.height >= self.max_bottom_y:
                self.y = self.max_bottom_y - self.height
                self.state = "limit"

            if (self.y > self.screen_height + self.height or
                    self.x < -self.width * 2 or
                    self.x > self.screen_width + self.width):
                self.state = "offscreen"

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        if self.state != "offscreen":
            screen.blit(self.image, (self.x, self.y))
