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
    "green":  (0, 220, 0),
    "blue":   (0, 150, 255),
    "red":    (255, 50, 50),
    "yellow": (255, 220, 0),
    "purple": (180, 0, 255),
}
CONTROL_SCHEMES = ["arrows", "wasd"]
DIFFICULTIES    = ["easy", "normal", "hard"]
DIFFICULTY_LABELS = {"easy": "Easy", "normal": "Normal", "hard": "Hard"}

# Difficulty multipliers (enemy spawn count modifier)
DIFFICULTY_SPAWN = {"easy": 3, "normal": 5, "hard": 8}

DARK_BG  = (8, 8, 20)
ACCENT   = (0, 220, 100)
WHITE    = (255, 255, 255)
GRAY     = (150, 150, 160)
DARK_BTN = (30, 30, 50)
SEL_BTN  = (0, 180, 80)


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

        # For ship colors show a colored swatch, otherwise show text
        if label == "Ship Color:":
            swatch = pygame.Rect(btn_x + item_w // 2 - 10, y + item_h // 2 - 10, 20, 20)
            pygame.draw.circle(screen, SHIP_COLOR_RGB.get(opt, WHITE),
                               (btn_x + item_w // 2, y + item_h // 2), 12)
            pygame.draw.circle(screen, WHITE if opt == selected else GRAY,
                               (btn_x + item_w // 2, y + item_h // 2), 12, 2)
        else:
            disp = opt.upper() if label == "Controls:" else DIFFICULTY_LABELS.get(opt, opt.capitalize())
            txt = font.render(disp, True, WHITE)
            screen.blit(txt, (btn_x + (item_w - txt.get_width()) // 2, y + (item_h - txt.get_height()) // 2))

        rects.append((rect, opt))
        btn_x += item_w + 10
    return rects


class GameManager:
    def __init__(self, screen, screen_width, screen_height, player_name=""):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.player_name = player_name
        self.db = DBManager(user="root", password="")
        self.leaderboard = []

        self.font      = pygame.font.SysFont("Arial", 28)
        self.big_font  = pygame.font.SysFont("Arial", 64)
        self.small_font = pygame.font.SysFont("Arial", 22)

        # --- Name input screen rects ---
        self.name_input_rect   = pygame.Rect(screen_width // 2 - 150, screen_height // 2, 300, 50)
        self.start_button_rect = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 80, 200, 50)
        self.profile_btn_rect  = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 145, 200, 40)

        # --- Reload rect (game over) ---
        self.reload_button_rect = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 50, 200, 50)

        # --- Profile state ---
        self.profile_ship_color    = "green"
        self.profile_control       = "arrows"
        self.profile_difficulty    = "normal"
        self.profile_back_rect     = pygame.Rect(screen_width // 2 - 100, screen_height - 80, 200, 45)
        self.profile_option_rects  = []   # populated each frame in _draw_profile

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
        self.spawn_number = DIFFICULTY_SPAWN.get(self.profile_difficulty, 5)
        self.game_state   = "name_input"

        self.old_name     = self.player_name
        self.player_history = []
        self.timer        = 0
        self.state_timer  = 0

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
            # Apply color to currently loaded player
            self.player.set_color(self.profile_ship_color)

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

    # ------------------------------------------------------------------
    # spawn_enemies
    # ------------------------------------------------------------------
    def spawn_enemies(self):
        self.enemies = []
        for i in range(self.spawn_number):
            self.enemies.append(Enemy(i, self.spawn_number, self.screen_width))
        self.timer = 0

    # ------------------------------------------------------------------
    # update (main dispatcher)
    # ------------------------------------------------------------------
    def update(self, events):
        if self.game_state == "name_input":
            self._update_name_input(events)
        elif self.game_state == "profile":
            self._update_profile(events)
        elif self.game_state in ("playing", "blinking"):
            self._update_playing(events)
        elif self.game_state == "game_over":
            self._update_game_over(events)

    # ------------------------------------------------------------------
    # NAME INPUT state
    # ------------------------------------------------------------------
    def _update_name_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.player_name = self.player_name[:-1]
                elif event.key == pygame.K_RETURN:
                    self._start_game()
                    return
                elif event.key != pygame.K_TAB and event.unicode.isprintable():
                    if len(self.player_name) < 15:
                        self.player_name += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.start_button_rect.collidepoint(event.pos):
                    self._start_game()
                    return
                if self.profile_btn_rect.collidepoint(event.pos):
                    # Must have a name to open profile
                    self.player_name = self.player_name.strip() or "Guest"
                    self.db.get_or_create_player(self.player_name)
                    self._load_profile_from_db()
                    self.game_state = "profile"
                    return

        # --- Draw name input screen ---
        self.screen.fill(DARK_BG)

        title = self.big_font.render("Space Invaders", True, ACCENT)
        self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2,
                                 self.screen_height // 2 - 160))

        prompt = self.font.render("Enter your name:", True, WHITE)
        self.screen.blit(prompt, (self.screen_width // 2 - prompt.get_width() // 2,
                                  self.screen_height // 2 - 50))

        pygame.draw.rect(self.screen, WHITE, self.name_input_rect, 2, border_radius=6)
        name_surf = self.font.render(self.player_name, True, WHITE)
        self.screen.blit(name_surf, (self.name_input_rect.x + 10,
                                     self.name_input_rect.y + 10))

        # START button
        pygame.draw.rect(self.screen, SEL_BTN, self.start_button_rect, border_radius=8)
        s_txt = self.font.render("START", True, WHITE)
        self.screen.blit(s_txt, (self.start_button_rect.centerx - s_txt.get_width() // 2,
                                 self.start_button_rect.centery - s_txt.get_height() // 2))

        # PROFILE button (smaller, outlined style)
        pygame.draw.rect(self.screen, DARK_BTN, self.profile_btn_rect, border_radius=8)
        pygame.draw.rect(self.screen, ACCENT,   self.profile_btn_rect, 2, border_radius=8)
        p_txt = self.small_font.render("✦  EDIT PROFILE", True, ACCENT)
        self.screen.blit(p_txt, (self.profile_btn_rect.centerx - p_txt.get_width() // 2,
                                 self.profile_btn_rect.centery - p_txt.get_height() // 2))

    # ------------------------------------------------------------------
    # PROFILE state
    # ------------------------------------------------------------------
    def _update_profile(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check all option buttons (populated by _draw_profile)
                for rect, category, value in self.profile_option_rects:
                    if rect.collidepoint(event.pos):
                        if category == "color":
                            self.profile_ship_color = value
                            self.player.set_color(value)
                        elif category == "control":
                            self.profile_control = value
                        elif category == "difficulty":
                            self.profile_difficulty = value
                # Back / Save button
                if self.profile_back_rect.collidepoint(event.pos):
                    self._save_profile_to_db()
                    self.game_state = "name_input"

        self._draw_profile()

    def _draw_profile(self):
        self.screen.fill(DARK_BG)
        self.profile_option_rects = []

        # Title
        title = self.big_font.render("Player Profile", True, ACCENT)
        self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 30))

        # Player name subtitle
        sub = self.font.render(f"Player: {self.player_name}", True, GRAY)
        self.screen.blit(sub, (self.screen_width // 2 - sub.get_width() // 2, 105))

        # --- Ship preview ---
        preview_x = self.screen_width // 2 - 40
        preview_y = 145
        self.screen.blit(self.player.image, (preview_x, preview_y))

        x_start = self.screen_width // 2 - 290
        y = 240

        # --- Ship Color row ---
        rects = draw_option_row(self.screen, self.small_font,
                                "Ship Color:", SHIP_COLORS, self.profile_ship_color,
                                y, x_start, item_w=80)
        self.profile_option_rects += [(r, "color", v) for r, v in rects]
        y += 60

        # --- Control Scheme row ---
        rects = draw_option_row(self.screen, self.small_font,
                                "Controls:", CONTROL_SCHEMES, self.profile_control,
                                y, x_start, item_w=110)
        self.profile_option_rects += [(r, "control", v) for r, v in rects]
        y += 60

        # --- Difficulty row ---
        rects = draw_option_row(self.screen, self.small_font,
                                "Difficulty:", DIFFICULTIES, self.profile_difficulty,
                                y, x_start, item_w=100)
        self.profile_option_rects += [(r, "difficulty", v) for r, v in rects]
        y += 70

        # --- Legend ---
        legend = self.small_font.render("Arrow Keys / WASD — move    SPACE — shoot", True, GRAY)
        self.screen.blit(legend, (self.screen_width // 2 - legend.get_width() // 2, y))

        # --- Save & Back button ---
        pygame.draw.rect(self.screen, SEL_BTN, self.profile_back_rect, border_radius=8)
        back_txt = self.font.render("💾  Save & Back", True, WHITE)
        self.screen.blit(back_txt, (self.profile_back_rect.centerx - back_txt.get_width() // 2,
                                    self.profile_back_rect.centery - back_txt.get_height() // 2))

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

            left_key  = pygame.K_a     if use_wasd else pygame.K_LEFT
            right_key = pygame.K_d     if use_wasd else pygame.K_RIGHT

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
                self.bullet = Bullet(self.player.x + self.player.width // 2 - 16,
                                     self.player.y)

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
                    tx, ty = self.player_history[0]
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
                self.game_state = "game_over"
                self.db.save_score(self.player_name, self.score)
                self.leaderboard = self.db.get_top_scores(limit=5)

        # --- Draw playing / blinking ---
        self.screen.fill(DARK_BG)

        self.player.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        if self.bullet:
            self.bullet.draw(self.screen)
        self.buttons.draw(self.screen)

        score_surf = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_surf, (20, 20))

        # HUD: show current control scheme hint
        ctrl_hint = "← → Move  |  SPACE Shoot" if self.profile_control == "arrows" else "A D Move  |  SPACE Shoot"
        hint_surf = self.small_font.render(ctrl_hint, True, GRAY)
        self.screen.blit(hint_surf, (self.screen_width - hint_surf.get_width() - 15, 20))

        # HUD: difficulty badge
        diff_colors = {"easy": (0, 200, 80), "normal": (255, 200, 0), "hard": (255, 60, 60)}
        diff_surf = self.small_font.render(self.profile_difficulty.upper(), True,
                                           diff_colors.get(self.profile_difficulty, WHITE))
        self.screen.blit(diff_surf, (self.screen_width - diff_surf.get_width() - 15, 45))

    # ------------------------------------------------------------------
    # GAME OVER state
    # ------------------------------------------------------------------
    def _update_game_over(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.reload_button_rect.collidepoint(event.pos):
                    self.reset_game()

        self.screen.fill(DARK_BG)

        go_text = self.big_font.render("GAME OVER", True, (255, 50, 50))
        self.screen.blit(go_text, (self.screen_width // 2 - go_text.get_width() // 2, 50))

        final_surf = self.font.render(f"Final Score: {self.score}", True, WHITE)
        self.screen.blit(final_surf, (self.screen_width // 2 - final_surf.get_width() // 2, 130))

        lb_title = self.font.render("Leaderboard", True, (255, 220, 0))
        self.screen.blit(lb_title, (self.screen_width // 2 - lb_title.get_width() // 2, 175))

        y_offset = 220
        if self.leaderboard:
            for i, entry in enumerate(self.leaderboard):
                color = ACCENT if entry["username"] == self.player_name else (200, 200, 200)
                lb_text = self.font.render(
                    f"{i+1}. {entry['username']}  —  {entry['score']}", True, color)
                self.screen.blit(lb_text, (self.screen_width // 2 - lb_text.get_width() // 2, y_offset))
                y_offset += 38
        else:
            no_scores = self.font.render("No scores yet", True, GRAY)
            self.screen.blit(no_scores, (self.screen_width // 2 - no_scores.get_width() // 2, y_offset))
            y_offset += 38

        self.reload_button_rect.y = y_offset + 20
        pygame.draw.rect(self.screen, SEL_BTN, self.reload_button_rect, border_radius=8)
        btn_txt = self.font.render("PLAY AGAIN", True, WHITE)
        self.screen.blit(btn_txt, (self.reload_button_rect.centerx - btn_txt.get_width() // 2,
                                   self.reload_button_rect.centery - btn_txt.get_height() // 2))

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