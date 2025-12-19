import pygame
import random
import os
import sys
import math

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
        "#......#....#......#........#",
        "#####.......#.........####..#",
        "#....###....#......#........#",
        "#..BB..#..###..BB......BB.#.#",
        "#..BB...........BB......BB..#",
        "#.####..##..##..####..##..###",
        "#......##...B##....##.......#",
        "#..BB.......................#",
        "#......#....#...B..#.....#.B#",
        "#############################",
    ],
    [
        "#############################",
        "#..BB....#..#....BB....#..#.#",
        "#..##....##.#....##....##...#",
        "#......BB......BB......BB...#",
        "####..######..######..####..#",
        "#......#......#......#......#",
        "#....###...######...##..##..#",
        "#......BB..............BB..##",
        "#..##....####....##....##.#.#",
        "#..B........#....BB....#..#.#",
        "#.......B...................#",
        "####..######..######.B##....#",
        "#......#....B.#......#...#..#",
        "#..BB.....#........BB....#..#",
        "#############################",
    ],
    [
        "#############################",
        "#....BB....#..#............##",
        "#.##..#..#.#.#..###..###B...#",
        "#.BB.....#...B..#....BB#....#",
        "#.#....#.##.##.##.#.#..#....#",
        "#.#..#..............#......##",
        "#.......###....###..#....#..#",
        "#.......BBB...............BB#",
        "#..............BBB.........B#",
        "#.#B.#..###....###..#.B#...##",
        "#.#..#..............#..#....#",
        "#.#..###.##B.#..#.###..#.#..#",
        "#.B......#......#....BB#....#",
        "#....#..#..##..B.#..#.#.....#",
        "#############################",
    ]
]

WIDTH = len(LEVELS[0][0]) * TILE_SIZE
HEIGHT = len(LEVELS[0]) * TILE_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The FOREST (Survive the forest!)")
clock = pygame.time.Clock()

# Colors
FLOOR_COLOR = (220, 200, 160)
WALL_COLOR = (80, 60, 50)
WHITE = (255, 255, 255)
RED = (200, 20, 20)
GREEN = (0, 200, 0)
GOLD = (255, 215, 0)

# ---------------- 2. ASSETS ----------------
def load_img(path, size, color):
    try:
        return pygame.transform.scale(pygame.image.load(path).convert_alpha(), size)
    except:
        surf = pygame.Surface(size); surf.fill(color); return surf
    
player_img = load_img("img/player.gif", (30, 30), (0, 255, 0))
player_img_left = player_img
player_img_right = pygame.transform.flip(player_img, True, False)

bush_img = load_img("img/bush.png", (40, 40), (0, 100, 0))
menu_bg = load_img("img/Final_poster.png", (WIDTH, HEIGHT), (20, 20, 20))

victory_music = pygame.mixer.Sound("sound/victory.mp3")
lvl_1_music = pygame.mixer.Sound("sound/lvl_1.mp3")
coin_sound = pygame.mixer.Sound("sound/coin.mp3")
collision_sound = pygame.mixer.Sound("sound/yru_runnen.mp3")
scary_sound = pygame.mixer.Sound("video/end.wav")


# ---------------- 3. CLASSES ----------------
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

restart_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 40, 220, 55)
quit_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 110, 220, 55)


class Player:
    def __init__(self, pos):
        self.rect = player_img.get_rect(topleft=pos)
        self.spawn_pos = pos
        self.speed = 4
        self.health = MAX_HEALTH
        self.is_hidden = False
        self.facing_right = True

    def update(self, walls, bushes):
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: 
            dx = -self.speed
            self.facing_right = False

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.speed
            self.facing_right = True

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
    def __init__(self, pos, speed, image):
        self.image = image
        self.rect = image.get_rect(topleft=pos)
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
            self.timer -= 1.5
            dx, dy = self.dir

        self.move(dx * self.speed, dy * self.speed, walls)

    def move(self, dx, dy, walls):
        self.rect.x += dx
        for w in walls:
            if self.rect.colliderect(w): self.rect.x -= dx
        self.rect.y += dy
        for w in walls:
            if self.rect.colliderect(w): self.rect.y -= dy

class Firework:
    def __init__(self):
        self.x = random.randint(100, WIDTH - 100)
        self.y = random.randint(50, HEIGHT // 2)
        self.particles = []

        for _ in range(60):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            self.particles.append([
                self.x,
                self.y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                random.randint(40, 60)
            ])

    def update(self):
        for p in self.particles:
            p[0] += p[2]
            p[1] += p[3]
            p[4] -= 1

    def draw(self, surf):
        for x, y, _, _, life in self.particles:
            if life > 0:
                pygame.draw.circle(surf, GOLD, (int(x), int(y)), 3)


# ---------------- 4. HELPERS ----------------
def draw_ui(surf, health):
    # Health Bar
    pygame.draw.rect(surf, RED, (40, 10, 200, 20))
    pygame.draw.rect(surf, GREEN, (40, 10, int((health/MAX_HEALTH)*200), 20))
    pygame.draw.rect(surf, WHITE, (40, 10, 200, 20), 2)

def get_level_data(level_map, level_idx):
    walls, bushes, coins, floors = [], [], [], []
    for y, row in enumerate(level_map):
        for x, char in enumerate(row):
            r = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if char == '#': walls.append(r)
            else:
                floors.append(r)
                if char == 'B': bushes.append(r)
                elif char == '.' and random.random() < 0.05: # 5% chance for coin
                    coins.append(pygame.Rect(r.centerx-5, r.centery-5, 10, 10))
    
    spawn = random.choice(bushes).topleft if bushes else (40, 40)
    return walls, bushes, coins, floors, spawn

def level_screen(level_number):
    start_time = pygame.time.get_ticks()

    while pygame.time.get_ticks() - start_time < 2000:
        clock.tick(60)
        screen.fill((0, 0, 0))

        font = pygame.font.SysFont(None, 70)
        text = font.render(f"LEVEL {level_number}", True, WHITE)
        screen.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2)))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


def game_over_screen():
    while True:
        pygame.mixer.music.stop()
        clock.tick(60)
        screen.fill((0, 0, 0))

        font_big = pygame.font.SysFont(None, 80)
        font_small = pygame.font.SysFont(None, 36)

        title = font_big.render("GAME OVER", True, RED)
        screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 80)))

        pygame.draw.rect(screen, GREEN, restart_button, border_radius=10)
        pygame.draw.rect(screen, RED, quit_button, border_radius=10)

        screen.blit(font_small.render("RESTART", True, WHITE),
                    restart_button.move(60, 15))
        screen.blit(font_small.render("QUIT", True, WHITE),
                    quit_button.move(80, 15))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.collidepoint(event.pos):
                    return "restart"
                if quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()


def game_complete_screen():
    lvl_1_music.stop()
    victory_music.play()

    fireworks = []
    spawn_timer = 0

    while True:
        clock.tick(60)
        screen.fill((10, 10, 30))

        spawn_timer += 1
        if spawn_timer > 25:
            fireworks.append(Firework())
            spawn_timer = 0

        for fw in fireworks[:]:
            fw.update()
            fw.draw(screen)
            if all(p[4] <= 0 for p in fw.particles):
                fireworks.remove(fw)

        font_big = pygame.font.SysFont(None, 60)
        font_mid = pygame.font.SysFont(None, 45)
        font_small = pygame.font.SysFont(None, 36)

        title = font_big.render("CONGRATULATIONS", True, GOLD)
        subtitle = font_mid.render("YOU SURVIVED THE FOREST!", True, WHITE)

        screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 120)))
        screen.blit(subtitle, subtitle.get_rect(center=(WIDTH//2, HEIGHT//2 - 50)))

        pygame.draw.rect(screen, GREEN, restart_button, border_radius=12)
        pygame.draw.rect(screen, RED, quit_button, border_radius=12)

        screen.blit(font_small.render("PLAY AGAIN", True, WHITE),
                    restart_button.move(40, 15))
        screen.blit(font_small.render("QUIT", True, WHITE),
                    quit_button.move(80, 15))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.collidepoint(event.pos):
                    pygame.mixer.music.stop()
                    return "restart"
                if quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

# ---------- VIDEO (FRAME-BASED) ----------
def play_end_animation():
    frame_folder = "video/end_frames"
    frames = []

    for f in sorted(os.listdir(frame_folder)):
        img = pygame.image.load(os.path.join(frame_folder, f)).convert()
        img = pygame.transform.scale(img, (WIDTH, HEIGHT))
        frames.append(img)

    scary_sound.play()

    for frame in frames:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                exit()

        screen.blit(frame, (0, 0))
        pygame.display.flip()
        clock.tick(24)  # video FPS

# ---------------- 5. MAIN LOOP ----------------
def main_game():
    level_idx = 0
    player = None
    camera = Camera()

    while level_idx < len(LEVELS):
        level_screen(level_idx + 1)
        lvl_1_music.play(-1)
        
        walls, bushes, coins, floors, spawn = get_level_data(LEVELS[level_idx], level_idx)
        
        if not player: player = Player(spawn)
        else: player.rect.topleft = spawn; player.health = MAX_HEALTH

        # Ghost image per level
        ghost_img = load_img(f"project/img/ghost{level_idx + 1}.png", (30, 30), (180, 180, 255))      

        # Create monsters
        monsters = [
            Monster(
                random.choice(floors).topleft, 
                2.0 + (level_idx * 0.8),
                ghost_img
            ) 
            for _ in range(level_idx + 3)
        ]
        
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
                    # collision_sound.play()
                    player.health -= 0.5 # Damage
                    is_touching_monster = True # Trigger Shake
                
            # Camera Update
            camera.update(is_touching_monster)

            # Dead
            if player.health <= 0: 
                lvl_1_music.stop()
                play_end_animation()
                choice = game_over_screen()
                if choice == "restart":
                    return  # Exit main_game() and restart from menu
                 
            # Complete Game
            for c in coins[:]:
                if player.rect.colliderect(c): 
                    coin_sound.play()
                    coins.remove(c)

            if not coins:
                level_running = False
                lvl_1_music.stop()
                # LAST LEVEL COMPLETED
                if level_idx == len(LEVELS) - 1:
                    choice = game_complete_screen()
                    if choice == "restart":
                        return   # back to main menu
                else:
                    level_idx += 1

                

            # Drawing
            screen.fill((10, 10, 10))
            
            # Draw everything with camera.apply()
            for f in floors: pygame.draw.rect(screen, FLOOR_COLOR, camera.apply(f))
            for w in walls: pygame.draw.rect(screen, WALL_COLOR, camera.apply(w))
            for b in bushes: screen.blit(bush_img, camera.apply(b))
            for c in coins: pygame.draw.circle(screen, GOLD, camera.apply(c).center, 6)
            for m in monsters: screen.blit(m.image, camera.apply(m.rect))
            
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
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                main_game()


if __name__ == "__main__":
    main_menu()