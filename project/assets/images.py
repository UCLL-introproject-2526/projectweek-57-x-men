import pygame
from core.settings import TILE_SIZE ,pl

player_img = pygame.transform.scale(
    pygame.image.load("img/player.gif").convert_alpha(),
    (TILE_SIZE-10, TILE_SIZE-10)
)

bush_img = pygame.transform.scale(
    pygame.image.load("img/bush.png").convert_alpha(),
    (TILE_SIZE, TILE_SIZE)
)

monster_img = pygame.transform.scale(
    pygame.image.load("img/ghost1.png").convert_alpha(),
    (TILE_SIZE-10, TILE_SIZE-10)
)

coin_img = pygame.transform.scale(
    pygame.image.load("img/coin.gif").convert_alpha(),
    (16, 16)
)
