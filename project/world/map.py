import pygame
import random
from core.settings import MAP, TILE_SIZE, FLOOR, WALL
from assets.images import bush_img, coin_img

def draw_map(surface):
    walls, bushes, coins = [], [], []

    for y, row in enumerate(MAP):
        for x, tile in enumerate(row):
            rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, FLOOR, rect)

            if tile == "#":
                pygame.draw.rect(surface, WALL, rect)
                walls.append(rect)
            elif tile == "B":
                surface.blit(bush_img, rect.topleft)
                bushes.append(rect)
            elif tile == "." and random.random() < 0.04:
                coins.append(pygame.Rect(rect.centerx-8, rect.centery-8, 16, 16))

    return walls, bushes, coins

def draw_coins(surface, coins):
    for coin in coins:
        surface.blit(coin_img, coin.topleft)
