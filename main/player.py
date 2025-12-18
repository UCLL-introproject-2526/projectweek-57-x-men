import pygame
import os
from setting import TILE_SIZE
import player

player_walk_right = []
player_walk_left = []
bush_img = None

def load_assets(tile_size=TILE_SIZE):
    global player_walk_right, player_walk_left, bush_img
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


class Player:
    def __init__(self):
        self.image = player_walk_right[0]
        self.rect = self.image.get_rect(topleft=(TILE_SIZE*2, TILE_SIZE*2))
        self.speed = 4
        self.hidden = False
        self.health = 100

        self.hitbox = self.rect.copy()
        self.hitbox.inflate_ip(-12, -12)

        self.facing_right = True

        # Animation
        self.walk_frames_right = player_walk_right
        self.walk_frames_left = player_walk_left
        self.frame_index = 0
        self.animation_speed = 0.15

    def update(self, keys, walls):
        dx = dy = 0
        moving = False

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= self.speed
            self.facing_right = True
            moving = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += self.speed
            self.facing_right = False
            moving = True
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= self.speed
            moving = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += self.speed
            moving = True

        self.move(dx, dy, walls)

        if moving:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.walk_frames_right):
                self.frame_index = 0
            self.image = self.walk_frames_right[int(self.frame_index)] if self.facing_right else self.walk_frames_left[int(self.frame_index)]
        else:
            self.image = self.walk_frames_right[0] if self.facing_right else self.walk_frames_left[0]

    def move(self, dx, dy, walls):
        self.hitbox.x += dx
        for w in walls:
            if self.hitbox.colliderect(w):
                if dx > 0: self.hitbox.right = w.left
                elif dx < 0: self.hitbox.left = w.right

        self.hitbox.y += dy
        for w in walls:
            if self.hitbox.colliderect(w):
                if dy > 0: self.hitbox.bottom = w.top
                elif dy < 0: self.hitbox.top = w.bottom

        self.rect.center = self.hitbox.center 

    def draw(self, surf):
        if self.hidden:
            img = self.image.copy()
            img.set_alpha(120)
            surf.blit(img, self.rect)
        else:
            surf.blit(self.image, self.rect)
