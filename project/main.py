import pygame
pygame.init()

from core.settings import *
from core.camera import Camera
from entities.player import Player
from entities.monster import Monster
from world.map import draw_map, draw_coins


ROWS = len(MAP)
COLS = len(MAP[0])
WIDTH, HEIGHT = COLS*TILE_SIZE, ROWS*TILE_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

def main():
    def reset_game():
        return Player(), [Monster(400,200), Monster(800,400)], Camera(), False, False

    player, monsters, camera, game_over, win = reset_game()
    base = pygame.Surface((WIDTH, HEIGHT))
    walls, bushes, coins = draw_map(base)
    total_coins = len(coins)

    font = pygame.font.SysFont(None, 36)
    play_again = pygame.Rect(WIDTH//2-100, HEIGHT//2+40, 200, 40)

    running = True
    while running:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.MOUSEBUTTONDOWN and (game_over or win):
                if play_again.collidepoint(e.pos):
                    player, monsters, camera, game_over, win = reset_game()
                    walls, bushes, coins = draw_map(base)
                    total_coins = len(coins)

        keys = pygame.key.get_pressed()
        base.fill((0,0,0))
        walls, bushes, _ = draw_map(base)

        if not game_over and not win:
            player.update(keys, walls)
            player.hidden = any(player.rect.colliderect(b) for b in bushes)

            for coin in coins[:]:
                if player.rect.colliderect(coin):
                    coins.remove(coin)

            for m in monsters:
                m.update(walls, player)
                if m.rect.colliderect(player.rect):
                    player.health -= 0.4
                    camera.shake = 8
                    camera.zoom = 1.1

            if player.health <= 0:
                game_over = True
            if not coins:
                win = True

        camera.shake = max(0, camera.shake - 1)
        camera.zoom += (1-camera.zoom)*0.1

        draw_coins(base, coins)
        for m in monsters:
            m.draw(base)
        player.draw(base)

        screen.fill((0,0,0))
        camera.apply(screen, base)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
