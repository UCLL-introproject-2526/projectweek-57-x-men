import pygame
import random
from setting import TILE_SIZE, MONSTER_COLOR

class Monster:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE-10, TILE_SIZE-10)
        self.speed = 2
        self.dir = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        self.timer = random.randint(30, 90)

    def update(self, walls, player):
        if not player.hidden:
            dx = 1 if player.rect.centerx > self.rect.centerx else -1
            dy = 1 if player.rect.centery > self.rect.centery else -1
        else:
            self.timer -= 1
            if self.timer <= 0:
                self.dir = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
                self.timer = random.randint(30, 90)
            dx, dy = self.dir

        self.move(dx*self.speed, dy*self.speed, walls)

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
        pygame.draw.rect(surf, MONSTER_COLOR, self.rect, border_radius=8)
