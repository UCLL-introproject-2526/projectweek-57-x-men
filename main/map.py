# map.py
import pygame
from setting import TILE_SIZE, MAP, FLOOR, WALL
import random
import player  # import the module where bush_img is defined

def draw_map(surf):
    walls, bushes, coins = [], [], []

    for y, row in enumerate(MAP):
        for x, tile in enumerate(row):
            rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surf, FLOOR, rect)

            if tile == '#':
                pygame.draw.rect(surf, WALL, rect)
                walls.append(rect)
            elif tile == 'B':
                if player.bush_img is not None:
                    surf.blit(player.bush_img, rect.topleft)
                bushes.append(rect)
            elif tile == '.' and random.random() < 0.04:
                coins.append(pygame.Rect(rect.centerx-6, rect.centery-6, 12, 12))

    return walls, bushes, coins
