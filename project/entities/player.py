import pygame
from assets.images import player_img

class Player:
    def __init__(self):
        self.image = player_img
        self.rect = self.image.get_rect(topleft=(80, 80))
        self.speed = 4
        self.hidden = False
        self.health = 100

    def update(self, keys, walls):
        dx = dy = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += self.speed
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy += self.speed
        self.move(dx, dy, walls)

    def move(self, dx, dy, walls):
        self.rect.x += dx
        for w in walls:
            if self.rect.colliderect(w):
                self.rect.x -= dx
        self.rect.y += dy
        for w in walls:
            if self.rect.colliderect(w):
                self.rect.y -= dy

    def draw(self, surf):
        img = self.image.copy()
        if self.hidden:
            img.set_alpha(120)
        surf.blit(img, self.rect)
