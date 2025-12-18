import pygame
from setting import *
import player  # module
from player import Player
from monster import Monster
from camera import Camera
from map import draw_map

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Brawl Stars Style Maze")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Load images after display is initialized
player.load_assets()
player_obj = Player()

def main():
    def reset_game():
        player_obj = Player()
        monsters = [
            Monster(TILE_SIZE*10, TILE_SIZE*5),
            Monster(TILE_SIZE*20, TILE_SIZE*10)
        ]
        camera = Camera()
        game_over = False
        win = False
        return player_obj, monsters, camera, game_over, win

    player_obj, monsters, camera, game_over, win = reset_game()
    base_surface = pygame.Surface((WIDTH, HEIGHT))
    walls, bushes, coins = draw_map(base_surface)
    total_coins = len(coins)
    play_again_btn = pygame.Rect(WIDTH//2-100, HEIGHT//2+40, 200, 40)

    running = True
    while running:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.MOUSEBUTTONDOWN and (game_over or win):
                if play_again_btn.collidepoint(e.pos):
                    player_obj, monsters, camera, game_over, win = reset_game()
                    walls, bushes, coins = draw_map(base_surface)
                    total_coins = len(coins)

        keys = pygame.key.get_pressed()
        base_surface.fill((0,0,0))

        # Draw map
        for y, row in enumerate(MAP):
            for x, tile in enumerate(row):
                rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(base_surface, FLOOR, rect)
                if tile == '#':
                    pygame.draw.rect(base_surface, WALL, rect)
                elif tile == 'B':
                    base_surface.blit(player.bush_img, rect.topleft)

        if not game_over and not win:
            player_obj.update(keys, walls)
            player_obj.hidden = any(player_obj.rect.colliderect(b) for b in bushes)

            for coin in coins[:]:
                if player_obj.rect.colliderect(coin):
                    coins.remove(coin)

            for m in monsters:
                m.update(walls, player_obj)
                if m.rect.colliderect(player_obj.rect):
                    player_obj.health -= 0.4
                    camera.shake = 8
                    camera.zoom = 1.1

            if player_obj.health <= 0:
                game_over = True
            if len(coins) == 0:
                win = True

        camera.shake = max(0, camera.shake - 1)
        camera.zoom += (1.0 - camera.zoom) * 0.1

        for coin in coins:
            pygame.draw.circle(base_surface, (255,215,0), coin.center, 6)
        for m in monsters:
            m.draw(base_surface)
        player_obj.draw(base_surface)

        # UI
        pygame.draw.rect(base_surface, (200,0,0), (20,20,200,16))
        pygame.draw.rect(base_surface, (0,200,0), (20,20,2*player_obj.health,16))
        base_surface.blit(font.render(f"Coins: {total_coins-len(coins)}/{total_coins}", True, (255,255,255)), (20,45))

        if game_over or win:
            msg = "GAME OVER" if game_over else "YOU WIN!"
            base_surface.blit(font.render(msg, True, (255,255,0)), (WIDTH//2-80, HEIGHT//2-40))
            pygame.draw.rect(base_surface, (50,150,50), play_again_btn, border_radius=8)
            base_surface.blit(font.render("PLAY AGAIN", True, (255,255,255)),
                              (play_again_btn.x+30, play_again_btn.y+8))

        screen.fill((0,0,0))
        camera.apply(base_surface)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
