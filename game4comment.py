import pygame
import random
import os
import sys
import math

# ---------------- 1. INITIALIZATION ----------------
# Initialize pygame modules (display, events, etc.)
pygame.init()
# Initialize pygame audio mixer (sounds/music)
pygame.mixer.init()

# Each map tile is 40x40 pixels
TILE_SIZE = 40
# Game runs at 60 frames per second (target)
FPS = 60
# Player max health (health bar is based on this)
MAX_HEALTH = 100

# YOUR ORIGINAL MAPS
# LEVELS is a list of levels.
# Each level is a grid represented by a list of strings (rows).
# Each character = one tile:
#   '#' = wall (solid, blocks movement)
#   'B' = bush (hiding spot)
#   '.' = walkable ground (coin may spawn randomly on these)
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

# Window width is number of columns * tile size
WIDTH = len(LEVELS[0][0]) * TILE_SIZE
# Window height is number of rows * tile size
HEIGHT = len(LEVELS[0]) * TILE_SIZE

# Create window/screen with computed size
screen = pygame.display.set_mode((WIDTH, HEIGHT))
# Window title
pygame.display.set_caption("The FOREST (Survive the forest!)")
# Clock controls FPS
clock = pygame.time.Clock()

# Colors (RGB)
FLOOR_COLOR = (220, 200, 160)  # floor background color
WALL_COLOR = (80, 60, 50)      # walls color
WHITE = (255, 255, 255)        # text/outline
RED = (200, 20, 20)            # health bar background + game over title
GREEN = (0, 200, 0)            # health bar fill + restart button background
GOLD = (255, 215, 0)           # coin color + victory title + fireworks particles

player_walk_right = []
player_walk_left = []
bush_img = None

def load_assets(tile_size=TILE_SIZE):
    global player_walk_right, player_walk_left, bush_img,tree_img
    # Load walking frames
    player_walk_right = [
        pygame.image.load(os.path.join("img", f"player_walk_{i}.png")).convert_alpha()
        for i in range(3)
    ]
    player_walk_right = [pygame.transform.scale(img, (tile_size-10, tile_size-10)) for img in player_walk_right]
    player_walk_left = [pygame.transform.flip(img, True, False) for img in player_walk_right]

    # Load bush
    bush_img = pygame.image.load(os.path.join("img", "bush.png")).convert_alpha()
    bush_img = pygame.transform.scale(bush_img, (tile_size, tile_size))



    # -------- MENU BACKGROUND --------
menu_bg = pygame.image.load(
    os.path.join("img", "Final_poster.png")
).convert_alpha()
menu_bg = pygame.transform.scale(menu_bg, (WIDTH, HEIGHT))

load_assets()

# Sound effects / music
victory_music = pygame.mixer.Sound("sound/victory.mp3")        # played on completion
lvl_1_music = pygame.mixer.Sound("sound/lvl_1.mp3")            # looped during levels
coin_sound = pygame.mixer.Sound("sound/coin.mp3")              # coin pickup
collision_sound = pygame.mixer.Sound("sound/yru_runnen.mp3")   # collision (currently commented out later)
scary_sound = pygame.mixer.Sound("video/end.wav")              # scary sound for end animation

# ---------------- 3. CLASSES ----------------
class Camera:
    def __init__(self):
        # Offsets applied to drawing to create shake effect
        self.offset_x = 0
        self.offset_y = 0

    def update(self, is_shaking):
        # If player is being hit, shake camera by random offsets
        if is_shaking:
            # Generate a random vibration
            self.offset_x = random.randint(-10, 10)
            self.offset_y = random.randint(-10, 10)
        else:
            # No shake, offsets reset
            self.offset_x = 0
            self.offset_y = 0

    def apply(self, rect):
        """Returns a new rect moved by the camera offset."""
        # Return shifted rectangle (drawing only, does not change physics positions)
        return rect.move(self.offset_x, self.offset_y)

# UI buttons (rectangles used for click detection + drawing)
restart_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 40, 220, 55)
quit_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 110, 220, 55)

class Player:
    def __init__(self, pos):
        # Player hitbox positioned at spawn
        self.image = player_walk_right[0]
        self.rect = self.image.get_rect(topleft=pos)
        # Store spawn position (for reference)
        self.spawn_pos = pos
        # Movement speed
        self.speed = 4
        # Current health
        self.health = MAX_HEALTH
        # True when in bush tile (hidden)
        self.is_hidden = False
        # Direction for choosing sprite image
        self.facing_right = True
        self.frame_index = 0.0
        self.anim_speed = 0.15

    def update(self, walls, bushes):
        # Read current keyboard state
        keys = pygame.key.get_pressed()
        dx = dy = 0

        # Left movement + face left
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -self.speed
            self.facing_right = True

        # Right movement + face right
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.speed
            self.facing_right = False

        # Up movement
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -self.speed

        # Down movement
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = self.speed

        # Horizontal collision:
        # move x, then push player out of wall if collided
        self.rect.x += dx
        for w in walls:
            if self.rect.colliderect(w):
                if dx > 0: self.rect.right = w.left
                if dx < 0: self.rect.left = w.right

        # Vertical collision:
        # move y, then push player out of wall if collided
        self.rect.y += dy
        for w in walls:
            if self.rect.colliderect(w):
                if dy > 0: self.rect.bottom = w.top
                if dy < 0: self.rect.top = w.bottom

        if dx != 0 or dy != 0:
            self.frame_index += self.anim_speed
        else:
            self.frame_index = 0

        if self.frame_index >= len(player_walk_right):
            self.frame_index = 0

        # Hidden if player center is inside any bush rectangle
        self.is_hidden = any(b.collidepoint(self.rect.center) for b in bushes)

class Monster:
    def __init__(self, pos, speed, image):
        # Each monster holds its own image (so different levels can have different ghosts)
        self.image = image
        # Rect built from that image at starting position
        self.rect = image.get_rect(topleft=pos)
        # Movement speed
        self.speed = speed
        # Random direction used for wandering when player is hidden
        self.dir = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
        # Timer controls how long it continues wandering in one direction
        self.timer = 0

    def update(self, player, walls):
        # If player is visible, chase (simple x/y direction)
        if not player.is_hidden:
            dx = 1 if player.rect.x > self.rect.x else -1
            dy = 1 if player.rect.y > self.rect.y else -1
        else:
            # If player hidden, wander randomly
            if self.timer <= 0:
                # Choose new direction occasionally
                self.dir = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
                self.timer = random.randint(40, 100)
            # Timer decreases (note: you used 1.5 here, making it count down faster)
            self.timer -= 1.5
            dx, dy = self.dir

        # Move and handle wall collisions
        self.move(dx * self.speed, dy * self.speed, walls)

    def move(self, dx, dy, walls):
        # Move in X; undo if collision
        self.rect.x += dx
        for w in walls:
            if self.rect.colliderect(w): self.rect.x -= dx

        # Move in Y; undo if collision
        self.rect.y += dy
        for w in walls:
            if self.rect.colliderect(w): self.rect.y -= dy

class Firework:
    def __init__(self):
        # Starting explosion point
        self.x = random.randint(100, WIDTH - 100)
        self.y = random.randint(50, HEIGHT // 2)
        # List of particles; each particle stores position, velocity, and life
        self.particles = []

        # Create 60 particles in random directions
        for _ in range(60):
            angle = random.uniform(0, 2 * math.pi)  # random angle around a circle
            speed = random.uniform(2, 6)            # random speed
            self.particles.append([
                self.x,                               # x position
                self.y,                               # y position
                math.cos(angle) * speed,              # x velocity
                math.sin(angle) * speed,              # y velocity
                random.randint(40, 60)                # life frames
            ])

    def update(self):
        # Move particles and reduce life
        for p in self.particles:
            p[0] += p[2]
            p[1] += p[3]
            p[4] -= 1

    def draw(self, surf):
        # Draw each particle still alive
        for x, y, _, _, life in self.particles:
            if life > 0:
                pygame.draw.circle(surf, GOLD, (int(x), int(y)), 3)

# ---------------- 4. HELPERS ----------------
def draw_ui(surf, health):
    # Health Bar (fixed position near top-left)
    pygame.draw.rect(surf, RED, (40, 10, 200, 20))
    pygame.draw.rect(surf, GREEN, (40, 10, int((health/MAX_HEALTH)*200), 20))
    pygame.draw.rect(surf, WHITE, (40, 10, 200, 20), 2)

def get_level_data(level_map, level_idx):
    # Convert the character-based level map into lists of rectangles
    # walls: collision
    # bushes: hide zones
    # coins: collectibles
    # floors: walkable tiles (used also for monster spawn positions)
    walls, bushes, coins, floors = [], [], [], []

    # Iterate rows and characters
    for y, row in enumerate(level_map):
        for x, char in enumerate(row):
            # Tile rect for current character
            r = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)

            # Wall tile
            if char == '#': walls.append(r)
            else:
                # Non-walls are floor
                floors.append(r)

                # Bush tile
                if char == 'B': bushes.append(r)
                # Coin spawns randomly on '.' (5% chance)
                elif char == '.' and random.random() < 0.05: # 5% chance for coin
                    coins.append(pygame.Rect(r.centerx-5, r.centery-5, 10, 10))

    # Spawn in a random bush if any exist, otherwise at (40,40)
    spawn = random.choice(bushes).topleft if bushes else (40, 40)
    return walls, bushes, coins, floors, spawn

def level_screen(level_number):
    # Display a black screen with "LEVEL X" for 2 seconds
    start_time = pygame.time.get_ticks()

    while pygame.time.get_ticks() - start_time < 2000:
        clock.tick(60)
        screen.fill((0, 0, 0))

        font = pygame.font.SysFont(None, 70)
        text = font.render(f"LEVEL {level_number}", True, WHITE)
        screen.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2)))

        pygame.display.flip()

        # Allow quitting during level screen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

def game_over_screen():
    # Game over UI loop: shows buttons until player clicks restart or quit
    while True:
        # Stop any playing "music" channel (you stop pygame.mixer.music here)
        pygame.mixer.music.stop()
        clock.tick(60)
        screen.fill((0, 0, 0))

        font_big = pygame.font.SysFont(None, 80)
        font_small = pygame.font.SysFont(None, 36)

        # "GAME OVER" title
        title = font_big.render("GAME OVER", True, RED)
        screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 80)))

        # Draw buttons
        pygame.draw.rect(screen, GREEN, restart_button, border_radius=10)
        pygame.draw.rect(screen, RED, quit_button, border_radius=10)

        # Button labels
        screen.blit(font_small.render("RESTART", True, WHITE),
                    restart_button.move(60, 15))
        screen.blit(font_small.render("QUIT", True, WHITE),
                    quit_button.move(80, 15))

        pygame.display.flip()

        # Event handling: quit or clicks
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Mouse click checks which button was clicked
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.collidepoint(event.pos):
                    return "restart"
                if quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

def game_complete_screen():
    # Stop level music and play victory music
    lvl_1_music.stop()
    victory_music.play()

    fireworks = []
    spawn_timer = 0

    # Victory screen loop with fireworks animation
    while True:
        clock.tick(60)
        screen.fill((10, 10, 30))

        # Spawn a new Firework every ~25 frames
        spawn_timer += 1
        if spawn_timer > 25:
            fireworks.append(Firework())
            spawn_timer = 0

        # Update/draw fireworks, remove if all particles dead
        for fw in fireworks[:]:
            fw.update()
            fw.draw(screen)
            if all(p[4] <= 0 for p in fw.particles):
                fireworks.remove(fw)

        # Fonts and text
        font_big = pygame.font.SysFont(None, 60)
        font_mid = pygame.font.SysFont(None, 45)
        font_small = pygame.font.SysFont(None, 36)

        title = font_big.render("CONGRATULATIONS", True, GOLD)
        subtitle = font_mid.render("YOU SURVIVED THE FOREST!", True, WHITE)

        screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 120)))
        screen.blit(subtitle, subtitle.get_rect(center=(WIDTH//2, HEIGHT//2 - 50)))

        # Buttons
        pygame.draw.rect(screen, GREEN, restart_button, border_radius=12)
        pygame.draw.rect(screen, RED, quit_button, border_radius=12)

        # Button labels
        screen.blit(font_small.render("PLAY AGAIN", True, WHITE),
                    restart_button.move(40, 15))
        screen.blit(font_small.render("QUIT", True, WHITE),
                    quit_button.move(80, 15))

        pygame.display.flip()

        # Handle events for victory screen
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
    # Plays an end "video" by loading a folder of frame images and showing them sequentially
    frame_folder = "video/end_frames"
    frames = []

    # Load each frame image, scale to screen size, store in list
    for f in sorted(os.listdir(frame_folder)):
        img = pygame.image.load(os.path.join(frame_folder, f)).convert()
        img = pygame.transform.scale(img, (WIDTH, HEIGHT))
        frames.append(img)

    # Play scary sound once
    scary_sound.play()

    # Display frames at 24 FPS
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
    # Which level we are currently playing
    level_idx = 0
    # Player created once and reused/reset between levels
    player = None
    # Camera instance for shaking effect
    camera = Camera()

    # Loop through levels until finished
    while level_idx < len(LEVELS):
        # Show "LEVEL X" intro screen
        level_screen(level_idx + 1)
        # Start looping level music (Sound loop; -1 means infinite loop)
        lvl_1_music.play(-1)

        # Build map rectangles and spawn for this level
        walls, bushes, coins, floors, spawn = get_level_data(LEVELS[level_idx], level_idx)

        # Create player first time or reset between levels
        if not player: player = Player(spawn)
        else: player.rect.topleft = spawn; player.health = MAX_HEALTH
        ghost_img = pygame.image.load(
            os.path.join("img", f"ghost{level_idx + 1}.png")
        ).convert_alpha()
        ghost_img = pygame.transform.scale(ghost_img, (30, 30))

        # Create monsters:
        # count = level_idx + 3
        # speed scales with level (2.0 + level_idx*0.8)
        monsters = [
            Monster(
                random.choice(floors).topleft,
                2.0 + (level_idx * 0.8),
                ghost_img
            )
            for _ in range(level_idx + 3)
        ]

        level_running = True
        # Run this level until coins are collected or player dies and chooses restart/quit
        while level_active := level_running:
            clock.tick(FPS)
            # Whether monster hit happened this frame (controls camera shake)
            is_touching_monster = False

            # Handle quit event
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()

            # ---------------- Logic ----------------
            # Update player movement/collisions/hiding
            player.update(walls, bushes)

            # Update each monster and check collision with player
            for m in monsters:
                m.update(player, walls)
                if m.rect.colliderect(player.rect) and not player.is_hidden:
                    # collision_sound.play()  # currently disabled (commented out)
                    player.health -= 0.5 # Damage per frame while touching monster
                    is_touching_monster = True # Trigger Shake

            # Update camera offsets based on collision
            camera.update(is_touching_monster)

            # Dead condition: play end animation and show game over menu
            if player.health <= 0:
                lvl_1_music.stop()
                play_end_animation()
                choice = game_over_screen()
                if choice == "restart":
                    return  # Exit main_game() and restart from menu

            # Coin collection:
            for c in coins[:]:
                if player.rect.colliderect(c):
                    coin_sound.play()
                    coins.remove(c)

            # If all coins collected, end the level
            if not coins:
                level_running = False
                lvl_1_music.stop()

                # If last level completed, show victory screen
                if level_idx == len(LEVELS) - 1:
                    choice = game_complete_screen()
                    if choice == "restart":
                        return   # back to main menu
                else:
                    # Otherwise go next level
                    level_idx += 1

            # ---------------- Drawing ----------------
            screen.fill((10, 10, 10))

            # Draw everything with camera shake applied
            for f in floors: pygame.draw.rect(screen, FLOOR_COLOR, camera.apply(f))
            for w in walls: pygame.draw.rect(screen, WALL_COLOR, camera.apply(w))
            for b in bushes: screen.blit(bush_img, camera.apply(b))
            for c in coins: pygame.draw.circle(screen, GOLD, camera.apply(c).center, 6)
            for m in monsters: screen.blit(m.image, camera.apply(m.rect))

            # Draw player with camera applied
            p_rect_shaken = camera.apply(player.rect)

            p_img = player_walk_right[int(player.frame_index)] if player.facing_right else player_walk_left[int(player.frame_index)]
            p_img = p_img.copy()

            # If hidden, draw semi-transparent
            if player.is_hidden:
                p_img.set_alpha(128)

            screen.blit(p_img, p_rect_shaken)

            # UI overlay (health bar)
            draw_ui(screen, player.health)
            pygame.display.flip()

def main_menu():
    # Menu loop (runs forever until quit)
    while True:
        # Draw background
        screen.blit(menu_bg, (0, 0))

        # Create the menu text
        font = pygame.font.SysFont(None, 45)
        text = font.render("PRESS SPACE TO BEGIN", True, WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT - 80))

        # Blink the text using time ticks
        if pygame.time.get_ticks() % 1000 < 500: screen.blit(text, text_rect)

        pygame.display.flip()

        # Handle menu events
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                # Start main game
                main_game()

# Entry point: start in menu when running this file directly
if __name__ == "__main__":
    main_menu()
