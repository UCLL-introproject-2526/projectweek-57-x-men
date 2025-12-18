import pygame
import random
from setting import WIDTH, HEIGHT

class Camera:
    def __init__(self):
        self.shake = 0
        self.zoom = 1.0

    def apply(self, surface):
        w, h = surface.get_size()
        scaled = pygame.transform.scale(surface, (int(w*self.zoom), int(h*self.zoom)))
        ox = random.randint(-self.shake, self.shake)
        oy = random.randint(-self.shake, self.shake)
        screen = pygame.display.get_surface()
        screen.blit(scaled, (ox, oy))
