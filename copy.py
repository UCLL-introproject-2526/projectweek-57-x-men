import pygame
import random
import os
import sys

# ---------------- INIT ----------------
pygame.init()
pygame.mixer.init()

TILE_SIZE = 40
FPS = 60

MAP = [
    "############################",
    "#......##....##....##......#",
    "#.####..##..##..####..####..#",
    "#..BB...........BB......B..#",
    "#..BB..#..###..BB..######..#",
    "#......#....#......#.......#",
    "#####..................#####",
    "#...........#......#.......#",
    "#..BB....####..BB......BB..#",
    "#..BB...........BB......BB.#",
    "#.####..##..##..####..##..##",     
    "#......##....##....##......#",
    "#..BB......BB......BB......#",
    "#......#....#......#.....#.#",
    "############################",
]

ROWS = len(MAP)
COLS = len(MAP[0])
WIDTH = COLS * TILE_SIZE
HEIGHT = ROWS * TILE_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Brawl Stars Maze")
clock = pygame.time.Clock()

# ---------------- COLORS ----------------
FLOOR = (35, 30, 25)
WALL = (80, 60, 50)

# ---------------- ASSETS ----------------
player_img = pygame.transform.scale(
    pygame.image.load("img/player.gif").convert_alpha(),
    (TILE_SIZE - 10, TILE_SIZE - 10)
)

bush_img = pygame.transform.scale(
    pygame.image.load("img/bush.png").convert_alpha(),
    (TILE_SIZE, TILE_SIZE)
)

monster_img = pygame.transform.scale(
    pygame.image.load("img/ghost1.png").convert_alpha(),
    (TILE_SIZE - 10, TILE_SIZE - 10)
)

coin_img = pygame.transform.scale(
    pygame.image.load("img/coin.gif").convert_alpha(),
    (16, 16)
)

end_sound = pygame.mixer.Sound("video/end.wav")

# ---------------- CAMERA ----------------
class Camera:
    def __init__(self):
        self.shake = 0
        self.zoom = 1.0

    def apply(self, surface):
        w, h = surface.get_size()
        scaled = pygame.transform.scale(surface, (int(w*self.zoom), int(h*self.zoom)))
        ox = random.randint(-self.shake, self.shake)
        oy = random.randint(-self.shake, self.shake)
        screen.blit(scaled, (ox, oy))

# ---------------- PLAYER ----------------
class Player:
    def __init__(self, start_x, start_y): # Add parameters here
        self.image = player_img
        self.rect = self.image.get_rect(topleft=(start_x, start_y))
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
        if self.hidden:
            img = self.image.copy()
            img.set_alpha(120)
            surf.blit(img, self.rect)
        else:
            surf.blit(self.image, self.rect)

# ---------------- MONSTER ----------------
class Monster:
    def __init__(self, x, y):
        self.image = monster_img
        self.rect = self.image.get_rect(topleft=(x, y))
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
        surf.blit(self.image, self.rect)

# ---------------- MAP ----------------
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
                surf.blit(bush_img, rect.topleft)
                bushes.append(rect)
            elif tile == '.' and random.random() < 0.04:
                coins.append(pygame.Rect(rect.centerx-6, rect.centery-6, 12, 12))
    return walls, bushes, coins

# ---------------- END VIDEO ----------------
def play_end_animation():
    frames = []
    folder = "video/end_frames"

    for f in sorted(os.listdir(folder)):
        img = pygame.image.load(os.path.join(folder, f)).convert()
        img = pygame.transform.scale(img, (WIDTH, HEIGHT))
        frames.append(img)

    end_sound.play()

    for frame in frames:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.blit(frame, (0, 0))
        pygame.display.flip()
        clock.tick(24)

    end_sound.stop()

# ---------------- MAIN ----------------
def main():
    player = Player()
    monsters = [
        Monster(TILE_SIZE*10, TILE_SIZE*5),
        Monster(TILE_SIZE*20, TILE_SIZE*10)
    ]
    camera = Camera()

    base_surface = pygame.Surface((WIDTH, HEIGHT))
    walls, bushes, coins = draw_map(base_surface)
    total_coins = len(coins)

    font = pygame.font.SysFont(None, 32)
    game_over = False
    win = False

    running = True
    while running:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        base_surface.fill((0,0,0))
        walls, bushes, _ = draw_map(base_surface)

        if not game_over and not win:
            player.update(keys, walls)
            player.hidden = any(player.rect.colliderect(b) for b in bushes)

            for coin in coins[:]:
                if player.rect.colliderect(coin):
                    coins.remove(coin)

            for m in monsters:
                m.update(walls, player)
                if m.rect.colliderect(player.rect):
                    player.health -= 0.5
                    camera.shake = 6
                    camera.zoom = 1.1

            if player.health <= 0 and not game_over:
                play_end_animation()
                game_over = True

            if len(coins) == 0:
                win = True

        camera.shake = max(0, camera.shake - 1)
        camera.zoom += (1.0 - camera.zoom) * 0.1

        for coin in coins:
            base_surface.blit(coin_img, coin.topleft)

        for m in monsters:
            m.draw(base_surface)
        player.draw(base_surface)

        pygame.draw.rect(base_surface, (200,0,0), (20,20,200,16))
        pygame.draw.rect(base_surface, (0,200,0), (20,20,2*player.health,16))

        screen.fill((0,0,0))
        camera.apply(base_surface)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
