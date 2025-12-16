import pygame
import random
import math
import sys

# ----------------------------
# CONFIG
# ----------------------------
TILE = 32
MAP_W, MAP_H = 60, 40          # big map
SCREEN_W, SCREEN_H = 1000, 650
FPS = 60

VISION_RADIUS_TILES = 6         # "within 5 meters" vibe -> set radius in tiles
VISION_RADIUS_PX = VISION_RADIUS_TILES * TILE

PLAYER_SPEED = 220              # pixels/sec

# ----------------------------
# INIT
# ----------------------------
pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Forest Maze Demo (Pygame)")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 18)

# ----------------------------
# MAP GENERATION (maze-like)
# 0 = floor, 1 = wall (trees/bushes)
# ----------------------------
def generate_maze(w, h):
    # Make odd dimensions for nicer maze carving
    w = w if w % 2 == 1 else w - 1
    h = h if h % 2 == 1 else h - 1

    grid = [[1 for _ in range(w)] for _ in range(h)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Carve passages using randomized DFS
    start_x, start_y = 1, 1
    grid[start_y][start_x] = 0
    stack = [(start_x, start_y)]

    dirs = [(2, 0), (-2, 0), (0, 2), (0, -2)]
    while stack:
        x, y = stack[-1]
        random.shuffle(dirs)
        carved = False
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and grid[ny][nx] == 1:
                # carve wall between
                grid[y + dy // 2][x + dx // 2] = 0
                grid[ny][nx] = 0
                stack.append((nx, ny))
                carved = True
                break
        if not carved:
            stack.pop()

    # Add some extra openings so it isn't too strict
    for _ in range((w * h) // 30):
        rx = random.randrange(1, w - 1)
        ry = random.randrange(1, h - 1)
        if grid[ry][rx] == 1:
            # open if it doesn't destroy everything
            grid[ry][rx] = 0

    return grid, w, h

grid, gen_w, gen_h = generate_maze(MAP_W, MAP_H)
MAP_W, MAP_H = gen_w, gen_h

# Make sure player spawn is open
grid[1][1] = 0

# ----------------------------
# HELPERS
# ----------------------------
def clamp(v, a, b):
    return max(a, min(b, v))

def is_wall(tx, ty):
    if tx < 0 or ty < 0 or tx >= MAP_W or ty >= MAP_H:
        return True
    return grid[ty][tx] == 1

def rect_collides_walls(rect):
    # Check corners (simple but effective for tile collision)
    corners = [
        (rect.left, rect.top),
        (rect.right, rect.top),
        (rect.left, rect.bottom),
        (rect.right, rect.bottom),
    ]
    for px, py in corners:
        tx = int(px // TILE)
        ty = int(py // TILE)
        if is_wall(tx, ty):
            return True
    return False

def world_to_screen(wx, wy, camx, camy):
    return wx - camx, wy - camy

# ----------------------------
# PLAYER
# ----------------------------
player = pygame.Rect(0, 0, int(TILE * 0.55), int(TILE * 0.55))
player.center = (TILE * 1.5, TILE * 1.5)

# ----------------------------
# COLLECTIBLES (scraps)
# ----------------------------
scraps = []
def spawn_scraps(n=12):
    scraps.clear()
    tries = 0
    while len(scraps) < n and tries < 20000:
        tries += 1
        tx = random.randrange(1, MAP_W - 1)
        ty = random.randrange(1, MAP_H - 1)
        if not is_wall(tx, ty):
            r = pygame.Rect(tx * TILE + TILE//4, ty * TILE + TILE//4, TILE//2, TILE//2)
            # avoid spawn right on player
            if r.centerx - player.centerx**1 != 0:
                scraps.append(r)

spawn_scraps(15)

score = 0

# ----------------------------
# CAMERA
# ----------------------------
camx = 0
camy = 0

# ----------------------------
# VISION MASK (dark overlay with a "hole")
# ----------------------------
def make_vision_overlay():
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))  # darkness level

    # Create a soft radial hole by drawing multiple circles
    px, py = world_to_screen(player.centerx, player.centery, camx, camy)

    # soft edge
    steps = 10
    for i in range(steps):
        radius = int(VISION_RADIUS_PX * (1 - i / steps))
        alpha = int(220 * (i / steps) * 0.9)
        pygame.draw.circle(overlay, (0, 0, 0, alpha), (int(px), int(py)), radius)

    # Clear the inner core more
    pygame.draw.circle(overlay, (0, 0, 0, 0), (int(px), int(py)), int(VISION_RADIUS_PX * 0.55))
    return overlay

# ----------------------------
# MAIN LOOP
# ----------------------------
running = True
while running:
    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                grid, MAP_W, MAP_H = generate_maze(60, 40)
                grid[1][1] = 0
                player.center = (TILE * 1.5, TILE * 1.5)
                spawn_scraps(15)
                score = 0

    keys = pygame.key.get_pressed()
    vx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
    vy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])

    # normalize diagonal
    mag = math.hypot(vx, vy)
    if mag > 0:
        vx /= mag
        vy /= mag

    # move with collision (separate axes)
    dx = vx * PLAYER_SPEED * dt
    dy = vy * PLAYER_SPEED * dt

    # X axis
    oldx = player.x
    player.x += int(dx)
    if rect_collides_walls(player):
        player.x = oldx

    # Y axis
    oldy = player.y
    player.y += int(dy)
    if rect_collides_walls(player):
        player.y = oldy

    # collect scraps
    for s in scraps[:]:
        if player.colliderect(s):
            scraps.remove(s)
            score += 1

    # update camera (center on player)
    camx = player.centerx - SCREEN_W // 2
    camy = player.centery - SCREEN_H // 2

    # clamp camera to map bounds
    max_camx = MAP_W * TILE - SCREEN_W
    max_camy = MAP_H * TILE - SCREEN_H
    camx = clamp(camx, 0, max(0, max_camx))
    camy = clamp(camy, 0, max(0, max_camy))

    # ----------------------------
    # DRAW
    # ----------------------------
    screen.fill((18, 28, 18))

    # draw tiles
    # (simple colors; later you can replace with sprites)
    start_tx = int(camx // TILE)
    start_ty = int(camy // TILE)
    end_tx = int((camx + SCREEN_W) // TILE) + 2
    end_ty = int((camy + SCREEN_H) // TILE) + 2

    for ty in range(start_ty, end_ty):
        for tx in range(start_tx, end_tx):
            if 0 <= tx < MAP_W and 0 <= ty < MAP_H:
                wx = tx * TILE
                wy = ty * TILE
                sx, sy = world_to_screen(wx, wy, camx, camy)

                if grid[ty][tx] == 1:
                    # trees/bush walls
                    pygame.draw.rect(screen, (20, 60, 25), (sx, sy, TILE, TILE))
                    # add rough “foliage” variation
                    pygame.draw.circle(screen, (25, 85, 35), (sx + TILE//2, sy + TILE//2), TILE//3)
                else:
                    pygame.draw.rect(screen, (25, 40, 25), (sx, sy, TILE, TILE))

    # draw scraps
    for s in scraps:
        sx, sy = world_to_screen(s.x, s.y, camx, camy)
        pygame.draw.rect(screen, (180, 170, 80), (sx, sy, s.w, s.h), border_radius=6)

    # draw player (torn office guy placeholder)
    psx, psy = world_to_screen(player.x, player.y, camx, camy)
    pygame.draw.rect(screen, (200, 200, 210), (psx, psy, player.w, player.h), border_radius=6)
    # "sword" small line
    pygame.draw.line(screen, (220, 220, 230),
                     (psx + player.w, psy + player.h//2),
                     (psx + player.w + 18, psy + player.h//2), 3)

    # vision overlay
    overlay = make_vision_overlay()
    screen.blit(overlay, (0, 0))

    # UI
    ui1 = font.render(f"Scraps: {score} / {score + len(scraps)}   |  R = regenerate map", True, (240, 240, 240))
    ui2 = font.render("Move: WASD / Arrow Keys  |  Vision: limited radius (dark outside)", True, (240, 240, 240))
    screen.blit(ui1, (14, 10))
    screen.blit(ui2, (14, 32))

    if len(scraps) == 0:
        win = font.render("You collected everything! Press R to generate a new forest maze.", True, (255, 255, 255))
        screen.blit(win, (14, 56))

    pygame.display.flip()

pygame.quit()
sys.exit()
