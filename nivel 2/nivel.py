import pygame
import random

from config import *
from jugador import Jugador
from peaton import Peaton
from powerup import PowerUp

class Nivel:
    def __init__(self):
        self.jugador = Jugador()
        self.peatones = self.generar_peatones()
        self.powerups = [PowerUp() for _ in range(2)]

        self.power_activo = False
        self.power_timer = 0

        self.t_inicio = pygame.time.get_ticks()
        self.duracion = 60000
        self.avance_final = False

    def generar_peatones(self):
        peatones = []

        carriles = list(range(NUM_CARRILES))
        random.shuffle(carriles)
        carriles.pop()

        carril_bus = random.choice(carriles)

        for c in carriles:
            largo = 200 if c == carril_bus else 100
            peatones.append(Peaton(c, largo))

        return peatones

    def actualizar(self):
        tiempo = pygame.time.get_ticks() - self.t_inicio

        if tiempo >= self.duracion:
            self.avance_final = True

        teclas = pygame.key.get_pressed()
        self.jugador.mover(teclas, self.avance_final)
        self.jugador.actualizar_invulnerabilidad()

        vel = 3 + int(4 * tiempo / self.duracion)

        for p in self.peatones:
            p.mover(vel)
            if self.jugador.rect.colliderect(p.rect):
                self.jugador.daño()

        for pu in self.powerups:
            pu.mover()
            if self.jugador.rect.colliderect(pu.rect):
                self.power_activo = True
                self.power_timer = pygame.time.get_ticks()
                self.jugador.velocidad = 8
                self.powerups.remove(pu)

        if self.power_activo:
            if pygame.time.get_ticks() - self.power_timer > 3000:
                self.power_activo = False
                self.jugador.velocidad = 5

    def dibujar(self, ventana):
        ventana.fill(BLANCO)

        self.jugador.dibujar(ventana)

        for p in self.peatones:
            p.dibujar(ventana)

        for pu in self.powerups:
            pu.dibujar(ventana)

        fuente = pygame.font.SysFont(None, 36)
        texto = fuente.render(f"Vidas: {self.jugador.vidas}", True, NEGRO)
        ventana.blit(texto, (10, 10))