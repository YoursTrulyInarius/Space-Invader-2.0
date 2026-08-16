import pygame

class MobileButtons:
    def __init__(self):
        self.left = pygame.Rect(20, 520, 80, 60)
        self.right = pygame.Rect(120, 520, 80, 60)
        self.fire = pygame.Rect(680, 520, 100, 60)

    def draw(self, screen):
        pygame.draw.rect(screen, (80, 80, 80), self.left)
        pygame.draw.rect(screen, (80, 80, 80), self.right)
        pygame.draw.rect(screen, (200, 50, 50), self.fire)

    def handle_mouse(self, player, events):
       
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0]:
            mouse_pos = pygame.mouse.get_pos()
            if self.left.collidepoint(mouse_pos):
                player.move_left()
            if self.right.collidepoint(mouse_pos):
                player.move_right()

        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.fire.collidepoint(event.pos):
                    return True
        return False
