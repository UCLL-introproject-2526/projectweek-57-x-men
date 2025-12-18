import pygame
import random
import os
import sys
import json

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# ---------------- SETTINGS & SAVE SYSTEM ----------------
TILE_SIZE = 40
FPS = 60
SCORE_FILE = "best_run.json"

def load_best_run():
    if os.path.exists(SCORE_FILE):
        try:
            with open(SCORE_FILE, "r") as f:
                return json.load(f)
        except: pass
    return {"name": "None", "time": 99999} 

def save_best_run(name, total_time):
    with open(SCORE_FILE, "w") as f:
        json.dump({"name": name, "time": total_time}, f)

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

# Screen Setup
ROWS = len(LEVELS[0])
COLS = len(LEVELS[0][0])
WIDTH = COLS * TILE_SIZE
HEIGHT = ROWS * TILE_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
<<<<<<< HEAD
pygame.display.set_caption("Horror Maze - Speedrun Edition")
=======
pygame.display.set_caption("Horror Maze - FAST MONSTERS")
>>>>>>> f2668d2b4190c29fa845d2d27dbb275939936da6
clock = pygame.time.Clock()

# Colors
FLOOR = (35, 30, 25); WALL = (80, 60, 50); WHITE = (255, 255, 255)
RED = (200, 20, 20); GOLD = (255, 215, 0); GREEN = (0, 255, 0)

<<<<<<< HEAD
# Assets
def load_sound(filename):
    return pygame.mixer.Sound(filename) if os.path.exists(filename) else None

move_sound = load_sound("project/music/why-are-you-running-orignal-scene.mp3")
scream_sound = load_sound("project/music/scream-of-terror3-325534.mp3")

def load_img(path, size, color):
    try: return pygame.transform.scale(pygame.image.load(path), size)
=======
# ---------------- ASSET LOADING ----------------
def load_img(path, size, color=(255, 0, 0)):
    try:
        return pygame.transform.scale(pygame.image.load(path), size)
>>>>>>> f2668d2b4190c29fa845d2d27dbb275939936da6
    except:
        s = pygame.Surface(size); s.fill(color); return s

player_img = load_img("project/img/player.gif", (30, 30), GREEN)
bush_img = load_img("project/img/bush.png", (40, 40), (0, 100, 0))
ghost_img = load_img("project/img/ghost.png", (30, 30), (255, 50, 50))
menu_bg = load_img("project/img/Final_poster.png", (WIDTH, HEIGHT), (20, 20, 20))

# ---------------- CLASSES ----------------
class Player:
    def __init__(self, spawn_pos, speed):
        self.rect = player_img.get_rect(topleft=spawn_pos)
<<<<<<< HEAD
        self.speed = 4
        self.lives = 5 
=======
        self.speed = 4.5 # Slightly faster player to keep it fair
        self.lives = 5
>>>>>>> f2668d2b4190c29fa845d2d27dbb275939936da6
        self.invince_frames = 0 
        self.is_hidden = False
        self.spawn_point = spawn_pos

    def move(self, keys, walls, bushes):
        if self.invince_frames > 0: self.invince_frames -= 1
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy += self.speed
        
<<<<<<< HEAD
        if (dx != 0 or dy != 0) and move_sound:
            if not self.move_channel.get_busy(): self.move_channel.play(move_sound, loops=-1)
        else: self.move_channel.stop()
=======
        if dx != 0 or dy != 0: is_moving = True
>>>>>>> f2668d2b4190c29fa845d2d27dbb275939936da6

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
                self.is_hidden = True; break

    def draw(self, surf):
        if self.invince_frames % 10 < 5:
            temp = player_img.copy()
            if self.is_hidden: temp.set_alpha(128)
            surf.blit(temp, self.rect)

class Monster:
    def __init__(self, x, y, speed):
        self.rect = ghost_img.get_rect(topleft=(x, y))
<<<<<<< HEAD
        self.speed = speed
        self.dir = pygame.Vector2(random.choice([(1,0), (-1,0), (0,1), (0,-1)]))
=======
        self.base_speed = speed
        self.dir = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
        self.change_dir_timer = 0
<<<<<<< HEAD
        
=======
        self.is_chasing = False

>>>>>>> 5c279d5ebdb47721df30696d3528261103baed62
    def update(self, player, walls, is_player_moving):
        # Increased detection: Chases if player moves nearby or isn't hidden
        if not player.is_hidden and is_player_moving:
            self.is_chasing = True
            dx = 1 if player.rect.centerx > self.rect.centerx else -1
            dy = 1 if player.rect.centery > self.rect.centery else -1
            self.dir = (dx, dy)
            current_speed = self.base_speed * 1.2 # Chase speed boost
        else:
            self.is_chasing = False
            current_speed = self.base_speed
            self.change_dir_timer -= 1
            if self.change_dir_timer <= 0:
                self.dir = random.choice([(1,0), (-1,0), (0,1), (0,-1), (1,1), (-1,-1)])
                self.change_dir_timer = random.randint(20, 50) # Faster patrol shifts
>>>>>>> f2668d2b4190c29fa845d2d27dbb275939936da6

    def update(self, player, walls):
        if not player.is_hidden:
            p_vec = pygame.Vector2(player.rect.center)
            m_vec = pygame.Vector2(self.rect.center)
            if m_vec.distance_to(p_vec) > 0:
                self.dir = (p_vec - m_vec).normalize()
        
        old_pos = self.rect.topleft
<<<<<<< HEAD
        self.rect.x += self.dir.x * self.speed
        for w in walls:
            if self.rect.colliderect(w): self.rect.x = old_pos[0]; break
        self.rect.y += self.dir.y * self.speed
        for w in walls:
            if self.rect.colliderect(w): self.rect.y = old_pos[1]; break
=======
        self.rect.x += self.dir[0] * current_speed
        self.rect.y += self.dir[1] * current_speed

        for w in walls:
            if self.rect.colliderect(w):
                self.rect.topleft = old_pos
                self.change_dir_timer = 0 
                break
>>>>>>> f2668d2b4190c29fa845d2d27dbb275939936da6

    def draw(self, surf):
        # Draw with a red tint if chasing
        surf.blit(ghost_img, self.rect)

# ---------------- HELPERS ----------------
def get_input(prompt):
    name = ""
    font = pygame.font.SysFont(None, 50)
    while True:
        screen.fill((10, 10, 10))
        txt = font.render(f"{prompt}: {name}", True, WHITE)
        screen.blit(txt, txt.get_rect(center=(WIDTH//2, HEIGHT//2)))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN and name != "": return name
                elif e.key == pygame.K_BACKSPACE: name = name[:-1]
                else: name += e.unicode
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()

def get_level_data(level_map):
    walls, bushes, coins, valid_floors = [], [], [], []
    for y, row in enumerate(level_map):
        for x, t in enumerate(row):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if t == '#': walls.append(rect)
            else:
                valid_floors.append(rect.center)
                if t == 'B': bushes.append(rect)
<<<<<<< HEAD
                elif t == '.' and random.random() < 0.08:
                    coins.append(pygame.Rect(rect.centerx-6, rect.centery-6, 12, 12))
    if not coins: coins.append(pygame.Rect(valid_floors[-1][0]-6, valid_floors[-1][1]-6, 12, 12))
    return walls, bushes, coins, valid_floors

=======
                elif t == '.':
                    if random.random() < 0.08:
                        coins.append(pygame.Rect(rect.centerx-6, rect.centery-6, 12, 12))
    
    if not coins:
        coins.append(pygame.Rect(valid_floor_tiles[-1][0]-6, valid_floor_tiles[-1][1]-6, 12, 12))
        
    return walls, bushes, coins, valid_floor_tiles, spawn_pos

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
        if pygame.time.get_ticks() % 1000 < 500: screen.blit(text, text_rect)
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE: menu_running = False

>>>>>>> f2668d2b4190c29fa845d2d27dbb275939936da6
def main():
    while True:
        best_data = load_best_run()
        # Initial Menu
        menu = True
        while menu:
            screen.blit(menu_bg, (0,0))
            f_menu = pygame.font.SysFont(None, 35)
            hs_txt = f_menu.render(f"RECORD: {best_data['time']}s by {best_data['name']}", True, GOLD)
            st_txt = f_menu.render("PRESS SPACE TO BEGIN", True, WHITE)
            screen.blit(hs_txt, hs_txt.get_rect(center=(WIDTH//2, HEIGHT-120)))
            screen.blit(st_txt, st_txt.get_rect(center=(WIDTH//2, HEIGHT-60)))
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE: menu = False

        player_name = get_input("ENTER SURVIVOR NAME")
        level_idx = 0; current_lives = 5; total_seconds = 0; game_active = True

        while level_idx < len(LEVELS) and game_active:
            walls, bushes, coins, valid_floors = get_level_data(LEVELS[level_idx])
            spawn_pos = (TILE_SIZE + 5, TILE_SIZE + 5)
            
            # SPEED SCALING
            p_speed = 4 + (level_idx * 0.7)
            m_speed = 1.8 + (level_idx * 0.6)
            
            player = Player(spawn_pos, p_speed)
            player.lives = current_lives
            monsters = []
<<<<<<< HEAD
            for _ in range(level_idx + 2):
                found = False
                while not found:
                    m_pos = random.choice(valid_floors)
                    if pygame.Vector2(m_pos).distance_to(spawn_pos) > 250:
                        monsters.append(Monster(m_pos[0]-15, m_pos[1]-15, m_speed))
                        found = True
=======
            num_monsters = level_idx + 3 # Extra monster per level
            for _ in range(num_monsters):
                found_v = False
                while not found_v:
                    m_pos = random.choice(valid_floors)
                    if pygame.Vector2(m_pos).distance_to(spawn_pos) > 200:
                        # Starting speed is now 3.5, increases by 0.8 per level
                        monsters.append(Monster(m_pos[0]-15, m_pos[1]-15, 3.5 + (level_idx * 0.8)))
                        found_v = True
>>>>>>> f2668d2b4190c29fa845d2d27dbb275939936da6

            start_ticks = pygame.time.get_ticks()
            level_running = True
            while level_running:
                elapsed = (pygame.time.get_ticks() - start_ticks) // 1000
                clock.tick(FPS)
                for e in pygame.event.get():
                    if e.type == pygame.QUIT: pygame.quit(); sys.exit()

                player.move(pygame.key.get_pressed(), walls, bushes)
                for m in monsters:
                    m.update(player, walls)
                    if m.rect.colliderect(player.rect) and player.invince_frames <= 0 and not player.is_hidden:
<<<<<<< HEAD
                        if scream_sound: scream_sound.play()
                        player.lives -= 1; player.invince_frames = 120
                        player.rect.topleft = player.spawn_point
                        if player.lives <= 0: game_active = False; level_running = False
=======
                        player.lives -= 1
                        player.invince_frames = 90 # Shorter recovery time
                        player.rect.topleft = player.spawn_point
                        if player.lives <= 0:
                            end_screen("GAME OVER", RED); game_active = False; level_running = False; break
>>>>>>> f2668d2b4190c29fa845d2d27dbb275939936da6

                for c in coins[:]:
                    if player.rect.colliderect(c): coins.remove(c)

                screen.fill((0,0,0))
                for f in valid_floors: pygame.draw.rect(screen, FLOOR, (f[0]-20, f[1]-20, 40, 40))
                for w in walls: pygame.draw.rect(screen, WALL, w)
                for b in bushes: screen.blit(bush_img, b)
                for c in coins: pygame.draw.circle(screen, GOLD, c.center, 6)
                for m in monsters: m.draw(screen)
                player.draw(screen)
                
                # HUD
                f_ui = pygame.font.SysFont(None, 30)
                timer_txt = f_ui.render(f"ELAPSED: {elapsed}s", True, WHITE)
                screen.blit(timer_txt, (WIDTH - 160, 15))
                for i in range(player.lives): pygame.draw.rect(screen, RED, (15 + i*30, 15, 20, 20))
                pygame.display.flip()

                if not coins:
<<<<<<< HEAD
                    total_seconds += elapsed
                    level_idx += 1; current_lives = player.lives; level_running = False
                    player.move_channel.stop()
=======
                    level_idx += 1; current_lives = player.lives
                    if level_idx < len(LEVELS): end_screen(f"LEVEL {level_idx+1}", WHITE)
                    level_running = False
>>>>>>> f2668d2b4190c29fa845d2d27dbb275939936da6

        # End Results
        screen.fill((0,0,0))
        f_end = pygame.font.SysFont(None, 55)
        if game_active:
            res_msg = f"CONGRATS, {player_name.upper()}!"
            time_msg = f"TOTAL TIME: {total_seconds}s"
            screen.blit(f_end.render(res_msg, True, GOLD), (50, 150))
            screen.blit(f_end.render(time_msg, True, WHITE), (50, 220))
            if total_seconds < best_data["time"]:
                save_best_run(player_name, total_seconds)
                screen.blit(f_end.render("NEW WORLD RECORD!", True, GREEN), (50, 290))
        else:
            screen.blit(f_end.render("GAME OVER - YOU DIED", True, RED), (WIDTH//2-200, HEIGHT//2))
        
        pygame.display.flip()
        pygame.time.delay(5000)

if __name__ == "__main__":
    main()