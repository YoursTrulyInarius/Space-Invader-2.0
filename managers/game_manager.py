import pygame
import random
from entities.player import Player
from entities.button import MobileButtons
from entities.enemy import Enemy
from entities.bullet import Bullet
from managers.db_manager import DBManager

class GameManager:
    def __init__(self, screen, screen_width, screen_height, player_name=""):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.player_name = player_name
        self.db = DBManager(user="root", password="")
        self.leaderboard = []
        self.font = pygame.font.SysFont("Arial", 36)
        self.big_font = pygame.font.SysFont("Arial", 64)
        self.reload_button_rect = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 50, 200, 50)
        self.name_input_rect = pygame.Rect(screen_width // 2 - 150, screen_height // 2, 300, 50)
        self.start_button_rect = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 80, 200, 50)
        self.rename_button_rect = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 140, 200, 50)
        self.old_name = ""
        self.reset_game(first_run=True)

    def reset_game(self, first_run=False):
        self.player = Player(self.screen_width, self.screen_height)
        self.buttons = MobileButtons()
        self.bullet = None
        self.enemies = []

        self.score = 0
        self.spawn_number = 5
        self.game_state = "name_input" if first_run else "playing"

        self.player_history = []
        self.timer = 0
        self.state_timer = 0
        if self.game_state != "name_input":
            self.spawn_enemies()

    def spawn_enemies(self):
        self.enemies = []
        for i in range(self.spawn_number):
            self.enemies.append(Enemy(i, self.spawn_number, self.screen_width))
        self.timer = 0

    def update(self, events):
        if self.game_state == "name_input":
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    elif event.key == pygame.K_RETURN:
                        if self.player_name.strip() == "":
                            self.player_name = "Guest"
                        self.game_state = "playing"
                        self.spawn_enemies()
                    else:
                        if len(self.player_name) < 15:
                            self.player_name += event.unicode
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.start_button_rect.collidepoint(event.pos):
                        if self.player_name.strip() == "":
                            self.player_name = "Guest"
                        self.game_state = "playing"
                        self.spawn_enemies()
                    elif self.rename_button_rect.collidepoint(event.pos):
                        if self.player_name.strip() != "":
                            self.old_name = self.player_name
                            self.player_name = ""
                            self.game_state = "rename_input"
            
            self.screen.fill((0, 0, 0))
            title_text = self.big_font.render("Space Invaders", True, (0, 255, 0))
            self.screen.blit(title_text, (self.screen_width // 2 - title_text.get_width() // 2, self.screen_height // 2 - 150))
            
            prompt_text = self.font.render("Enter your name:", True, (255, 255, 255))
            self.screen.blit(prompt_text, (self.screen_width // 2 - prompt_text.get_width() // 2, self.screen_height // 2 - 50))
            
            pygame.draw.rect(self.screen, (255, 255, 255), self.name_input_rect, 2)
            name_text = self.font.render(self.player_name, True, (255, 255, 255))
            self.screen.blit(name_text, (self.name_input_rect.x + 10, self.name_input_rect.y + 5))
            
            pygame.draw.rect(self.screen, (50, 150, 50), self.start_button_rect)
            start_btn_text = self.font.render("START", True, (255, 255, 255))
            self.screen.blit(start_btn_text, (self.start_button_rect.x + (self.start_button_rect.width - start_btn_text.get_width()) // 2, self.start_button_rect.y + (self.start_button_rect.height - start_btn_text.get_height()) // 2))
            
            pygame.draw.rect(self.screen, (150, 150, 50), self.rename_button_rect)
            rename_btn_text = self.font.render("RENAME", True, (255, 255, 255))
            self.screen.blit(rename_btn_text, (self.rename_button_rect.x + (self.rename_button_rect.width - rename_btn_text.get_width()) // 2, self.rename_button_rect.y + (self.rename_button_rect.height - rename_btn_text.get_height()) // 2))
            
            return

        if self.game_state == "rename_input":
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    elif event.key == pygame.K_RETURN:
                        if self.player_name.strip() != "":
                            self.db.update_player_username(self.old_name, self.player_name.strip())
                        self.game_state = "name_input"
                        self.player_name = self.player_name.strip()
                    else:
                        if len(self.player_name) < 15:
                            self.player_name += event.unicode
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.start_button_rect.collidepoint(event.pos):
                        if self.player_name.strip() != "":
                            self.db.update_player_username(self.old_name, self.player_name.strip())
                        self.game_state = "name_input"
                        self.player_name = self.player_name.strip()
            
            self.screen.fill((0, 0, 0))
            title_text = self.big_font.render("Rename Profile", True, (0, 255, 0))
            self.screen.blit(title_text, (self.screen_width // 2 - title_text.get_width() // 2, self.screen_height // 2 - 150))
            
            prompt_text = self.font.render(f"New name for {self.old_name}:", True, (255, 255, 255))
            self.screen.blit(prompt_text, (self.screen_width // 2 - prompt_text.get_width() // 2, self.screen_height // 2 - 50))
            
            pygame.draw.rect(self.screen, (255, 255, 255), self.name_input_rect, 2)
            name_text = self.font.render(self.player_name, True, (255, 255, 255))
            self.screen.blit(name_text, (self.name_input_rect.x + 10, self.name_input_rect.y + 5))
            
            pygame.draw.rect(self.screen, (50, 150, 150), self.start_button_rect)
            update_btn_text = self.font.render("UPDATE", True, (255, 255, 255))
            self.screen.blit(update_btn_text, (self.start_button_rect.x + (self.start_button_rect.width - update_btn_text.get_width()) // 2, self.start_button_rect.y + (self.start_button_rect.height - update_btn_text.get_height()) // 2))
            
            return

        if self.game_state == "playing" or self.game_state == "blinking":
            self.player_history.append((self.player.x, self.player.y))
            if len(self.player_history) > 60:
                self.player_history.pop(0)

        if self.game_state == "playing":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.player.move_left()
            if keys[pygame.K_RIGHT]:
                self.player.move_right()

            screen_button_fired = self.buttons.handle_mouse(self.player, events)
            
            keyboard_fired = False
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    keyboard_fired = True

            if (screen_button_fired or keyboard_fired) and self.bullet is None:
                self.bullet = Bullet(self.player.x + self.player.width // 2 - 16, self.player.y)

            self.player.keep_inside_screen()

            if self.bullet:
                self.bullet.update()
                if not self.bullet.is_active:
                    self.bullet = None

            self.timer += 1

            if self.timer >= 180:
                waiting_enemies = [e for e in self.enemies if e.state == "waiting"]
                if waiting_enemies:
                    chosen_enemy = random.choice(waiting_enemies)
                    target_x, target_y = self.player_history[0]
                    chosen_enemy.start_drop(target_x, target_y)
                    self.timer = 0

            all_despawned = True
            for enemy in self.enemies:
                enemy.update()
                if enemy.state != "offscreen":
                    all_despawned = False

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

        elif self.game_state == "game_over":
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.reload_button_rect.collidepoint(event.pos):
                        self.reset_game()

        self.screen.fill((0, 0, 0))

        if self.game_state != "game_over":
            self.player.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)
            if self.bullet:
                self.bullet.draw(self.screen)
            self.buttons.draw(self.screen)

        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (20, 20))

        if self.game_state == "game_over":
            go_text = self.big_font.render("GAME OVER", True, (255, 50, 50))
            self.screen.blit(go_text, (self.screen_width // 2 - go_text.get_width() // 2, 50))

            final_score_text = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(final_score_text, (self.screen_width // 2 - final_score_text.get_width() // 2, 130))

            lb_title_text = self.font.render("Leaderboard", True, (255, 255, 0))
            self.screen.blit(lb_title_text, (self.screen_width // 2 - lb_title_text.get_width() // 2, 180))
            
            y_offset = 230
            if self.leaderboard:
                for i, entry in enumerate(self.leaderboard):
                    lb_text = self.font.render(f"{i+1}. {entry['username']} - {entry['score']}", True, (200, 200, 200))
                    self.screen.blit(lb_text, (self.screen_width // 2 - lb_text.get_width() // 2, y_offset))
                    y_offset += 40
            else:
                lb_text = self.font.render("No scores available", True, (200, 200, 200))
                self.screen.blit(lb_text, (self.screen_width // 2 - lb_text.get_width() // 2, y_offset))
                y_offset += 40

            self.reload_button_rect.y = y_offset + 30
            pygame.draw.rect(self.screen, (50, 150, 50), self.reload_button_rect)
            btn_text = self.font.render("RELOAD", True, (255, 255, 255))
            self.screen.blit(btn_text, (self.reload_button_rect.x + (self.reload_button_rect.width - btn_text.get_width()) // 2, self.reload_button_rect.y + (self.reload_button_rect.height - btn_text.get_height()) // 2))

    def check_collisions(self):
        player_rect = self.player.get_rect()

        for enemy in self.enemies:
            if enemy.state == "offscreen":
                continue

            enemy_rect = enemy.get_rect()

            if player_rect.colliderect(enemy_rect):
                self.game_state = "blinking"
                self.player.is_blinking = True
                self.state_timer = 0
                return

            if self.bullet and self.bullet.get_rect().colliderect(enemy_rect):
                enemy.state = "offscreen"
                self.bullet = None
                self.score += 1
                break