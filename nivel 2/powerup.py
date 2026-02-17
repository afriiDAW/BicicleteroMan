import pygame
import random
from config import ANCHO, ALTO, VERDE

class PowerUp:
    def __init__(self):
        self.rect = pygame.Rect(
            random.randint(300, ANCHO),
            random.randint(0, ALTO-30),
            30, 30
        )

    def mover(self):
        self.rect.x -= 2
        if self.rect.right < 0:
            self.rect.x = ANCHO + random.randint(0, 200)

    def dibujar(self, ventana):
        pygame.draw.rect(ventana, VERDE, self.rect)