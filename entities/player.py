import pygame

# Maps color names (from DB) to RGB tint values
# Use fully saturated, bright colors so the tint result is vivid.
SHIP_COLOR_MAP = {
    "green":  (0,   255, 80),
    "blue":   (60,  180, 255),
    "red":    (255, 60,  60),
    "yellow": (255, 230, 0),
    "purple": (210, 0,   255),
}

class Player:
    def __init__(self, screen_width, screen_height, ship_color="green"):
        self.width = 80
        self.height = 80
        self.speed = 5
        raw = pygame.image.load("assets/myship.png").convert_alpha()
        self.base_image = pygame.transform.scale(raw, (self.width, self.height))

        # Build a grayscale (luminance) version of the ship ONCE.
        # Grayscale * any_color via BLEND_RGB_MULT gives correct tinting
        # regardless of what colors the original artwork contains.
        self.gray_image = self._make_grayscale(self.base_image)

        self.x = screen_width // 2 - self.width // 2
        self.y = screen_height - 100
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.is_blinking = False
        self.blink_timer = 0
        self.visible = True

        self.set_color(ship_color)

    # ------------------------------------------------------------------
    @staticmethod
    def _make_grayscale(surface):
        """
        Return a new SRCALPHA surface where every pixel is converted to
        luminance-correct grayscale while the alpha channel is kept intact.
        Runs once at load time (80×80 = 6 400 pixels — negligible cost).
        """
        w, h = surface.get_size()
        gray = pygame.Surface((w, h), flags=pygame.SRCALPHA)
        for px in range(w):
            for py in range(h):
                r, g, b, a = surface.get_at((px, py))
                # Luminance-correct grayscale, then boost brightness so
                # BLEND_RGB_MULT produces vivid, fully-saturated colors.
                # Without the boost, mid-gray (~128) * tint stays dim.
                lum = int(0.299 * r + 0.587 * g + 0.114 * b)
                lum = min(255, int(lum * 1.9))   # <-- brightness boost
                gray.set_at((px, py), (lum, lum, lum, a))
        return gray

    # ------------------------------------------------------------------
    def set_color(self, color_name):
        """
        Tint the ship image with the chosen color.
        Strategy: copy the grayscale base, then BLEND_RGB_MULT with the
        target color.  Gray × color = correct hue at full brightness,
        and alpha is never touched so transparency is preserved perfectly.
        """
        tint = SHIP_COLOR_MAP.get(color_name, SHIP_COLOR_MAP["green"])
        self.image = self.gray_image.copy()

        w, h = self.image.get_size()
        tint_surf = pygame.Surface((w, h), flags=pygame.SRCALPHA)
        tint_surf.fill((tint[0], tint[1], tint[2], 255))  # alpha=255 keeps BLEND_RGB_MULT from touching alpha

        # BLEND_RGB_MULT: result_RGB = (gray_RGB * tint_RGB) / 255
        # Because gray_RGB = (L, L, L), result is (L*tR/255, L*tG/255, L*tB/255)
        # — i.e. the tint color scaled by luminance. Alpha channel is untouched.
        self.image.blit(tint_surf, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

    # ------------------------------------------------------------------
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
