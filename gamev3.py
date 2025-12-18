import pygame
import random
import os
import sys
import json

# ---------------- 1. INITIALIZATION ----------------
pygame.init()
pygame.mixer.init()

TILE_SIZE = 40
FPS = 60
MAX_HEALTH = 100
SCORE_FILE = "best_run.json"

# YOUR ORIGINAL MAPS (UNCHANGED)
LEVELS = [
    [
        "#############################",
        "#......##....##....##.......#",
        "#.####..##..##..####..####..#",
        "#..BB.....#.....BB......B...#",
        "#..BB..#..#.#..BB..######...#",
        "#......#....#......#........#",
        "#####.......#.........####..#",
        "#....###....#......#........#",
        "#..BB..#..###..BB......BB.#.#",
        "#..BB...........BB......BB..#",
        "#.####..##..##..####..##..###",
        "#......##....##....##.......#",
        "#..BB......BB......BB.......#",
        "#......#....#......#.....#..#",
        "#############################",
    ],
    [
        "#############################",
        "#..BB....####....BB....####.#",
        "#..##....####....##....####.#",
        "#......BB......BB......BB...#",
        "####..######..######..####..#",
        "#......#......#......#......#",
        "#.######..####..######..##..#",
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
pygame.display.set_caption("Horror Maze - Predator AI")
clock = pygame.time.Clock()

# Colors
FLOOR_COLOR = (245, 245, 220) 
WALL_COLOR = (80, 60, 50)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 20, 20)
GREEN = (0, 255, 0) # Your player fallback color
GOLD = (255, 215, 0)

# ---------------- 2. ASSETS & LOADING ----------------
player_walk_right = []
player_walk_left = []

def load_img(path, size, color):
    try: return pygame.transform.scale(pygame.image.load(path).convert_alpha(), size)
    except:
        s = pygame.Surface(size); s.fill(color); return s

def display_loading_screen():
    loading_img = load_img("project/img/loading_screen.png", (WIDTH, HEIGHT), (20, 20, 20))
    screen.blit(loading_img, (0, 0))
    font = pygame.font.SysFont(None, 40)
    txt = font.render("LOADING ASSETS...", True, WHITE)
    screen.blit(txt, (WIDTH // 2 - 120, HEIGHT - 100))
    pygame.display.flip()
    pygame.time.delay(1500)

def load_assets(tile_size=TILE_SIZE):
    global player_walk_right, player_walk_left, bush_img, ghost_img, player_img
    
    # 1. Load the specific Player GIF requested
    player_img = load_img("project/img/player.gif", (30, 30), (0, 255, 0))
    
    # 2. Try to load walking frames
    try:
        player_walk_right = [
            pygame.image.load(os.path.join("img", f"player_walk_{i}.png")).convert_alpha()
            for i in range(3)
        ]
        player_walk_right = [pygame.transform.scale(img, (tile_size-10, tile_size-10)) for img in player_walk_right]
    except:
        # If walking frames fail, use the player.gif for the animation list
        player_walk_right = [player_img, player_img, player_img]

    # Create flipped versions for left movement
    player_walk_left = [pygame.transform.flip(img, True, False) for img in player_walk_right]

    # Other assets
    bush_img = load_img("project/img/bush.png", (40, 40), (0, 100, 0))
    ghost_img = load_img("project/img/ghost.png", (30, 30), (180, 180, 255))

# ---------------- 3. CLASSES ----------------
class Camera:
    def __init__(self):
        self.offset_x = 0; self.offset_y = 0

    def update(self, is_shaking):
        if is_shaking:
            self.offset_x = random.randint(-8, 8)
            self.offset_y = random.randint(-8, 8)
        else:
            self.offset_x = 0; self.offset_y = 0

    def apply(self, rect):
        return rect.move(self.offset_x, self.offset_y)

class Player:
    def __init__(self, pos):
        self.rect = pygame.Rect(pos[0], pos[1], 30, 30)
        self.speed = 5
        self.health = MAX_HEALTH
        self.is_hidden = False
        self.frame = 0
        self.facing_right = True
        self.is_moving = False

    def update(self, walls, bushes):
        keys = pygame.key.get_pressed()
        dx = dy = 0
        self.is_moving = False

        if keys[pygame.K_LEFT] or keys[pygame.K_a]: 
            dx = -self.speed; self.facing_right = False; self.is_moving = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]: 
            dx = self.speed; self.facing_right = True; self.is_moving = True
            
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -self.speed; self.is_moving = True
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = self.speed; self.is_moving = True

        # Axis-Independent Collision (Fixes Monster/Player clipping)
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

        if self.is_moving: self.frame = (self.frame + 0.15) % 3
        else: self.frame = 0

        self.is_hidden = any(b.collidepoint(self.rect.center) for b in bushes)

    def draw(self, surf, camera):
        frames = player_walk_left if self.facing_r else player_walk_right
        current_img = frames[int(self.frame)].copy()
        if self.is_hidden: current_img.set_alpha(128)
        surf.blit(current_img, camera.apply(self.rect))

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
                self.timer = random.randint(50, 100)
            self.timer -= 1
            dx, dy = self.dir

        # Fixed Monster Wall Clipping logic
        old_x = self.rect.x
        self.rect.x += dx * self.speed
        for w in walls:
            if self.rect.colliderect(w): self.rect.x = old_x; break
            
        old_y = self.rect.y
        self.rect.y += dy * self.speed
        for w in walls:
            if self.rect.colliderect(w): self.rect.y = old_y; break

# ---------------- 4. HELPERS ----------------
def get_level_data(level_map):
    walls, bushes, coins, floors = [], [], [], []
    for y, row in enumerate(level_map):
        for x, char in enumerate(row):
            r = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if char == '#': walls.append(r)
            else:
                floors.append(r)
                if char == 'B': bushes.append(r)
                elif char == '.' and random.random() < 0.1:
                    coins.append(pygame.Rect(r.centerx-5, r.centery-5, 10, 10))
    
    # Player spawns in a random bush
    if bushes:
        target_bush = random.choice(bushes)
        spawn = (target_bush.x + 5, target_bush.y + 5)
    else:
        spawn = (TILE_SIZE + 5, TILE_SIZE + 5)
        
    return walls, bushes, coins, floors, spawn

def show_transition(text):
    screen.fill(BLACK)
    font = pygame.font.SysFont(None, 60)
    label = font.render(text, True, WHITE)
    screen.blit(label, label.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
    pygame.display.flip()
    pygame.time.delay(1500)

# ---------------- 5. MAIN ----------------
def main_game():
    display_loading_screen()
    load_assets()
    
    level_idx = 0
    player = None
    camera = Camera()
    start_ticks = pygame.time.get_ticks()

    while level_idx < len(LEVELS):
        show_transition(f"LEVEL {level_idx + 1}")
        walls, bushes, coins, floors, spawn = get_level_data(LEVELS[level_idx])
        
        if not player: player = Player(spawn)
        else: player.rect.topleft = spawn; player.health = MAX_HEALTH

        monsters = [Monster(random.choice(floors).topleft, 2.7 + (level_idx * 0.4)) for _ in range(level_idx + 3)]
        
        level_running = True
        while level_running:
            clock.tick(FPS)
            elapsed = (pygame.time.get_ticks() - start_ticks) // 1000
            is_shaking = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()

            player.update(walls, bushes)
            for m in monsters:
                m.update(player, walls)
                if m.rect.colliderect(player.rect) and not player.is_hidden:
                    player.health -= 1.5; is_shaking = True
            
            camera.update(is_shaking)
            if player.health <= 0: show_transition("GAME OVER"); return

            for c in coins[:]:
                if player.rect.colliderect(c): coins.remove(c)
            if not coins: level_running = False; level_idx += 1

            screen.fill(FLOOR_COLOR)
            for w in walls: pygame.draw.rect(screen, WALL_COLOR, camera.apply(w))
            for b in bushes: screen.blit(bush_img, camera.apply(b))
            for c in coins: pygame.draw.circle(screen, GOLD, camera.apply(c).center, 6)
            for m in monsters: screen.blit(ghost_img, camera.apply(m.rect))
            
            player.draw(screen, camera)
            
            # HUD
            pygame.draw.rect(screen, RED, (20, 20, 200, 15))
            pygame.draw.rect(screen, GREEN, (20, 20, int((player.health/MAX_HEALTH)*200), 15))
            timer_txt = pygame.font.SysFont(None, 30).render(f"TIME: {elapsed}s", True, BLACK)
            screen.blit(timer_txt, (WIDTH - 150, 20))
            
            pygame.display.flip()

    show_transition(f"ESCAPED IN {(pygame.time.get_ticks()-start_ticks)//1000}s!")

if __name__ == "__main__":
    main_game()