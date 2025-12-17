import pygame
import random
import json
import os
import sys

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# ---------------- SETTINGS ----------------
TILE_SIZE = 40
FPS = 60
SAVE_FILE = "savegame.json"

# ---------------- LEVEL MAPS ----------------
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
        "############################",
        "#..BB....####....BB....####.#",
        "#..##....####....##....####.#",
        "#......BB......BB......BB...#",
        "####..######..######..####..#",
        "#......#......#......#......#",
        "#.######..####..######..##..#",
        "#......BB......BB......BB..##",
        "#..##....####....##....##.#.#",
        "#..BB....####....BB....#..#.#",
        "#......BB......BB......BB..##",
        "####..######..######..####..#",
        "#......#......#......#...#..#",
        "#..BB......BB......BB.......#",
        "############################",
    ],
    [
        "############################",
        "#..........####...........##",
        "#.##..#..#..##..###..###...#",
        "#.#BB....#......#....BB#...#",
        "#.#....#.##.##.##.#.#..#...#",
        "#.#..#..............#.....##",
        "#.......###....###..#....#.#",
        "#.........BBBB.............#",
        "#..........BBBB............#",
        "#.#..#..###....###..#..#..##",
        "#.#..#..............#..#...#",
        "#.#..###.##..#..#.###..#.#.#",
        "#.#BB....#......#....BB#...#",
        "#.#.##..#..##....#..#.#....#",
        "############################",
    ]
]

# Calculate Screen Size
ROWS = len(LEVELS[0])
COLS = len(LEVELS[0][0])
WIDTH = COLS * TILE_SIZE
HEIGHT = ROWS * TILE_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Horror Maze - Why Are You Running?")
clock = pygame.time.Clock()

# ---------------- COLORS ----------------
FLOOR = (35, 30, 25)
WALL = (80, 60, 50)
WHITE = (255, 255, 255)
RED = (200, 20, 20)
GOLD = (255, 215, 0)

# ---------------- ASSET LOADING ----------------
def load_sound(filename):
    if os.path.exists(filename):
        return pygame.mixer.Sound(filename)
    return None

move_sound = load_sound("project/music/why-are-you-running-orignal-scene.mp3")
scream_sound = load_sound("project/music/scream-of-terror3-325534.mp3")

def load_img(path, size, color=(255, 0, 0)):
    try:
        return pygame.transform.scale(pygame.image.load(path), size)
    except:
        surf = pygame.Surface(size)
        surf.fill(color)
        return surf

player_img = load_img("project/img/player.gif", (30, 30), (0, 255, 0))
bush_img = load_img("project/img/bush.png", (40, 40), (0, 100, 0))
ghost_img = load_img("project/img/ghost.png", (30, 30), (180, 180, 255))
menu_bg = load_img("project/img/Final_poster.png", (WIDTH, HEIGHT), (20, 20, 20))

# ---------------- CLASSES ----------------
class Player:
    def __init__(self, spawn_pos):
        self.rect = player_img.get_rect(topleft=spawn_pos)
        self.speed = 4
        self.lives = 3
        self.invince_frames = 0 
        self.is_hidden = False
        self.spawn_point = spawn_pos
        self.move_channel = pygame.mixer.Channel(1)

    def move(self, keys, walls, bushes):
        if self.invince_frames > 0: self.invince_frames -= 1
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy += self.speed
        
        if (dx != 0 or dy != 0) and move_sound:
            if not self.move_channel.get_busy():
                self.move_channel.play(move_sound, loops=-1)
        else:
            self.move_channel.stop()

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

        self.is_hidden = False
        for b in bushes:
            if b.collidepoint(self.rect.center):
                self.is_hidden = True
                break

    def draw(self, surf):
        if self.invince_frames % 10 < 5:
            temp_img = player_img.copy()
            if self.is_hidden:
                temp_img.set_alpha(128) 
            surf.blit(temp_img, self.rect)

class Monster:
    def __init__(self, x, y, speed):
        self.rect = ghost_img.get_rect(topleft=(x, y))
        self.speed = speed

    def update(self, player, walls):
        if not player.is_hidden:
            dx = 1 if player.rect.centerx > self.rect.centerx else -1
            dy = 1 if player.rect.centery > self.rect.centery else -1
        else:
            dx, dy = random.choice([(-1,0), (1,0), (0,-1), (0,1), (0,0)])

        self.rect.x += dx * self.speed
        for w in walls:
            if self.rect.colliderect(w): self.rect.x -= dx * self.speed
        self.rect.y += dy * self.speed
        for w in walls:
            if self.rect.colliderect(w): self.rect.y -= dy * self.speed

    def draw(self, surf): surf.blit(ghost_img, self.rect)

# ---------------- HELPERS ----------------
def get_level_data(level_map):
    walls, bushes, coins = [], [], []
    spawn_pos = (TILE_SIZE, TILE_SIZE) 
    found_spawn = False

    for y, row in enumerate(level_map):
        for x, t in enumerate(row):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if t == '#': walls.append(rect)
            elif t == 'B': 
                bushes.append(rect)
                if not found_spawn:
                    spawn_pos = (x * TILE_SIZE + 5, y * TILE_SIZE + 5)
                    found_spawn = True
            elif t == '.':
                if random.random() < 0.07:
                    coins.append(pygame.Rect(rect.centerx-6, rect.centery-6, 12, 12))
    return walls, bushes, coins, spawn_pos

def end_screen(text, color):
    font = pygame.font.SysFont(None, 80)
    screen.fill((0, 0, 0))
    label = font.render(text, True, color)
    screen.blit(label, label.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
    pygame.display.flip()
    pygame.time.delay(3000)

def main_menu():
    menu_running = True
    while menu_running:
        screen.blit(menu_bg, (0, 0))
        font = pygame.font.SysFont(None, 45)
        text = font.render("PRESS SPACE TO BEGIN", True, WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT - 80))
        
        if pygame.time.get_ticks() % 1000 < 500:
            screen.blit(text, text_rect)
            
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    menu_running = False

# ---------------- MAIN LOOP ----------------
def main():
    while True: # Wrap everything in a loop to return to menu
        main_menu()
        
        level_idx = 0
        current_lives = 3
        game_active = True

        while level_idx < len(LEVELS) and game_active:
            walls, bushes, coins, spawn_pos = get_level_data(LEVELS[level_idx])
            player = Player(spawn_pos)
            player.lives = current_lives
            
            # Monster speed increases per level
            
            
            if not coins: coins.append(pygame.Rect(WIDTH//2, HEIGHT//2, 12, 12))

            level_running = True
            while level_running:
                clock.tick(FPS)
                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        pygame.quit(); sys.exit()

                keys = pygame.key.get_pressed()
                player.move(keys, walls, bushes)

                # Monster Collision Logic
                for m in monsters:
                    m.update(player, walls)
                    if m.rect.colliderect(player.rect) and player.invince_frames <= 0 and not player.is_hidden:
                        if scream_sound: scream_sound.play()
                        player.lives -= 1
                        player.invince_frames = 120 
                        player.rect.topleft = player.spawn_point
                        
                        if player.lives <= 0:
                            player.move_channel.stop()
                            end_screen("GAME OVER", RED)
                            game_active = False # Break to outer loop
                            level_running = False

                # Coin Collection
                for c in coins[:]:
                    if player.rect.colliderect(c): coins.remove(c)

                # Rendering
                screen.fill((0,0,0))
                for y in range(len(LEVELS[level_idx])):
                    for x in range(len(LEVELS[level_idx][0])):
                        pygame.draw.rect(screen, FLOOR, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                
                for w in walls: pygame.draw.rect(screen, WALL, w)
                for b in bushes: screen.blit(bush_img, b)
                for c in coins: pygame.draw.circle(screen, GOLD, c.center, 6)
                for m in monsters: m.draw(screen)
                player.draw(screen)
                
                # HUD
                for i in range(player.lives):
                    pygame.draw.rect(screen, RED, (15 + i*30, 15, 20, 20))
                
                pygame.display.flip()

                # Win condition for level
                if not coins and game_active:
                    player.move_channel.stop()
                    level_idx += 1
                    current_lives = player.lives
                    if level_idx < len(LEVELS): 
                        end_screen(f"LEVEL {level_idx+1}", WHITE)
                    level_running = False

        # If we finished all levels
        if game_active:
            end_screen("YOU SURVIVED!", GOLD)

if __name__ == "__main__":
    main()