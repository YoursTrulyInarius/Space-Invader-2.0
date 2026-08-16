import pygame
import random
from entities.player import Player
from entities.button import MobileButtons
from entities.enemy import Enemy
from entities.bullet import Bullet

class GameManager:
    def __init__(self, screen, screen_width, screen_height):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.SysFont("Arial", 36)
        self.big_font = pygame.font.SysFont("Arial", 64)
        self.reload_button_rect = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 50, 200, 50)
        self.reset_game()

    def reset_game(self):
        self.player = Player(self.screen_width, self.screen_height)
        self.buttons = MobileButtons()
        self.bullet = None
        self.enemies = []

        self.score = 0
        self.spawn_number = 5
        self.game_state = "playing"

        self.player_history = []
        self.timer = 0
        self.state_timer = 0
        self.spawn_enemies()

    def spawn_enemies(self):
        self.enemies = []
        for i in range(self.spawn_number):
            self.enemies.append(Enemy(i, self.spawn_number, self.screen_width))
        self.timer = 0

    def update(self, events):
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
            self.screen.blit(go_text, (self.screen_width // 2 - go_text.get_width() // 2, self.screen_height // 2 - 120))

            final_score_text = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(final_score_text, (self.screen_width // 2 - final_score_text.get_width() // 2, self.screen_height // 2 - 20))

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