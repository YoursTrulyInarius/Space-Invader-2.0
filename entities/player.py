import pygame

# Maps color names (from DB) to RGB tint values
SHIP_COLOR_MAP = {
    "green":  (0,   255, 0),
    "blue":   (0,   150, 255),
    "red":    (255, 50,  50),
    "yellow": (255, 220, 0),
    "purple": (180, 0,   255),
}

class Player:
    def __init__(self, screen_width, screen_height, ship_color="green"):
        self.width = 80
        self.height = 80
        self.speed = 5
        self.base_image = pygame.image.load("assets/myship.png").convert_alpha()
        self.base_image = pygame.transform.scale(self.base_image, (self.width, self.height))
        self.x = screen_width // 2 - self.width // 2
        self.y = screen_height - 100
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.is_blinking = False
        self.blink_timer = 0
        self.visible = True

        self.set_color(ship_color)

    def set_color(self, color_name):
        """Apply a color tint to the ship image."""
        tint = SHIP_COLOR_MAP.get(color_name, SHIP_COLOR_MAP["green"])
        self.image = self.base_image.copy()
        tint_surface = pygame.Surface(self.image.get_size(), flags=pygame.SRCALPHA)
        tint_surface.fill((*tint, 100))  # semi-transparent tint overlay
        self.image.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def move_left(self, use_wasd=False):
        if not self.is_blinking:
            self.x -= self.speed

    def move_right(self, use_wasd=False):
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

