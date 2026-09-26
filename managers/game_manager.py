import pygame
import random
from entities.player import Player, SHIP_COLOR_MAP
from entities.button import MobileButtons
from entities.enemy import Enemy
from entities.bullet import Bullet
from managers.db_manager import DBManager

# --- Profile options ---
SHIP_COLORS   = ["green", "blue", "red", "yellow", "purple"]
SHIP_COLOR_RGB = {
    "green":  (0,   255, 80),
    "blue":   (60,  180, 255),
    "red":    (255, 60,  60),
    "yellow": (255, 230, 0),
    "purple": (210, 0,   255),
}
CONTROL_SCHEMES = ["arrows", "wasd"]
DIFFICULTIES    = ["easy", "normal", "hard"]
DIFFICULTY_LABELS = {"easy": "Easy", "normal": "Normal", "hard": "Hard"}

# Difficulty multipliers (enemy spawn count modifier)
DIFFICULTY_SPAWN = {"easy": 3, "normal": 5, "hard": 8}

# Original visual identity: "editorial noir" with charcoal, ivory, and plum accents.
DARK_BG   = (12, 12, 16)
ACCENT    = (205, 138, 186)
ACCENT_2  = (148, 202, 187)
WHITE     = (241, 236, 228)
GRAY      = (168, 164, 156)
DARK_BTN  = (30, 29, 35)
SEL_BTN   = (118, 86, 120)
SEL_BTN_H = (219, 178, 205)
RED_ERR   = (230, 118, 118)
GOLD      = (212, 182, 104)
PANEL_BG  = (21, 21, 26)
PANEL_BOR = (143, 133, 146)
FIELD_BG  = (15, 15, 20)
ACCENT_DIM = (72, 53, 76)


def draw_panel(screen, rect, fill_color=PANEL_BG, border_color=PANEL_BOR, radius=18):
    """Draw a refined editorial panel with soft depth and a structured frame."""
    shadow = pygame.Rect(rect.x + 7, rect.y + 9, rect.width, rect.height)
    shadow_surface = pygame.Surface((shadow.width, shadow.height), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surface, (0, 0, 0, 95), shadow_surface.get_rect(), border_radius=radius)
    screen.blit(shadow_surface, shadow.topleft)

    pygame.draw.rect(screen, fill_color, rect, border_radius=radius)
    pygame.draw.rect(screen, border_color, rect, 2, border_radius=radius)

    top_line = pygame.Rect(rect.x + 16, rect.y + 14, rect.width - 32, 3)
    pygame.draw.rect(screen, ACCENT, top_line, border_radius=2)

    inner = pygame.Rect(rect.x + 10, rect.y + 10, rect.width - 20, rect.height - 20)
    inner_surface = pygame.Surface((inner.width, inner.height), pygame.SRCALPHA)
    pygame.draw.rect(inner_surface, (255, 255, 255, 14), inner_surface.get_rect(), border_radius=radius - 6)
    screen.blit(inner_surface, inner.topleft)


def draw_option_row(screen, font, label, options, selected, y, x_start, item_w=120, item_h=40):
    """Draw a labeled row of selectable option buttons. Returns list of (rect, option) tuples."""
    label_surf = font.render(label, True, WHITE)
    screen.blit(label_surf, (x_start, y + 8))

    rects = []
    btn_x = x_start + 180
    for opt in options:
        rect = pygame.Rect(btn_x, y, item_w, item_h)
        is_selected = opt == selected
        color = SEL_BTN if is_selected else DARK_BTN
        base_border = ACCENT_2 if is_selected else (117, 95, 86)
        pygame.draw.rect(screen, color, rect, border_radius=10)
        pygame.draw.rect(screen, base_border, rect, 2, border_radius=10)

        if label == "Ship Color:":
            pygame.draw.circle(screen, SHIP_COLOR_RGB.get(opt, WHITE),
                               (btn_x + item_w // 2, y + item_h // 2), 12)
            pygame.draw.circle(screen, WHITE if is_selected else GRAY,
                               (btn_x + item_w // 2, y + item_h // 2), 12, 2)
        else:
            disp = opt.upper() if label == "Controls:" else DIFFICULTY_LABELS.get(opt, opt.capitalize())
            txt = font.render(disp, True, WHITE)
            screen.blit(txt, (btn_x + (item_w - txt.get_width()) // 2,
                               y + (item_h - txt.get_height()) // 2))

        rects.append((rect, opt))
        btn_x += item_w + 10
    return rects


def draw_glow_rect(screen, rect, color, radius=10, layers=3):
    """Draw a soft rectangular glow around a rect."""
    for i in range(layers, 0, -1):
        expand = i * 3
        alpha = 42 // i
        glow_rect = rect.inflate(expand * 2, expand * 2)
        s = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (*color, alpha), s.get_rect(), border_radius=radius + expand)
        screen.blit(s, glow_rect.topleft)


def draw_text_field(screen, font, rect, text, placeholder, focused, masked=False, label=None, label_font=None):
    """Draw a styled input field with optional floating label above it."""
    border_color = ACCENT if focused else (88, 82, 93)
    bg_color = (20, 20, 26) if focused else FIELD_BG

    if focused:
        draw_glow_rect(screen, rect, ACCENT, radius=12, layers=2)

    pygame.draw.rect(screen, bg_color, rect, border_radius=12)
    pygame.draw.rect(screen, border_color, rect, 2, border_radius=12)

    display = ("●" * len(text)) if masked else text
    if display:
        surf = font.render(display, True, WHITE)
    else:
        surf = font.render(placeholder, True, (149, 146, 152))

    screen.blit(surf, (rect.x + 14, rect.y + (rect.height - surf.get_height()) // 2))

    if focused and (pygame.time.get_ticks() // 530) % 2 == 0:
        cx_pos = rect.x + 14 + (surf.get_width() if display else 0) + 2
        pygame.draw.line(screen, ACCENT,
                         (cx_pos, rect.y + 10),
                         (cx_pos, rect.bottom - 10), 2)

    if label and label_font and focused:
        lbl_surf = label_font.render(label, True, ACCENT)
        lx = rect.x + 10
        ly = rect.y - lbl_surf.get_height() - 4
        screen.blit(lbl_surf, (lx, ly))


def draw_button(screen, font, rect, text, primary=True):
    """Draw a polished editorial button with a softer luxury finish."""
    if primary:
        top_rect = pygame.Rect(rect.x, rect.y, rect.width, rect.height // 2)
        bottom_rect = pygame.Rect(rect.x, rect.y + rect.height // 2, rect.width, rect.height - rect.height // 2)
        pygame.draw.rect(screen, SEL_BTN_H, top_rect, border_radius=12)
        pygame.draw.rect(screen, SEL_BTN, bottom_rect, border_radius=0)
        pygame.draw.rect(screen, SEL_BTN, rect, border_radius=12)
        pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=12)
    else:
        pygame.draw.rect(screen, DARK_BTN, rect, border_radius=12)
        pygame.draw.rect(screen, (126, 118, 130), rect, 2, border_radius=12)

    txt_surf = font.render(text, True, WHITE)
    screen.blit(txt_surf, (rect.centerx - txt_surf.get_width() // 2,
                            rect.centery - txt_surf.get_height() // 2))


def draw_divider(screen, cx, y, width=340, color=None):
    """Draw a horizontal decorative divider."""
    if color is None:
        color = ACCENT_2
    pygame.draw.line(screen, color, (cx - width // 2, y), (cx + width // 2, y), 2)


def draw_glow_title(screen, big_font, text, cx, y, color=ACCENT_2):
    """Draw title text with a soft colour glow underneath."""
    glow = big_font.render(text, True, (*color, 80))
    for dx, dy in [(-2, 2), (2, 2), (0, 3)]:
        gs = pygame.Surface(glow.get_size(), pygame.SRCALPHA)
        gs.blit(glow, (0, 0))
        gs.set_alpha(45)
        screen.blit(gs, (cx - glow.get_width() // 2 + dx, y + dy))
    surf = big_font.render(text, True, color)
    screen.blit(surf, (cx - surf.get_width() // 2, y))


def draw_stars(screen, stars):
    """Draw a simple star-field background."""
    t = pygame.time.get_ticks()
    for i, (x, y, r, brightness) in enumerate(stars):
        flicker = int(brightness + 30 * ((t // 800 + i * 37) % 3 - 1) * 0.3)
        flicker = max(60, min(220, flicker))
        pygame.draw.circle(screen, (flicker, flicker, flicker), (x, y), r)


def generate_stars(screen_width, screen_height, count=150):
    """Generate random star positions for background."""
    stars = []
    for _ in range(count):
        x = random.randint(0, screen_width)
        y = random.randint(0, screen_height)
        r = random.choice([1, 1, 1, 2])
        b = random.randint(50, 170)
        stars.append((x, y, r, b))
    return stars


def clean_username(username):
    """Filter out non-printable ASCII or control characters from username."""
    if not username:
        return "Guest"
    cleaned = "".join(c for c in username if c.isprintable() and ord(c) >= 32)
    return cleaned.strip() or "Guest"


def render_retro_score(score_val, color, scale=3):
    """Render score as pixelated 8-bit retro font by drawing at small size and scaling up."""
    small_font = pygame.font.SysFont("Consolas", 14, bold=True)
    temp = small_font.render(str(score_val), False, color)
    w, h = temp.get_size()
    return pygame.transform.scale(temp, (int(w * scale), int(h * scale)))


def draw_heart(screen, x, y, color, size=14):
    """Draw a cleaner heart icon for the HUD."""
    surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    cx = size
    cy = size

    pygame.draw.circle(surface, color, (cx - size // 2, cy - size // 3), size // 2)
    pygame.draw.circle(surface, color, (cx + size // 2, cy - size // 3), size // 2)
    pygame.draw.polygon(surface, color, [
        (cx, cy + size // 2),
        (cx - size, cy - size // 4),
        (cx - size // 2, cy - size),
        (cx, cy - size // 2),
        (cx + size // 2, cy - size),
        (cx + size, cy - size // 4),
    ])
    screen.blit(surface, (x, y))


class GameManager:
    def __init__(self, screen, screen_width, screen_height, player_name=""):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.player_name = player_name
        self.db = DBManager(user="root", password="")
        self.leaderboard = []
        self.stars = generate_stars(screen_width, screen_height)

        self.font       = pygame.font.SysFont("Georgia", 28, bold=True)
        self.big_font   = pygame.font.SysFont("Georgia", 68, bold=True)
        self.small_font = pygame.font.SysFont("Trebuchet MS", 22, bold=True)
        self.tiny_font  = pygame.font.SysFont("Trebuchet MS", 18, bold=True)

        # --- Layout constants ---
        cx = screen_width // 2

        # Name input screen rects (shown after login)
        self.name_input_rect   = pygame.Rect(cx - 160, 320, 320, 52)
        self.start_button_rect = pygame.Rect(cx - 110, 400, 220, 52)
        self.profile_btn_rect  = pygame.Rect(cx - 110, 468, 220, 42)

        # Reload rect (game over) — repositioned dynamically in _update_game_over
        self.reload_button_rect = pygame.Rect(cx - 110, screen_height // 2 + 50, 220, 52)

        # Profile state
        self.profile_ship_color   = "green"
        self.profile_control      = "arrows"
        self.profile_difficulty   = "normal"
        self.profile_back_rect    = pygame.Rect(cx - 110, screen_height - 80, 220, 48)
        self.profile_option_rects = []

        # --- Login screen rects ---
        field_w = 360
        self.login_user_rect    = pygame.Rect(cx - field_w // 2, 220, field_w, 54)
        self.login_pass_rect    = pygame.Rect(cx - field_w // 2, 304, field_w, 54)
        self.login_btn_rect     = pygame.Rect(cx - 182, 392, 170, 54)
        self.login_reg_btn_rect = pygame.Rect(cx + 12, 392, 170, 54)
        self.login_lb_btn_rect  = pygame.Rect(cx - 120, 468, 240, 42)

        # --- Register screen rects ---
        self.reg_user_rect    = pygame.Rect(cx - field_w // 2, 198, field_w, 54)
        self.reg_pass_rect    = pygame.Rect(cx - field_w // 2, 280, field_w, 54)
        self.reg_conf_rect    = pygame.Rect(cx - field_w // 2, 362, field_w, 54)
        self.reg_create_rect  = pygame.Rect(cx - 182, 444, 170, 54)
        self.reg_back_rect    = pygame.Rect(cx + 12, 444, 170, 54)

        # --- Leaderboard screen rect ---
        self.lb_back_rect = pygame.Rect(cx - 100, 528, 200, 46)

        # --- Auth state ---
        self.login_username  = ""
        self.login_password  = ""
        self.login_focus     = "username"   # "username" | "password"
        self.login_error     = ""

        self.reg_username    = ""
        self.reg_password    = ""
        self.reg_confirm     = ""
        self.reg_focus       = "username"   # "username" | "password" | "confirm"
        self.reg_error       = ""
        self.reg_success     = ""

        self.old_name = ""
        self.fire_cooldown = 0
        self.reset_game()

    # ------------------------------------------------------------------
    # reset_game
    # ------------------------------------------------------------------
    def reset_game(self):
        self.player  = Player(self.screen_width, self.screen_height, self.profile_ship_color)
        self.buttons = MobileButtons()
        self.bullets = []
        self.enemy_bullets = []
        self.enemies = []

        self.score        = 0
        self.personal_best = 0
        self.max_player_lives = 3
        self.player_lives = self.max_player_lives
        self.spawn_number = DIFFICULTY_SPAWN.get(self.profile_difficulty, 5)
        self.game_state   = "login"

        self.old_name     = self.player_name
        self.player_history = []
        self.timer        = 0
        self.state_timer  = 0
        self.enemy_direction = 1
        self.enemy_fire_timer = 0
        self.fire_cooldown = 0
        self.bullets = []
        self.enemy_bullets = []

        # Clear auth fields on full reset
        self.login_username = self.player_name  # pre-fill if returning
        self.login_password = ""
        self.login_error    = ""
        self.reg_username   = ""
        self.reg_password   = ""
        self.reg_confirm    = ""
        self.reg_error      = ""
        self.reg_success    = ""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _load_profile_from_db(self):
        """Pull saved profile settings for the current player from DB."""
        if not self.player_name:
            return
        profile = self.db.get_player_profile(self.player_name)
        if profile:
            self.profile_ship_color = profile.get("ship_color", "green") or "green"
            self.profile_control    = profile.get("control_scheme", "arrows") or "arrows"
            self.profile_difficulty = profile.get("difficulty", "normal") or "normal"
            self.player.set_color(self.profile_ship_color)
        self.personal_best = self.db.get_player_best_score(self.player_name)

    def _save_profile_to_db(self):
        """Persist current profile settings to DB."""
        if not self.player_name:
            return
        self.db.get_or_create_player(self.player_name)
        self.db.update_player_profile(
            self.player_name,
            ship_color     = self.profile_ship_color,
            control_scheme = self.profile_control,
            difficulty     = self.profile_difficulty,
        )

    def _after_login(self):
        """Common post-login initialisation."""
        self._load_profile_from_db()
        self.spawn_number = DIFFICULTY_SPAWN.get(self.profile_difficulty, 5)
        self.player.set_color(self.profile_ship_color)
        self.game_state = "name_input"

    def _start_game(self):
        """Common logic when pressing START from the name input screen."""
        self.player_name = self.player_name.strip() or "Guest"
        if self.old_name and self.old_name != self.player_name:
            self.db.update_player_username(self.old_name, self.player_name)
        self.db.get_or_create_player(self.player_name)
        self._load_profile_from_db()
        self.spawn_number = DIFFICULTY_SPAWN.get(self.profile_difficulty, 5)
        self.player.set_color(self.profile_ship_color)
        self.game_state = "playing"
        self.spawn_enemies()

    def _handle_text_input(self, event, field_name, max_len=50, digits_only=False):
        """Generic keyboard handling for a text input field. Returns updated string."""
        current = getattr(self, field_name)
        ctrl = pygame.key.get_mods() & pygame.KMOD_CTRL
        if event.key == pygame.K_BACKSPACE:
            if ctrl:
                current = ""
            else:
                current = current[:-1]
        elif event.key == pygame.K_v and ctrl:
            try:
                clip = pygame.scrap.get(pygame.SCRAP_TEXT)
                if clip:
                    text = clip.decode("utf-8", errors="ignore").replace("\x00", "").split("\n")[0]
                    current = (current + text)[:max_len]
            except Exception:
                pass
        elif event.unicode and event.unicode.isprintable() and event.key != pygame.K_TAB:
            if len(current) < max_len:
                current += event.unicode
        setattr(self, field_name, current)

    # ------------------------------------------------------------------
    # spawn_enemies
    # ------------------------------------------------------------------
    def spawn_enemies(self):
        self.enemies = []
        self.enemy_direction = 1
        for i in range(self.spawn_number):
            enemy = Enemy(i, self.spawn_number, self.screen_width, self.screen_height)
            enemy.direction = self.enemy_direction
            self.enemies.append(enemy)
        self.timer = 0

    # ------------------------------------------------------------------
    # update (main dispatcher)
    # ------------------------------------------------------------------
    def update(self, events):
        if self.game_state == "login":
            self._update_login(events)
        elif self.game_state == "register":
            self._update_register(events)
        elif self.game_state == "leaderboard":
            self._update_leaderboard(events)
        elif self.game_state == "name_input":
            self._update_name_input(events)
        elif self.game_state == "profile":
            self._update_profile(events)
        elif self.game_state in ("playing", "blinking"):
            self._update_playing(events)
        elif self.game_state == "game_over":
            self._update_game_over(events)

    # ------------------------------------------------------------------
    # LOGIN state
    # ------------------------------------------------------------------
    def _update_login(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.login_focus = "password" if self.login_focus == "username" else "username"
                elif event.key == pygame.K_RETURN:
                    self._do_login()
                    return
                elif self.login_focus == "username":
                    self._handle_text_input(event, "login_username", max_len=50)
                elif self.login_focus == "password":
                    self._handle_text_input(event, "login_password", max_len=100)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.login_user_rect.collidepoint(event.pos):
                    self.login_focus = "username"
                elif self.login_pass_rect.collidepoint(event.pos):
                    self.login_focus = "password"
                elif self.login_btn_rect.collidepoint(event.pos):
                    self._do_login()
                    return
                elif self.login_reg_btn_rect.collidepoint(event.pos):
                    self.reg_username = self.login_username
                    self.reg_password = ""
                    self.reg_confirm  = ""
                    self.reg_error    = ""
                    self.reg_success  = ""
                    self.reg_focus    = "username"
                    self.game_state   = "register"
                    return
                elif self.login_lb_btn_rect.collidepoint(event.pos):
                    self.leaderboard = self.db.get_top_scores(limit=10)
                    self.game_state  = "leaderboard"
                    return

        self._draw_login()

    def _do_login(self):
        if not self.login_username.strip():
            self.login_error = "Please enter a username."
            return
        if not self.login_password:
            self.login_error = "Please enter a password."
            return

        player_row = self.db.login_player(self.login_username.strip(), self.login_password)
        if player_row:
            self.player_name  = player_row["username"]
            self.login_error  = ""
            self.login_password = ""
            self._after_login()
        else:
            self.login_error = "Incorrect username or password."

    def _draw_login(self):
        self.screen.fill(DARK_BG)
        draw_stars(self.screen, self.stars)

        cx = self.screen_width // 2
        sw = self.screen_width

        # ── Glowing title ──────────────────────────────────────────
        draw_glow_title(self.screen, self.big_font, "Space Invaders", cx, 32)

        sub = self.small_font.render("Sign in to play", True, GRAY)
        self.screen.blit(sub, (cx - sub.get_width() // 2, 108))

        # Decorative accent line
        draw_divider(self.screen, cx, 140, width=260, color=(0, 120, 55))

        # ── Card panel ─────────────────────────────────────────────
        panel = pygame.Rect(cx - 245, 170, 490, 340)
        draw_panel(self.screen, panel, fill_color=PANEL_BG, border_color=PANEL_BOR, radius=22)

        # Column labels above fields
        lbl_u = self.tiny_font.render("USERNAME", True, (80, 90, 140))
        lbl_p = self.tiny_font.render("PASSWORD", True, (80, 90, 140))
        self.screen.blit(lbl_u, (self.login_user_rect.x + 6,
                                  self.login_user_rect.y - lbl_u.get_height() - 8))
        self.screen.blit(lbl_p, (self.login_pass_rect.x + 6,
                                  self.login_pass_rect.y - lbl_p.get_height() - 8))

        # Fields
        draw_text_field(self.screen, self.font, self.login_user_rect,
                        self.login_username, "Enter username...", self.login_focus == "username")
        draw_text_field(self.screen, self.font, self.login_pass_rect,
                        self.login_password, "Enter password...", self.login_focus == "password", masked=True)

        # Buttons
        draw_button(self.screen, self.font, self.login_btn_rect,     "LOGIN",    primary=True)
        draw_button(self.screen, self.font, self.login_reg_btn_rect, "REGISTER", primary=False)

        # Divider between buttons and leaderboard
        draw_divider(self.screen, cx, 462, width=420, color=(30, 34, 60))

        # Leaderboard link
        draw_button(self.screen, self.small_font, self.login_lb_btn_rect, "  Leaderboard", primary=False)

        # Error message
        if self.login_error:
            err_bg = pygame.Rect(cx - 185, 515, 370, 30)
            pygame.draw.rect(self.screen, (50, 10, 10), err_bg, border_radius=6)
            err = self.small_font.render(self.login_error, True, RED_ERR)
            self.screen.blit(err, (cx - err.get_width() // 2, 520))

        # Hint footer
        hint = self.tiny_font.render("Tab  switch field   •   Enter  login", True, (50, 54, 82))
        self.screen.blit(hint, (cx - hint.get_width() // 2, self.screen_height - 26))

    # ------------------------------------------------------------------
    # REGISTER state
    # ------------------------------------------------------------------
    def _update_register(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    order = ["username", "password", "confirm"]
                    idx = order.index(self.reg_focus)
                    self.reg_focus = order[(idx + 1) % len(order)]
                elif event.key == pygame.K_RETURN:
                    self._do_register()
                    return
                elif self.reg_focus == "username":
                    self._handle_text_input(event, "reg_username", max_len=50)
                elif self.reg_focus == "password":
                    self._handle_text_input(event, "reg_password", max_len=100)
                elif self.reg_focus == "confirm":
                    self._handle_text_input(event, "reg_confirm", max_len=100)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.reg_user_rect.collidepoint(event.pos):
                    self.reg_focus = "username"
                elif self.reg_pass_rect.collidepoint(event.pos):
                    self.reg_focus = "password"
                elif self.reg_conf_rect.collidepoint(event.pos):
                    self.reg_focus = "confirm"
                elif self.reg_create_rect.collidepoint(event.pos):
                    self._do_register()
                    return
                elif self.reg_back_rect.collidepoint(event.pos):
                    self.game_state = "login"
                    return

        self._draw_register()

    def _do_register(self):
        username = self.reg_username.strip()
        password = self.reg_password
        confirm  = self.reg_confirm

        if not username or len(username) < 3:
            self.reg_error = "Username must be at least 3 characters."
            return
        if not password or len(password) < 4:
            self.reg_error = "Password must be at least 4 characters."
            return
        if password != confirm:
            self.reg_error = "Passwords do not match."
            return

        ok, result = self.db.register_player(username, password)
        if ok:
            # Auto-login after successful registration
            self.player_name   = username
            self.reg_error     = ""
            self.reg_success   = f"Account created! Welcome, {username}!"
            self._after_login()
        else:
            self.reg_error = result

    def _draw_register(self):
        self.screen.fill(DARK_BG)
        draw_stars(self.screen, self.stars)

        cx = self.screen_width // 2

        draw_glow_title(self.screen, self.big_font, "Create Account", cx, 26)

        sub = self.small_font.render("Join the Space Invaders leaderboard!", True, GRAY)
        self.screen.blit(sub, (cx - sub.get_width() // 2, 100))

        draw_divider(self.screen, cx, 132, width=340, color=(0, 120, 55))

        # Panel
        panel = pygame.Rect(cx - 245, 155, 490, 340)
        draw_panel(self.screen, panel, fill_color=PANEL_BG, border_color=PANEL_BOR, radius=22)

        # Field labels
        labels_data = [
            ("USERNAME (3+ chars)",  self.reg_user_rect),
            ("PASSWORD (4+ chars)",  self.reg_pass_rect),
            ("CONFIRM PASSWORD",     self.reg_conf_rect),
        ]
        for lbl_text, f_rect in labels_data:
            lbl = self.tiny_font.render(lbl_text, True, (80, 90, 140))
            self.screen.blit(lbl, (f_rect.x + 4, f_rect.y - lbl.get_height() - 4))

        draw_text_field(self.screen, self.font, self.reg_user_rect,
                        self.reg_username, "Choose a username...", self.reg_focus == "username")
        draw_text_field(self.screen, self.font, self.reg_pass_rect,
                        self.reg_password, "Choose a password...", self.reg_focus == "password", masked=True)
        draw_text_field(self.screen, self.font, self.reg_conf_rect,
                        self.reg_confirm,  "Re-enter password...", self.reg_focus == "confirm",  masked=True)

        draw_button(self.screen, self.font, self.reg_create_rect, "CREATE", primary=True)
        draw_button(self.screen, self.font, self.reg_back_rect,   "< BACK", primary=False)

        # Error / success
        msg_y = 520
        if self.reg_error:
            err_bg = pygame.Rect(cx - 185, msg_y - 3, 370, 30)
            pygame.draw.rect(self.screen, (50, 10, 10), err_bg, border_radius=6)
            err = self.small_font.render(self.reg_error, True, RED_ERR)
            self.screen.blit(err, (cx - err.get_width() // 2, msg_y))
        if self.reg_success:
            ok_surf = self.small_font.render(self.reg_success, True, ACCENT)
            self.screen.blit(ok_surf, (cx - ok_surf.get_width() // 2, msg_y))

        hint = self.tiny_font.render("Tab  switch field   •   Enter  create", True, (50, 54, 82))
        self.screen.blit(hint, (cx - hint.get_width() // 2, self.screen_height - 26))

    # ------------------------------------------------------------------
    # LEADERBOARD state
    # ------------------------------------------------------------------
    def _update_leaderboard(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.lb_back_rect.collidepoint(event.pos):
                    self.game_state = "login"
                    return
            elif event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                self.game_state = "login"
                return

        self._draw_leaderboard()

    def _draw_leaderboard(self):
        self.screen.fill(DARK_BG)
        draw_stars(self.screen, self.stars)

        cx = self.screen_width // 2

        # Title with gold glow (properly centered)
        draw_glow_title(self.screen, self.big_font, "Leaderboard", cx, 18, color=GOLD)

        sub = self.small_font.render("Top 10 All-Time Scores", True, GRAY)
        self.screen.blit(sub, (cx - sub.get_width() // 2, 90))

        draw_divider(self.screen, cx, 118, width=320, color=(90, 70, 0))

        # Table panel
        table_rect = pygame.Rect(cx - 285, 126, 570, 384)
        draw_panel(self.screen, table_rect, fill_color=PANEL_BG, border_color=PANEL_BOR, radius=18)

        # Header row
        header_y = 138
        rank_x  = cx - 258
        name_x  = cx - 190
        score_center_x = cx + 125
        date_x  = cx + 172

        # Renders header columns
        headers = [("#", rank_x), ("PLAYER", name_x), ("DATE", date_x)]
        for h_text, h_x in headers:
            h_surf = self.tiny_font.render(h_text, True, (140, 120, 40))
            self.screen.blit(h_surf, (h_x, header_y))

        score_lbl_surf = self.tiny_font.render("SCORE", True, (140, 120, 40))
        self.screen.blit(score_lbl_surf, (score_center_x - score_lbl_surf.get_width() // 2, header_y))

        # Header divider
        pygame.draw.line(self.screen, (45, 48, 82),
                         (table_rect.x + 12, header_y + 24),
                         (table_rect.right - 12, header_y + 24), 1)

        if not self.leaderboard:
            no_data = self.font.render("No scores yet — be the first!", True, GRAY)
            self.screen.blit(no_data, (cx - no_data.get_width() // 2, 285))
        else:
            row_y = header_y + 32
            rank_colors = {1: GOLD, 2: (210, 210, 210), 3: (205, 130, 55)}
            medals      = {1: "1", 2: "2", 3: "3"}
            for i, entry in enumerate(self.leaderboard, start=1):
                display_name = clean_username(entry["username"])
                is_me     = (entry["username"] == self.player_name)
                row_color = ACCENT if is_me else (220, 220, 230)

                # Highlight strip for current player
                if is_me:
                    strip = pygame.Rect(table_rect.x + 6, row_y - 4,
                                        table_rect.width - 12, 32)
                    s = pygame.Surface((strip.width, strip.height), pygame.SRCALPHA)
                    s.fill((0, 200, 90, 25))
                    self.screen.blit(s, strip.topleft)
                    pygame.draw.rect(self.screen, (0, 180, 80, 60), strip, 1, border_radius=4)

                # Alternating row tint
                elif i % 2 == 0:
                    strip = pygame.Rect(table_rect.x + 6, row_y - 4,
                                        table_rect.width - 12, 32)
                    s = pygame.Surface((strip.width, strip.height), pygame.SRCALPHA)
                    s.fill((255, 255, 255, 6))
                    self.screen.blit(s, strip.topleft)

                rank_color = rank_colors.get(i, (100, 100, 120))
                rank_label = medals.get(i, str(i))
                rank_surf  = self.small_font.render(rank_label, True, rank_color)
                name_surf  = self.small_font.render(display_name[:18], True, row_color)
                score_surf = self.font.render(str(entry["score"]), True, row_color)

                achieved = entry.get("achieved_at")
                date_str = str(achieved)[:10] if achieved else "—"
                date_surf = self.tiny_font.render(date_str, True, (90, 95, 125))

                self.screen.blit(rank_surf,  (rank_x,  row_y))
                self.screen.blit(name_surf,  (name_x,  row_y))
                self.screen.blit(score_surf, (score_center_x - score_surf.get_width() // 2, row_y - 2))
                self.screen.blit(date_surf,  (date_x,  row_y + 6))
                row_y += 34

        # Back button
        draw_button(self.screen, self.font, self.lb_back_rect, "< BACK", primary=False)

    # ------------------------------------------------------------------
    # NAME INPUT state
    # ------------------------------------------------------------------
    def _update_name_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                ctrl_held = pygame.key.get_mods() & pygame.KMOD_CTRL
                if event.key == pygame.K_BACKSPACE:
                    if ctrl_held or getattr(self, "_name_select_all", False):
                        self.player_name = ""
                        self._name_select_all = False
                    else:
                        self.player_name = self.player_name[:-1]
                elif event.key == pygame.K_a and ctrl_held:
                    self._name_select_all = True
                elif event.key == pygame.K_v and ctrl_held:
                    try:
                        clipboard = pygame.scrap.get(pygame.SCRAP_TEXT)
                        if clipboard:
                            text = clipboard.decode("utf-8", errors="ignore").replace("\x00", "").split("\n")[0]
                            combined = self.player_name + text
                            self.player_name = combined[:15]
                    except Exception:
                        pass
                elif event.key == pygame.K_RETURN:
                    self._start_game()
                    return
                elif event.key != pygame.K_TAB and event.unicode.isprintable():
                    if getattr(self, "_name_select_all", False):
                        self.player_name = event.unicode
                        self._name_select_all = False
                    elif len(self.player_name) < 15:
                        self.player_name += event.unicode
                else:
                    self._name_select_all = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.start_button_rect.collidepoint(event.pos):
                    self._start_game()
                    return
                if self.profile_btn_rect.collidepoint(event.pos):
                    self.player_name = self.player_name.strip() or "Guest"
                    self.db.get_or_create_player(self.player_name)
                    self._load_profile_from_db()
                    self.game_state = "profile"
                    return

        # --- Draw name input screen ---
        self.screen.fill(DARK_BG)
        draw_stars(self.screen, self.stars)

        cx = self.screen_width // 2
        sh = self.screen_height

        # Glowing title
        draw_glow_title(self.screen, self.big_font, "Space Invaders", cx, 48)

        # Divider
        draw_divider(self.screen, cx, 126, width=280, color=(0, 120, 55))

        # Player info card (futuristic dashboard style)
        card = pygame.Rect(cx - 210, 142, 420, 96)
        draw_panel(self.screen, card, fill_color=PANEL_BG, border_color=PANEL_BOR, radius=18)

        # Left Column: Pilot Username
        pilot_lbl = self.tiny_font.render("PILOT", True, (80, 90, 140))
        pilot_val = self.font.render(self.player_name, True, ACCENT)
        self.screen.blit(pilot_lbl, (cx - 180, card.y + 22))
        self.screen.blit(pilot_val, (cx - 180, card.y + 44))

        # Vertical Divider
        pygame.draw.line(self.screen, (40, 44, 80), (cx, card.y + 16), (cx, card.bottom - 16), 1)

        # Right Column: Golden High Score Pill Badge
        pb_rect = pygame.Rect(cx + 20, card.y + 18, 160, 60)
        pygame.draw.rect(self.screen, (32, 26, 8), pb_rect, border_radius=12)
        pygame.draw.rect(self.screen, (150, 115, 20), pb_rect, 2, border_radius=12)

        pb_lbl = self.tiny_font.render("BEST SCORE", True, (180, 150, 80))
        pb_val = render_retro_score(self.personal_best, GOLD, scale=1.8)
        self.screen.blit(pb_lbl, (pb_rect.centerx - pb_lbl.get_width() // 2, pb_rect.y + 8))
        self.screen.blit(pb_val, (pb_rect.centerx - pb_val.get_width() // 2, pb_rect.y + 26))

        # Display name field
        dn_lbl = self.tiny_font.render("DISPLAY NAME", True, (80, 90, 140))
        self.screen.blit(dn_lbl, (self.name_input_rect.x + 4,
                                   self.name_input_rect.y - dn_lbl.get_height() - 6))

        draw_text_field(self.screen, self.font, self.name_input_rect,
                        self.player_name, "Your display name...", True)

        # START button
        draw_button(self.screen, self.font, self.start_button_rect, "PLAY", primary=True)

        # PROFILE button
        draw_button(self.screen, self.small_font, self.profile_btn_rect, "EDIT PROFILE", primary=False)

    # ------------------------------------------------------------------
    # PROFILE state
    # ------------------------------------------------------------------
    def _update_profile(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, category, value in self.profile_option_rects:
                    if rect.collidepoint(event.pos):
                        if category == "color":
                            self.profile_ship_color = value
                            self.player.set_color(value)
                        elif category == "control":
                            self.profile_control = value
                        elif category == "difficulty":
                            self.profile_difficulty = value
                if self.profile_back_rect.collidepoint(event.pos):
                    self._save_profile_to_db()
                    self.game_state = "name_input"

        self._draw_profile()

    def _draw_profile(self):
        self.screen.fill(DARK_BG)
        draw_stars(self.screen, self.stars)
        self.profile_option_rects = []

        cx = self.screen_width // 2

        draw_glow_title(self.screen, self.big_font, "Player Profile", cx, 26)
        draw_divider(self.screen, cx, 104, width=260, color=(0, 120, 55))

        sub = self.small_font.render(f"Player:  {self.player_name}", True, GRAY)
        self.screen.blit(sub, (cx - sub.get_width() // 2, 114))

        # Ship preview in a small card
        preview_card = pygame.Rect(cx - 48, 140, 96, 96)
        pygame.draw.rect(self.screen, PANEL_BG, preview_card, border_radius=12)
        pygame.draw.rect(self.screen, PANEL_BOR, preview_card, 2, border_radius=12)
        self.screen.blit(self.player.image, (cx - 40, 148))

        x_start = cx - 290
        y = 255

        rects = draw_option_row(self.screen, self.small_font,
                                "Ship Color:", SHIP_COLORS, self.profile_ship_color,
                                y, x_start, item_w=80)
        self.profile_option_rects += [(r, "color", v) for r, v in rects]
        y += 62

        rects = draw_option_row(self.screen, self.small_font,
                                "Controls:", CONTROL_SCHEMES, self.profile_control,
                                y, x_start, item_w=115)
        self.profile_option_rects += [(r, "control", v) for r, v in rects]
        y += 62

        legend = self.small_font.render("Arrow Keys / WASD  —  move    SPACE  —  shoot", True, (80, 90, 130))
        self.screen.blit(legend, (cx - legend.get_width() // 2, y))

        draw_button(self.screen, self.font, self.profile_back_rect, "Save & Back", primary=True)

    # ------------------------------------------------------------------
    # PLAYING / BLINKING state
    # ------------------------------------------------------------------
    def _update_playing(self, events):
        if self.game_state in ("playing", "blinking"):
            self.player_history.append((self.player.x, self.player.y))
            if len(self.player_history) > 60:
                self.player_history.pop(0)

        if self.game_state == "playing":
            keys = pygame.key.get_pressed()
            use_wasd = (self.profile_control == "wasd")

            left_key  = pygame.K_a    if use_wasd else pygame.K_LEFT
            right_key = pygame.K_d    if use_wasd else pygame.K_RIGHT

            if keys[left_key]:
                self.player.move_left()
            if keys[right_key]:
                self.player.move_right()

            screen_button_fired = self.buttons.handle_mouse(self.player, events)
            keyboard_fired = keys[pygame.K_SPACE]

            if self.fire_cooldown > 0:
                self.fire_cooldown -= 1

            if (screen_button_fired or keyboard_fired) and self.fire_cooldown <= 0:
                bullet_x = self.player.x + self.player.width // 2 - 16
                self.bullets.append(Bullet(bullet_x, self.player.y, direction="up", speed=3.5, screen_height=self.screen_height))
                self.fire_cooldown = 20

            self.player.keep_inside_screen()

            for bullet in self.bullets[:]:
                bullet.update()
                if not bullet.is_active:
                    self.bullets.remove(bullet)

            self.timer += 1
            self.enemy_fire_timer += 1

            alive_enemies = [e for e in self.enemies if e.state in ("waiting", "dropping")]
            if alive_enemies:
                min_x = min(e.x for e in alive_enemies)
                max_x = max(e.x + e.width for e in alive_enemies)
                if min_x <= 0 or max_x >= self.screen_width:
                    self.enemy_direction *= -1
                    for enemy in alive_enemies:
                        enemy.y += enemy.vertical_step

            for enemy in self.enemies:
                enemy.update(self.enemy_direction)

            if self.enemy_fire_timer >= 90:
                can_fire = [e for e in self.enemies if e.state in ("waiting", "dropping", "limit")]
                if can_fire:
                    shooter = random.choice(can_fire)
                    bullet_x = shooter.x + shooter.width // 2 - 12
                    bullet_y = shooter.y + shooter.height - 8
                    self.enemy_bullets.append(Bullet(bullet_x, bullet_y, direction="down", speed=2.5, screen_height=self.screen_height))
                self.enemy_fire_timer = 0

            for enemy_bullet in self.enemy_bullets[:]:
                enemy_bullet.update()
                if not enemy_bullet.is_active:
                    self.enemy_bullets.remove(enemy_bullet)

            all_despawned = all(e.state == "offscreen" for e in self.enemies)
            if all_despawned:
                self.spawn_number += 1
                self.spawn_enemies()

            self.check_collisions()

        elif self.game_state == "blinking":
            self.player.update_blink()
            self.state_timer += 1
            for enemy in self.enemies:
                enemy.update()

            if self.state_timer >= 180:
                if self.player_lives <= 0:
                    self.db.save_score(self.player_name, self.score)
                    if self.score > self.personal_best:
                        self.personal_best = self.score
                    self.leaderboard = self.db.get_top_scores(limit=10)
                    self.game_state = "game_over"
                else:
                    self.game_state = "playing"
                    self.player.is_blinking = False
                    self.player.visible = True
                    self.player.x = self.screen_width // 2 - self.player.width // 2
                    self.player.y = self.screen_height - 100
                    self.bullets = []
                    self.enemy_bullets = []

        # --- Draw playing / blinking ---
        self.screen.fill(DARK_BG)
        draw_stars(self.screen, self.stars)

        self.player.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        for bullet in self.bullets:
            bullet.draw(self.screen)
        for enemy_bullet in self.enemy_bullets:
            enemy_bullet.draw(self.screen)
        self.buttons.draw(self.screen)

        # HUD — score chip (compact layout)
        score_bg = pygame.Rect(10, 10, 150, 38)
        pygame.draw.rect(self.screen, (14, 16, 36), score_bg, border_radius=8)
        pygame.draw.rect(self.screen, (40, 44, 80), score_bg, 1, border_radius=8)
        score_lbl = self.tiny_font.render("SCORE", True, (80, 90, 140))
        self.screen.blit(score_lbl, (20, 20))
        
        score_val = render_retro_score(self.score, WHITE, scale=1.8)
        self.screen.blit(score_val, (84, 17))
 
        # HUD — best chip (compact layout)
        pb_bg = pygame.Rect(10, 54, 150, 38)
        pygame.draw.rect(self.screen, (14, 16, 36), pb_bg, border_radius=8)
        pygame.draw.rect(self.screen, (40, 44, 80), pb_bg, 1, border_radius=8)
        pb_lbl = self.tiny_font.render("BEST", True, (100, 80, 10))
        self.screen.blit(pb_lbl, (20, 64))
        
        pb_val = render_retro_score(self.personal_best, GOLD, scale=1.8)
        self.screen.blit(pb_val, (84, 61))

        lives_bg = pygame.Rect(self.screen_width - 190, 58, 170, 38)
        pygame.draw.rect(self.screen, (14, 16, 36), lives_bg, border_radius=8)
        pygame.draw.rect(self.screen, (40, 44, 80), lives_bg, 1, border_radius=8)
        lives_lbl = self.tiny_font.render("LIVES", True, (200, 100, 110))
        self.screen.blit(lives_lbl, (self.screen_width - 180, 68))

        heart_x = self.screen_width - 128
        for i in range(self.max_player_lives):
            heart_color = (255, 80, 90) if i < self.player_lives else (80, 80, 90)
            draw_heart(self.screen, heart_x + i * 24, 66, heart_color, size=14)

        # HUD — right side hints
        ctrl_hint = "← → Move  |  SPACE Shoot" if self.profile_control == "arrows" else "A D Move  |  SPACE Shoot"
        hint_surf = self.tiny_font.render(ctrl_hint, True, (70, 75, 110))
        self.screen.blit(hint_surf, (self.screen_width - hint_surf.get_width() - 12, 14))

        diff_colors = {"easy": (0, 200, 80), "normal": (255, 200, 0), "hard": (255, 60, 60)}
        diff_col  = diff_colors.get(self.profile_difficulty, WHITE)
        diff_surf = self.small_font.render(self.profile_difficulty.upper(), True, diff_col)
        self.screen.blit(diff_surf, (self.screen_width - diff_surf.get_width() - 12, 32))

    # ------------------------------------------------------------------
    # GAME OVER state
    # ------------------------------------------------------------------
    def _update_game_over(self, events):
        cx = self.screen_width // 2

        # Dynamic rects based on leaderboard length (max 5 shown on game over screen)
        lb_count = min(len(self.leaderboard), 5)
        lb_height = max(lb_count, 1) * 34
        view_lb_y = 274 + lb_height + 12
        play_again_y = view_lb_y + 54

        self.view_lb_btn_rect    = pygame.Rect(cx - 120, view_lb_y, 240, 44)
        self.reload_button_rect  = pygame.Rect(cx - 100, play_again_y, 200, 50)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.reload_button_rect.collidepoint(event.pos):
                    # Keep player logged in; only reset gameplay
                    saved_name   = self.player_name
                    saved_best   = self.personal_best
                    saved_color  = self.profile_ship_color
                    saved_ctrl   = self.profile_control
                    saved_diff   = self.profile_difficulty
                    self.reset_game()
                    self.player_name      = saved_name
                    self.personal_best    = saved_best
                    self.profile_ship_color = saved_color
                    self.profile_control   = saved_ctrl
                    self.profile_difficulty = saved_diff
                    self.player.set_color(saved_color)
                    self.spawn_number = DIFFICULTY_SPAWN.get(saved_diff, 5)
                    self.game_state = "name_input"
                    return
                if self.view_lb_btn_rect.collidepoint(event.pos):
                    self.game_state = "leaderboard"
                    return

        self.screen.fill(DARK_BG)
        draw_stars(self.screen, self.stars)

        # Title
        draw_glow_title(self.screen, self.big_font, "GAME OVER", cx, 24, color=(220, 40, 40))

        # Score card (made taller to prevent score text overflow/overlap)
        score_card = pygame.Rect(cx - 160, 96, 320, 96)
        pygame.draw.rect(self.screen, PANEL_BG, score_card, border_radius=16)
        pygame.draw.rect(self.screen, PANEL_BOR, score_card, 2, border_radius=16)

        sc_lbl  = self.tiny_font.render("FINAL SCORE", True, (80, 90, 140))
        self.screen.blit(sc_lbl, (cx - sc_lbl.get_width() // 2, 106))
        
        # Retro pixelated score value
        sc_val = render_retro_score(self.score, WHITE, scale=3.6)
        self.screen.blit(sc_val, (cx - sc_val.get_width() // 2, 130))

        # New best badge (pushed down slightly to keep clean margins)
        new_best_y = 202
        if self.score >= self.personal_best and self.score > 0:
            nb_bg = pygame.Rect(cx - 120, new_best_y - 2, 240, 28)
            pygame.draw.rect(self.screen, (35, 28, 0), nb_bg, border_radius=8)
            pygame.draw.rect(self.screen, (140, 100, 0), nb_bg, 1, border_radius=8)
            nb_surf = self.small_font.render(" New Personal Best!", True, GOLD)
            self.screen.blit(nb_surf, (cx - nb_surf.get_width() // 2, new_best_y))

        # Leaderboard mini-table (repositioned to account for taller score card)
        lb_title = self.small_font.render("TOP SCORES", True, (120, 100, 20))
        self.screen.blit(lb_title, (cx - lb_title.get_width() // 2, 242))
        draw_divider(self.screen, cx, 266, width=360, color=(60, 50, 0))

        y_offset = 274
        if self.leaderboard:
            rank_colors = {1: GOLD, 2: (210, 210, 210), 3: (205, 130, 55)}
            for i, entry in enumerate(self.leaderboard[:5], start=1):
                display_name = clean_username(entry["username"])
                is_me = entry["username"] == self.player_name
                row_col = ACCENT if is_me else (200, 200, 215)
                rk_col  = rank_colors.get(i, row_col)

                if is_me:
                    hi = pygame.Rect(cx - 190, y_offset - 3, 380, 30)
                    hs = pygame.Surface((hi.width, hi.height), pygame.SRCALPHA)
                    hs.fill((0, 200, 80, 22))
                    self.screen.blit(hs, hi.topleft)

                rk_surf  = self.small_font.render(str(i), True, rk_col)
                nm_surf  = self.small_font.render(display_name[:16], True, row_col)
                sc_surf2 = self.font.render(str(entry["score"]), True, row_col)
                self.screen.blit(rk_surf,  (cx - 185, y_offset))
                self.screen.blit(nm_surf,  (cx - 155, y_offset))
                self.screen.blit(sc_surf2, (cx + 80,  y_offset - 2))
                y_offset += 34
        else:
            no_scores = self.small_font.render("No scores yet", True, GRAY)
            self.screen.blit(no_scores, (cx - no_scores.get_width() // 2, y_offset))
            y_offset += 34

        # View full leaderboard
        draw_button(self.screen, self.small_font, self.view_lb_btn_rect,
                    "  Full Leaderboard", primary=False)

        # Play Again
        draw_button(self.screen, self.font, self.reload_button_rect, "PLAY AGAIN", primary=True)

    # ------------------------------------------------------------------
    # Collision detection
    # ------------------------------------------------------------------
    def _take_hit(self):
        if self.player.is_blinking or self.game_state != "playing":
            return

        self.player_lives -= 1
        self.player.is_blinking = True
        self.game_state = "blinking"
        self.state_timer = 0
        self.bullets = []
        self.enemy_bullets = []

    def check_collisions(self):
        player_rect = self.player.get_rect()

        for enemy in self.enemies:
            if enemy.state == "offscreen":
                continue

            enemy_rect = enemy.get_rect()

            if player_rect.colliderect(enemy_rect):
                self._take_hit()
                return

            for bullet in self.bullets[:]:
                if bullet.get_rect().colliderect(enemy_rect):
                    enemy.state = "offscreen"
                    bullet.is_active = False
                    self.score += 1
                    break

        for enemy_bullet in self.enemy_bullets[:]:
            if enemy_bullet.get_rect().colliderect(player_rect):
                enemy_bullet.is_active = False
                self._take_hit()
                return