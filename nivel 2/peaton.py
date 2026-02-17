import pygame
import random
from config import ANCHO, ALTURA_CARRIL, ROJO

class Peaton:
    def __init__(self, carril, largo):
        self.rect = pygame.Rect(
            random.randint(300, ANCHO),
            carril * ALTURA_CARRIL,
            largo,
            ALTURA_CARRIL
        )

    def mover(self, velocidad):
        self.rect.x -= velocidad

    def dibujar(self, ventana):
        pygame.draw.rect(ventana, ROJO, self.rect)