import random
from assets.images import monster_img

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

        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

    def draw(self, surf):
        surf.blit(self.image, self.rect)
