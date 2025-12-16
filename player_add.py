# BRAWL STARS STYLE MAZE (TOP-DOWN)
# ---------------------------------
# Features added:
# - Bushes hide the player
# - 2 roaming monsters (random movement)
# - Camera zoom + shake on collision
# ---------------------------------

import pygame
import random

pygame.init()

# -------- SETTINGS --------
TILE_SIZE = 40
MAP = [
    "####################",
    "#......##....##....#",
    "#.####..##..##..####.#",
    "#..BB...........BB..#",
    "#..BB..######..BB...#",
    "#......#....#......#",
    "#######.#.##.#.#######",
    "#......#....#......#",
    "#..BB..######..BB...#",
    "#..BB...........BB..#",
    "#.####..##..##..####.#",
    "#......##....##....#",
    "####################",
]

ROWS = len(MAP)
COLS = len(MAP[0])
WIDTH = COLS * TILE_SIZE
HEIGHT = ROWS * TILE_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Brawl Stars Style Maze")
clock = pygame.time.Clock()

# -------- COLORS --------
FLOOR = (220, 200, 160)
WALL = (120, 90, 60)
BUSH = (50, 160, 90)
PLAYER = (80, 140, 255)
MONSTER = (200, 80, 80)

# -------- CAMERA --------
class Camera:
    def __init__(self):
        self.shake = 0
        self.zoom = 1.0

    def apply(self, surface):
        w, h = surface.get_size()
        scaled = pygame.transform.scale(surface, (int(w*self.zoom), int(h*self.zoom)))
        offset_x = random.randint(-self.shake, self.shake)
        offset_y = random.randint(-self.shake, self.shake)
        screen.blit(scaled, (offset_x, offset_y))

# -------- PLAYER --------
class Player:
    def __init__(self):
        self.image = pygame.image.load("img/player.jpeg").convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE-10, TILE_SIZE-10))
        self.rect = self.image.get_rect(topleft=(TILE_SIZE*2, TILE_SIZE*2))
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
                if dx > 0: self.rect.right = w.left
                if dx < 0: self.rect.left = w.right
        self.rect.y += dy
        for w in walls:
            if self.rect.colliderect(w):
                if dy > 0: self.rect.bottom = w.top
                if dy < 0: self.rect.top = w.bottom

    def draw(self, surf):
        if not self.hidden:
            surf.blit(self.image, self.rect)

# -------- MONSTER --------
class Monster:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE-10, TILE_SIZE-10)
        self.dir = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        self.timer = random.randint(30, 90)
        self.speed = 2

    def update(self, walls):
        self.timer -= 1
        if self.timer <= 0:
            self.dir = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
            self.timer = random.randint(30, 90)

        dx = self.dir[0] * self.speed
        dy = self.dir[1] * self.speed
        self.move(dx, dy, walls)

    def move(self, dx, dy, walls):
        self.rect.x += dx
        for w in walls:
            if self.rect.colliderect(w):
                self.rect.x -= dx
                self.dir = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        self.rect.y += dy
        for w in walls:
            if self.rect.colliderect(w):
                self.rect.y -= dy
                self.dir = random.choice([(1,0),(-1,0),(0,1),(0,-1)])

    def draw(self, surf):
        pygame.draw.rect(surf, MONSTER, self.rect, border_radius=8)

# -------- MAP --------
def draw_map(surf):
    walls = []
    bushes = []
    coins = []
    for y, row in enumerate(MAP):
        for x, tile in enumerate(row):
            rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surf, FLOOR, rect)
            if tile == '#':
                pygame.draw.rect(surf, WALL, rect, border_radius=6)
                walls.append(rect)
            if tile == 'B':
                pygame.draw.rect(surf, BUSH, rect.inflate(-6, -6), border_radius=10)
                bushes.append(rect)
            if tile == '.':
                if random.random() < 0.05:
                    coin = pygame.Rect(rect.centerx-6, rect.centery-6, 12, 12)
                    coins.append(coin)
    return walls, bushes, coins

# -------- MAIN --------
def main():
    player = Player()
    monsters = [
        Monster(TILE_SIZE*10, TILE_SIZE*5),
        Monster(TILE_SIZE*15, TILE_SIZE*9)
    ]
    camera = Camera()

    base_surface = pygame.Surface((WIDTH, HEIGHT))
    walls, bushes, coins = draw_map(base_surface)
    total_coins = len(coins)
    font = pygame.font.SysFont(None, 32)

    running = True
    while running:
        clock.tick(60)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        base_surface.fill((0,0,0))
        walls, bushes, _ = draw_map(base_surface)

        player.update(keys, walls)
        player.hidden = any(player.rect.colliderect(b) for b in bushes)

        for coin in coins[:]:
            if player.rect.colliderect(coin):
                coins.remove(coin)

        for m in monsters:
            m.update(walls)
            if m.rect.colliderect(player.rect):
                player.health -= 0.5
                camera.shake = 10
                camera.zoom = 1.1

        camera.shake = max(0, camera.shake - 1)
        camera.zoom += (1.0 - camera.zoom) * 0.1

        for coin in coins:
            pygame.draw.circle(base_surface, (255, 215, 0), coin.center, 6)

        for m in monsters:
            m.draw(base_surface)
        player.draw(base_surface)

        # UI
        pygame.draw.rect(base_surface, (200,0,0), (20, 20, 200, 16))
        pygame.draw.rect(base_surface, (0,200,0), (20, 20, 2*player.health, 16))
        text = font.render(f"Coins: {total_coins-len(coins)}/{total_coins}", True, (255,255,255))
        base_surface.blit(text, (20, 45))

        if len(coins) == 0:
            win = font.render("YOU WIN!", True, (255,255,0))
            base_surface.blit(win, (WIDTH//2-60, HEIGHT//2))

        if player.health <= 0:
            over = font.render("GAME OVER", True, (255,50,50))
            base_surface.blit(over, (WIDTH//2-80, HEIGHT//2))

        screen.fill((0,0,0))
        camera.apply(base_surface)
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
