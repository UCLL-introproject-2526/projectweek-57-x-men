import pygame
import random
import os
import sys

# ---------------- 1. INITIALIZATION ----------------
pygame.init()
pygame.mixer.init()

TILE_SIZE = 40
FPS = 60
MAX_HEALTH = 100

# YOUR ORIGINAL MAPS
LEVELS = [
    [
        "#############################",
        "#......##....##....##.......#",
        "#.####..##..##..####..####..#",
        "#..BB.....#.....BB......B...#",
        "#..BB..#..#.#..BB..######...#",
        "#...TTX.#.T..#......#.......#",
        "#####.XX....#...T.....####..#",
        "#....###....#..T...#........#",
        "#..BB..#..###..BB..XX..BB.#.#",
        "#..BB...........BB...TX.BB..#",
        "#.####..##..##..####..##..###",
        "#.TXT..##....##....##.......#",
        "#..BB.XX...BB...X..BB.......#",
        "#......#..TT.#..XX..#....#..#",
        "#############################",
    ],
    [
        "#############################",
        "#..BB....####....BB....####.#",
        "#..##....####....##....####.#",
        "#......BB......BB......BB...#",
        "####..######..######..####..#",
        "#......#......#......#......#",
        "#....###...######...##..##..#",
        "#......BB......BB......BB..##",
        "#..##....####....##....##.#.#",
        "#..BB....####....BB....#..#.#",
        "#......BB......BB......BB...#",
        "####..######..######..####..#",
        "#......#......#......#...#..#",
        "#..BB......BB......BB.......#",
        "#############################",
    ],
    [
        "#############################",
        "#..........####............##",
        "#.##..#..#..##..###..###....#",
        "#.#BB....#......#....BB#....#",
        "#.#....#.##.##.##.#.#..#....#",
        "#.#..#..............#......##",
        "#.......###....###..#....#..#",
        "#.........BBBB..............#",
        "#..........BBBB.............#",
        "#.#..#..###....###..#..#...##",
        "#.#..#..............#..#....#",
        "#.#..###.##..#..#.###..#.#..#",
        "#.BBB....#......#....BB#....#",
        "#...##..#..##....#..#.#.....#",
        "#############################",
    ]
]

WIDTH = len(LEVELS[0][0]) * TILE_SIZE
HEIGHT = len(LEVELS[0]) * TILE_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Horror Maze - Camera Shake Edition")
clock = pygame.time.Clock()

# Colors
FLOOR_COLOR = (220, 200, 160)
WALL_COLOR = (80, 60, 50)
WHITE = (255, 255, 255)
RED = (200, 20, 20)
GREEN = (0, 200, 0)
GOLD = (255, 215, 0)

# ---------------- 2. ASSETS & CAMERA ----------------
def load_img(path, size, color):
    try:
        return pygame.transform.scale(pygame.image.load(path).convert_alpha(), size)
    except:
        surf = pygame.Surface(size); surf.fill(color); return surf

player_img = load_img("project/img/player.gif", (30, 30), (0, 255, 0))
player_img_right = player_img
player_img_left = pygame.transform.flip(player_img, True, False)

bush_img = load_img("project/img/bush.png", (40, 40), (0, 100, 0))
tree_1_img = load_img("project/img/Forest/tree_1.png", (TILE_SIZE, TILE_SIZE * 2), (100, 50, 30))
tree_2_img = load_img("project/img/Forest/tree_2.png", (TILE_SIZE, TILE_SIZE * 2), (100, 50, 30))
ghost_img = load_img("project/img/ghost1.png", (30, 30), (180, 180, 255))      
menu_bg = load_img("project/img/Final_poster.png", (WIDTH, HEIGHT), (20, 20, 20))

class Camera:
    def __init__(self):
        self.offset_x = 0
        self.offset_y = 0

    def update(self, is_shaking):
        if is_shaking:
            # Generate a random vibration
            self.offset_x = random.randint(-10, 10)
            self.offset_y = random.randint(-10, 10)
        else:
            self.offset_x = 0
            self.offset_y = 0

    def apply(self, rect):
        """Returns a new rect moved by the camera offset."""
        return rect.move(self.offset_x, self.offset_y)

# ---------------- 3. CLASSES ----------------
class Player:
    def __init__(self, pos):
        self.rect = player_img.get_rect(topleft=pos)
        self.spawn_pos = pos
        self.speed = 4
        self.health = MAX_HEALTH
        self.is_hidden = False
        self.facing_right = False

    def update(self, walls, bushes):
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: 
            dx = -self.speed
            self.facing_right = True

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.speed
            self.facing_right = False

        if keys[pygame.K_UP] or keys[pygame.K_w]: 
            dy = -self.speed

        if keys[pygame.K_DOWN] or keys[pygame.K_s]: 
            dy = self.speed
        

        # Horizontal collision
        self.rect.x += dx
        for w in walls:
            if self.rect.colliderect(w):
                if dx > 0: self.rect.right = w.left
                if dx < 0: self.rect.left = w.right


        # Vertical collision
        self.rect.y += dy
        for w in walls:
            if self.rect.colliderect(w):
                if dy > 0: self.rect.bottom = w.top
                if dy < 0: self.rect.top = w.bottom

        self.is_hidden = any(b.collidepoint(self.rect.center) for b in bushes)

class Monster:
    def __init__(self, pos, speed):
        self.rect = ghost_img.get_rect(topleft=pos)
        self.speed = speed
        self.dir = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
        self.timer = 0

    def update(self, player, walls):
        if not player.is_hidden:
            dx = 1 if player.rect.x > self.rect.x else -1
            dy = 1 if player.rect.y > self.rect.y else -1
        else:
            if self.timer <= 0:
                self.dir = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
                self.timer = random.randint(40, 100)
            self.timer -= 1
            dx, dy = self.dir

        self.move(dx * self.speed, dy * self.speed, walls)

    def move(self, dx, dy, walls):
        self.rect.x += dx
        for w in walls:
            if self.rect.colliderect(w): self.rect.x -= dx
        self.rect.y += dy
        for w in walls:
            if self.rect.colliderect(w): self.rect.y -= dy

# ---------------- 4. HELPERS ----------------
def draw_ui(surf, health):
    # Health Bar
    pygame.draw.rect(surf, RED, (20, 20, 200, 20))
    pygame.draw.rect(surf, GREEN, (20, 20, int((health/MAX_HEALTH)*200), 20))
    pygame.draw.rect(surf, WHITE, (20, 20, 200, 20), 2)

def get_level_data(level_map, level_idx):
    walls, bushes, coins, floors = [], [], [], []
    trees = []  # ← New: store tree positions for drawing
    for y, row in enumerate(level_map):
        for x, char in enumerate(row):
            r = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if char == '#':
                walls.append(r)
            else:
                floors.append(r)
                if char == 'B':
                    bushes.append(r)
                elif char == 'T':
                    trees.append(('T', r))
                elif char == 'X':
                    trees.append(('X', r))
                elif char == '.' and random.random() < 0.08:
                    coins.append(pygame.Rect(r.centerx - 5, r.centery - 5, 10, 10))
                
    spawn = random.choice(bushes).topleft if bushes else (40, 40)
    return walls, bushes, coins, floors, trees, spawn  # ← return trees too

# ---------------- 5. MAIN LOOP ----------------
def main_game():
    level_idx = 0
    player = None
    camera = Camera()

    while level_idx < len(LEVELS):
        walls, bushes, coins, floors, spawn = get_level_data(LEVELS[level_idx], level_idx)
        
        if not player: player = Player(spawn)
        else: player.rect.topleft = spawn; player.health = MAX_HEALTH

        monsters = [Monster(random.choice(floors).topleft, 2.0 + (level_idx * 0.8)) for _ in range(level_idx + 3)]
        
        level_running = True
        while level_active := level_running:
            clock.tick(FPS)
            is_touching_monster = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()

            # Logic
            player.update(walls, bushes)
            for m in monsters:
                m.update(player, walls)
                if m.rect.colliderect(player.rect) and not player.is_hidden:
                    player.health -= 0.5 # Damage
                    is_touching_monster = True # Trigger Shake
            
            # Camera Update
            camera.update(is_touching_monster)

            if player.health <= 0: return # Dead

            for c in coins[:]:
                if player.rect.colliderect(c): coins.remove(c)
            if not coins: level_running = False; level_idx += 1

            # Drawing
            screen.fill((10, 10, 10))
            
            # Draw everything with camera.apply()
            for f in floors: pygame.draw.rect(screen, FLOOR_COLOR, camera.apply(f))
            for w in walls: pygame.draw.rect(screen, WALL_COLOR, camera.apply(w))
            for b in bushes: screen.blit(bush_img, camera.apply(b))
            for c in coins: pygame.draw.circle(screen, GOLD, camera.apply(c).center, 6)
            for m in monsters: screen.blit(ghost_img, camera.apply(m.rect))
            
            # Draw player (with hiding effect)
            p_rect_shaken = camera.apply(player.rect)

            # Choose player image based on facing direction
            p_img = player_img_right if player.facing_right else player_img_left
            p_img = p_img.copy()

            if player.is_hidden: 
                p_img.set_alpha(128)

            screen.blit(p_img, p_rect_shaken)

            draw_ui(screen, player.health)
            pygame.display.flip()

def main_menu():
    while True:
        screen.blit(menu_bg, (0, 0))
        font = pygame.font.SysFont(None, 45)
        text = font.render("PRESS SPACE TO BEGIN", True, WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT - 80))
        if pygame.time.get_ticks() % 1000 < 500: screen.blit(text, text_rect)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: main_game()

if __name__ == "__main__":
    main_menu()