import pygame
from config import ANCHO, ALTO, AZUL

class Jugador:
    def __init__(self):
        self.rect = pygame.Rect(ANCHO//3, ALTO//2, 80, 30)
        self.velocidad = 5
        self.vidas = 3
        self.invulnerable = False
        self.inv_timer = 0
        self.tiempo_inv = 1500

    def mover(self, teclas, avance_final):
        if avance_final:
            return

        if teclas[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.velocidad
        if teclas[pygame.K_DOWN] and self.rect.bottom < ALTO:
            self.rect.y += self.velocidad

    def daño(self):
        if not self.invulnerable:
            self.vidas -= 1
            self.rect.x, self.rect.y = 100, ALTO//2
            self.invulnerable = True
            self.inv_timer = pygame.time.get_ticks()

    def actualizar_invulnerabilidad(self):
        if self.invulnerable:
            if pygame.time.get_ticks() - self.inv_timer > self.tiempo_inv:
                self.invulnerable = False

    def dibujar(self, ventana):
        pygame.draw.rect(ventana, AZUL, self.rect)