import pygame
import random
import math

pygame.init()

# ---------- SETTINGS ----------
TILE_SIZE = 40
FPS = 60

MAP = [
    "############################",
    "#......##....##....##......#",
    "#.####..##..##..####..####.#",
    "#..BB...........BB......B..#",
    "#..BB..#..###..BB..######..#",
    "#......#...........#.......#",
    "#####.......#.........######",
    "#......#....#......#.......#",
    "#..BB..######..BB......BB.##",
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
pygame.display.set_caption("Maze Game with Animated Hearts")
clock = pygame.time.Clock()

# ---------- COLORS ----------
FLOOR = (220, 200, 160)
WALL = (120, 90, 60)
WHITE = (255, 255, 255)
HEART_RED = (200, 40, 40)

# ---------- LOAD IMAGES ----------
monster_img = pygame.transform.scale(
    pygame.image.load("img/ghost1.png").convert_alpha(),
    (TILE_SIZE - 10, TILE_SIZE - 10)
)

bush_img = pygame.transform.scale(
    pygame.image.load("img/bush.png").convert_alpha(),
    (TILE_SIZE, TILE_SIZE)
)

# ---------- HEART DRAWING ----------
def draw_heart(surface, x, y, size, pulse):
    s = int(size * pulse)

    left_circle = (x + s//3, y + s//3)
    right_circle = (x + 2*s//3, y + s//3)
    bottom_point = (x + s//2, y + s)

    pygame.draw.circle(surface, HEART_RED, left_circle, s//3)
    pygame.draw.circle(surface, HEART_RED, right_circle, s//3)
    pygame.draw.polygon(surface, HEART_RED, [
        (x, y + s//3),
        (x + s, y + s//3),
        bottom_point
    ])

# ---------- PLAYER ----------
class Player:
    def __init__(self):
        self.load_frames()
        self.image = self.idle_left[0]
        self.rect = self.image.get_rect(topleft=(TILE_SIZE*2+5, TILE_SIZE*2+5))
        self.hitbox = self.rect.inflate(-12, -12)

        self.speed = 4
        self.health = 5
        self.hidden = False

        self.facing_right = True
        self.frame = 0
        self.last_anim = 0
        self.anim_delay = 150
        self.moving = False

    def load_frames(self):
        self.idle_left = [
            pygame.image.load("img/player_walk_1.png").convert_alpha()
        ]
        self.walk_left = [
            pygame.image.load("img/player_walk_1.png").convert_alpha(),
            pygame.image.load("img/player_walk_2.png").convert_alpha()
        ]
        self.idle_right = [pygame.transform.flip(f, True, False) for f in self.idle_left]
        self.walk_right = [pygame.transform.flip(f, True, False) for f in self.walk_left]

    def update(self, keys, walls):
        dx = dy = 0
        self.moving = False

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= self.speed
            self.facing_right = False
            self.moving = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += self.speed
            self.facing_right = True
            self.moving = True
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= self.speed
            self.moving = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += self.speed
            self.moving = True

        self.move(dx, dy, walls)
        self.animate()

    def move(self, dx, dy, walls):
        self.hitbox.x += dx
        for w in walls:
            if self.hitbox.colliderect(w):
                if dx > 0: self.hitbox.right = w.left
                if dx < 0: self.hitbox.left = w.right

        self.hitbox.y += dy
        for w in walls:
            if self.hitbox.colliderect(w):
                if dy > 0: self.hitbox.bottom = w.top
                if dy < 0: self.hitbox.top = w.bottom

        self.rect.center = self.hitbox.center

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_anim > self.anim_delay:
            self.last_anim = now
            self.frame += 1

        frames = (
            self.walk_right if self.moving and self.facing_right else
            self.walk_left if self.moving else
            self.idle_right if self.facing_right else
            self.idle_left
        )

        self.frame %= len(frames)
        self.image = frames[self.frame]

    def draw(self, surf):
        img = self.image.copy()
        if self.hidden:
            img.set_alpha(120)
        surf.blit(img, self.rect)

# ---------- MONSTER ----------
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

# ---------- MAP ----------
def build_map(surf):
    walls, bushes, coins = [], [], []
    for y, row in enumerate(MAP):
        for x, t in enumerate(row):
            r = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surf, FLOOR, r)
            if t == '#':
                pygame.draw.rect(surf, WALL, r)
                walls.append(r)
            elif t == 'B':
                surf.blit(bush_img, r.topleft)
                bushes.append(r)
            elif t == '.' and random.random() < 0.04:
                coins.append(pygame.Rect(r.centerx-6, r.centery-6, 12, 12))
    return walls, bushes, coins

# ---------- MAIN ----------
def main():
    base = pygame.Surface((WIDTH, HEIGHT))
    font = pygame.font.SysFont(None, 32)

    player = Player()
    monsters = [Monster(400, 200), Monster(700, 400)]
    walls, bushes, coins = build_map(base)
    total_coins = len(coins)

    running = True
    while running:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player.update(keys, walls)
        player.hidden = any(player.rect.colliderect(b) for b in bushes)

        for m in monsters:
            m.update(walls, player)
            if m.rect.colliderect(player.rect):
                player.health -= 1
                player.rect.topleft = (TILE_SIZE*2, TILE_SIZE*2)

        for c in coins[:]:
            if player.rect.colliderect(c):
                coins.remove(c)

        if player.health <= 0:
            running = False

        base.fill((0,0,0))
        build_map(base)
        for c in coins:
            pygame.draw.circle(base, (255,215,0), c.center, 6)
        for m in monsters:
            m.draw(base)
        player.draw(base)

        # ❤️ ANIMATED HEARTS
        time = pygame.time.get_ticks() / 400
        pulse = 1 + 0.1 * math.sin(time)

        for i in range(player.health):
            draw_heart(base, 20 + i*32, 20, 22, pulse)

        base.blit(
            font.render(f"Coins: {total_coins - len(coins)}/{total_coins}", True, WHITE),
            (20, 55)
        )

        screen.blit(base, (0,0))
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
