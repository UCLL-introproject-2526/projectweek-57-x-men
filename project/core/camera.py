import random
import pygame

class Camera:
    def __init__(self):
        self.shake = 0
        self.zoom = 1.0

    def apply(self, screen, surface):
        w, h = surface.get_size()
        scaled = pygame.transform.scale(surface, (int(w*self.zoom), int(h*self.zoom)))
        ox = random.randint(-self.shake, self.shake)
        oy = random.randint(-self.shake, self.shake)
        screen.blit(scaled, (ox, oy))
