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

DARK_BG   = (6,  6,  18)
ACCENT    = (0,  220, 100)
WHITE     = (255, 255, 255)
GRAY      = (140, 140, 155)
DARK_BTN  = (25, 28, 52)
SEL_BTN   = (0,  160, 72)
SEL_BTN_H = (0,  200, 90)          # lighter shade for top of button
RED_ERR   = (255, 80,  80)
GOLD      = (255, 215, 0)
PANEL_BG  = (12, 14, 32)
PANEL_BOR = (38, 42, 78)
FIELD_BG  = (18, 20, 42)
ACCENT_DIM = (0, 120, 55)          # subtle glow colour


def draw_option_row(screen, font, label, options, selected, y, x_start, item_w=120, item_h=40):
    """Draw a labeled row of selectable option buttons. Returns list of (rect, option) tuples."""
    label_surf = font.render(label, True, WHITE)
    screen.blit(label_surf, (x_start, y + 8))

    rects = []
    btn_x = x_start + 180
    for opt in options:
        rect = pygame.Rect(btn_x, y, item_w, item_h)
        color = SEL_BTN if opt == selected else DARK_BTN
        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, ACCENT if opt == selected else GRAY, rect, 2, border_radius=8)

        if label == "Ship Color:":
            pygame.draw.circle(screen, SHIP_COLOR_RGB.get(opt, WHITE),
                               (btn_x + item_w // 2, y + item_h // 2), 12)
            pygame.draw.circle(screen, WHITE if opt == selected else GRAY,
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
        alpha  = 40 // i
        glow_rect = rect.inflate(expand * 2, expand * 2)
        s = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (*color, alpha), s.get_rect(), border_radius=radius + expand)
        screen.blit(s, glow_rect.topleft)


def draw_text_field(screen, font, rect, text, placeholder, focused, masked=False, label=None, label_font=None):
    """Draw a styled input field with optional floating label above it."""
    border_color = ACCENT if focused else (55, 60, 95)
    bg_color     = (22, 26, 52) if focused else FIELD_BG

    # Glow on focus
    if focused:
        draw_glow_rect(screen, rect, ACCENT, radius=10, layers=2)

    pygame.draw.rect(screen, bg_color,     rect, border_radius=10)
    pygame.draw.rect(screen, border_color, rect, 2, border_radius=10)

    display = ("●" * len(text)) if masked else text
    if display:
        surf = font.render(display, True, WHITE)
    else:
        surf = font.render(placeholder, True, (70, 75, 105))

    screen.blit(surf, (rect.x + 14, rect.y + (rect.height - surf.get_height()) // 2))

    # Blinking cursor when focused
    if focused and (pygame.time.get_ticks() // 530) % 2 == 0:
        cx_pos = rect.x + 14 + (surf.get_width() if display else 0) + 2
        pygame.draw.line(screen, ACCENT,
                         (cx_pos, rect.y + 10),
                         (cx_pos, rect.bottom - 10), 2)

    # Floating label badge above the field
    if label and label_font and focused:
        lbl_surf = label_font.render(label, True, ACCENT)
        lx = rect.x + 10
        ly = rect.y - lbl_surf.get_height() - 4
        screen.blit(lbl_surf, (lx, ly))


def draw_button(screen, font, rect, text, primary=True):
    """Draw a polished gradient-style button."""
    if primary:
        # Two-tone fill: lighter top half, darker bottom
        top_rect = pygame.Rect(rect.x, rect.y, rect.width, rect.height // 2)
        bot_rect = pygame.Rect(rect.x, rect.y + rect.height // 2, rect.width, rect.height - rect.height // 2)
        pygame.draw.rect(screen, SEL_BTN_H, rect,     border_radius=10)
        pygame.draw.rect(screen, SEL_BTN,   bot_rect, border_radius=0)
        pygame.draw.rect(screen, SEL_BTN,   rect,     border_radius=10)   # re-clip corners
        pygame.draw.rect(screen, (0, 255, 120), rect, 2, border_radius=10)
    else:
        pygame.draw.rect(screen, DARK_BTN, rect, border_radius=10)
        pygame.draw.rect(screen, (55, 60, 95), rect, 2, border_radius=10)

    txt_surf = font.render(text, True, WHITE)
    screen.blit(txt_surf, (rect.centerx - txt_surf.get_width()  // 2,
                            rect.centery - txt_surf.get_height() // 2))


def draw_divider(screen, cx, y, width=340, color=None):
    """Draw a horizontal decorative divider."""
    if color is None:
        color = (40, 44, 80)
    pygame.draw.line(screen, color, (cx - width // 2, y), (cx + width // 2, y), 1)


def draw_glow_title(screen, big_font, text, cx, y, color=ACCENT):
    """Draw title text with a soft colour glow underneath."""
    # Glow layer (slightly offset, low alpha)
    glow = big_font.render(text, True, (*color, 60))
    for dx, dy in [(-2, 2), (2, 2), (0, 3)]:
        gs = pygame.Surface(glow.get_size(), pygame.SRCALPHA)
        gs.blit(glow, (0, 0))
        gs.set_alpha(40)
        screen.blit(gs, (cx - glow.get_width() // 2 + dx, y + dy))
    # Main title
    surf = big_font.render(text, True, color)
    screen.blit(surf, (cx - surf.get_width() // 2, y))


def draw_stars(screen, stars):
    """Draw a simple star-field background."""
    t = pygame.time.get_ticks()
    for i, (x, y, r, brightness) in enumerate(stars):
        # Subtle twinkle: offset brightness by a sine-like pattern
        flicker = int(brightness + 30 * ((t // 800 + i * 37) % 3 - 1) * 0.3)
        flicker = max(40, min(220, flicker))
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


class GameManager:
    def __init__(self, screen, screen_width, screen_height, player_name=""):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.player_name = player_name
        self.db = DBManager(user="root", password="")
        self.leaderboard = []
        self.stars = generate_stars(screen_width, screen_height)

        self.font       = pygame.font.SysFont("Arial", 28)
        self.big_font   = pygame.font.SysFont("Arial", 64)
        self.small_font = pygame.font.SysFont("Arial", 22)
        self.tiny_font  = pygame.font.SysFont("Arial", 18)

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
        field_w = 340
        self.login_user_rect    = pygame.Rect(cx - field_w // 2, 212, field_w, 52)
        self.login_pass_rect    = pygame.Rect(cx - field_w // 2, 294, field_w, 52)
        self.login_btn_rect     = pygame.Rect(cx - field_w // 2, 380, 158, 52)
        self.login_reg_btn_rect = pygame.Rect(cx + field_w // 2 - 158, 380, 158, 52)
        self.login_lb_btn_rect  = pygame.Rect(cx - 100, 450, 200, 42)

        # --- Register screen rects ---
        self.reg_user_rect    = pygame.Rect(cx - field_w // 2, 190, field_w, 52)
        self.reg_pass_rect    = pygame.Rect(cx - field_w // 2, 272, field_w, 52)
        self.reg_conf_rect    = pygame.Rect(cx - field_w // 2, 354, field_w, 52)
        self.reg_create_rect  = pygame.Rect(cx - field_w // 2, 434, 158, 52)
        self.reg_back_rect    = pygame.Rect(cx + field_w // 2 - 158, 434, 158, 52)

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
        self.reset_game()

    # ------------------------------------------------------------------
    # reset_game
    # ------------------------------------------------------------------
    def reset_game(self):
        self.player  = Player(self.screen_width, self.screen_height, self.profile_ship_color)
        self.buttons = MobileButtons()
        self.bullet  = None
        self.enemies = []

        self.score        = 0
        self.personal_best = 0
        self.spawn_number = DIFFICULTY_SPAWN.get(self.profile_difficulty, 5)
        self.game_state   = "login"

        self.old_name     = self.player_name
        self.player_history = []
        self.timer        = 0
        self.state_timer  = 0

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
        for i in range(self.spawn_number):
            self.enemies.append(Enemy(i, self.spawn_number, self.screen_width, self.screen_height))
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
        panel = pygame.Rect(cx - 200, 158, 400, 320)
        pygame.draw.rect(self.screen, PANEL_BG, panel, border_radius=16)
        pygame.draw.rect(self.screen, PANEL_BOR, panel, 2, border_radius=16)

        # Column labels above fields
        lbl_u = self.tiny_font.render("USERNAME", True, (80, 90, 140))
        lbl_p = self.tiny_font.render("PASSWORD", True, (80, 90, 140))
        self.screen.blit(lbl_u, (self.login_user_rect.x + 4,
                                  self.login_user_rect.y - lbl_u.get_height() - 4))
        self.screen.blit(lbl_p, (self.login_pass_rect.x + 4,
                                  self.login_pass_rect.y - lbl_p.get_height() - 4))

        # Fields
        draw_text_field(self.screen, self.font, self.login_user_rect,
                        self.login_username, "Enter username...", self.login_focus == "username")
        draw_text_field(self.screen, self.font, self.login_pass_rect,
                        self.login_password, "Enter password...", self.login_focus == "password", masked=True)

        # Buttons
        draw_button(self.screen, self.font, self.login_btn_rect,     "LOGIN",    primary=True)
        draw_button(self.screen, self.font, self.login_reg_btn_rect, "REGISTER", primary=False)

        # Divider between buttons and leaderboard
        draw_divider(self.screen, cx, 444, width=360, color=(30, 34, 60))

        # Leaderboard link
        draw_button(self.screen, self.small_font, self.login_lb_btn_rect, "  Leaderboard", primary=False)

        # Error message
        if self.login_error:
            err_bg = pygame.Rect(cx - 185, 503, 370, 30)
            pygame.draw.rect(self.screen, (50, 10, 10), err_bg, border_radius=6)
            err = self.small_font.render(self.login_error, True, RED_ERR)
            self.screen.blit(err, (cx - err.get_width() // 2, 508))

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
        panel = pygame.Rect(cx - 200, 145, 400, 320)
        pygame.draw.rect(self.screen, PANEL_BG, panel, border_radius=16)
        pygame.draw.rect(self.screen, PANEL_BOR, panel, 2, border_radius=16)

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
        msg_y = 498
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
        pygame.draw.rect(self.screen, PANEL_BG, table_rect, border_radius=14)
        pygame.draw.rect(self.screen, PANEL_BOR, table_rect, 2, border_radius=14)

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
        pygame.draw.rect(self.screen, PANEL_BG, card, border_radius=16)
        pygame.draw.rect(self.screen, PANEL_BOR, card, 2, border_radius=16)

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
            keyboard_fired = any(
                e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE
                for e in events
            )

            if (screen_button_fired or keyboard_fired) and self.bullet is None:
                bullet_x = self.player.x + self.player.width // 2 - 16
                self.bullet = Bullet(bullet_x, self.player.y)

            self.player.keep_inside_screen()

            if self.bullet:
                self.bullet.update()
                if not self.bullet.is_active:
                    self.bullet = None

            self.timer += 1
            if self.timer >= 180:
                waiting = [e for e in self.enemies if e.state == "waiting"]
                if waiting:
                    chosen = random.choice(waiting)
                    tx, ty = self.player_history[-1] if self.player_history else (self.player.x, self.player.y)
                    chosen.start_drop(tx, ty)
                    self.timer = 0

            all_despawned = all(e.state == "offscreen" for e in self.enemies)
            for enemy in self.enemies:
                enemy.update()

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
                # Save score live to DB immediately
                self.db.save_score(self.player_name, self.score)
                # Update personal best if beaten
                if self.score > self.personal_best:
                    self.personal_best = self.score
                # Refresh leaderboard
                self.leaderboard = self.db.get_top_scores(limit=10)
                self.game_state = "game_over"

        # --- Draw playing / blinking ---
        self.screen.fill(DARK_BG)
        draw_stars(self.screen, self.stars)

        self.player.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        if self.bullet:
            self.bullet.draw(self.screen)
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
    def check_collisions(self):
        player_rect = self.player.get_rect()

        for enemy in self.enemies:
            if enemy.state == "offscreen":
                continue

            enemy_rect = enemy.get_rect()

            if player_rect.colliderect(enemy_rect):
                self.game_state   = "blinking"
                self.player.is_blinking = True
                self.state_timer  = 0
                return

            if self.bullet and self.bullet.get_rect().colliderect(enemy_rect):
                enemy.state  = "offscreen"
                self.bullet  = None
                self.score  += 1
                break