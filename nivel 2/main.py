import pygame
from config import ANCHO, ALTO
from nivel import Nivel

pygame.init()

VENTANA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Camino a la escuela")

clock = pygame.time.Clock()
nivel = Nivel()
activo = True

while activo:
    clock.tick(60)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            activo = False

    nivel.actualizar()
    nivel.dibujar(VENTANA)

    if nivel.jugador.vidas <= 0:
        print("Game Over")
        activo = False

    pygame.display.flip()

pygame.quit()
