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
        self.rect = pygame.Rect(TILE_SIZE*2, TILE_SIZE*2, TILE_SIZE-10, TILE_SIZE-10)
        self.speed = 4
        self.hidden = False

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
            pygame.draw.rect(surf, PLAYER, self.rect, border_radius=8)

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
    return walls, bushes

# -------- MAIN --------
def main():
    player = Player()
    monsters = [
        Monster(TILE_SIZE*10, TILE_SIZE*5),
        Monster(TILE_SIZE*15, TILE_SIZE*9)
    ]
    camera = Camera()

    base_surface = pygame.Surface((WIDTH, HEIGHT))
    running = True

    while running:
        clock.tick(60)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        base_surface.fill((0,0,0))
        walls, bushes = draw_map(base_surface)

        player.update(keys, walls)
        player.hidden = any(player.rect.colliderect(b) for b in bushes)

        for m in monsters:
            m.update(walls)
            if m.rect.colliderect(player.rect):
                camera.shake = 10
                camera.zoom = 1.1

        camera.shake = max(0, camera.shake - 1)
        camera.zoom += (1.0 - camera.zoom) * 0.1

        for m in monsters:
            m.draw(base_surface)
        player.draw(base_surface)

        screen.fill((0,0,0))
        camera.apply(base_surface)
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
