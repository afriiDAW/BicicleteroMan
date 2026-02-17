import pygame
import random

# Física básica
GRAVITY = 0.8
JUMP_FORCE = -12


class Thief(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 60))
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect(topleft=(x, y))

        # Movimiento
        # Aumentamos la velocidad base para que el ladrón sea más rápido
        self.base_speed = 2.4
        self.speed = self.base_speed

        # Física vertical
        self.vel_y = 0
        self.on_ground = False

        # IA / rutas
        self.route = None
        self.next_route_change = 0
        self.choose_route()

        # temporizador para saltos automáticos en rutas zigzag
        self.last_jump_time = 0

    def choose_route(self):
        """Selecciona una ruta aleatoria: 'ground', 'platforms', 'zigzag'.
        Cada ruta dura un intervalo aleatorio.
        """
        self.route = random.choice(["ground", "platforms", "zigzag"]) 
        self.next_route_change = pygame.time.get_ticks() + random.randint(2500, 7000)

    def update(self, platforms: list, level_width: int, player) -> bool:
        """Actualiza la posición del ladrón.

        platforms: lista de objetos con attribute `rect`.
        player: instancia de Player para consultar su velocidad actual.
        Devuelve True si el ladrón llega al final del nivel (escapa).
        """
        now = pygame.time.get_ticks()

        # Cambiar ruta si toca
        if now >= self.next_route_change:
            self.choose_route()

        # Movimiento horizontal: ajustar para ser ligeramente más rápido que la
        # velocidad base del jugador (ignorando powerups/slow) para que los
        # powerups afecten solo al jugador.
        # ahora el ladrón irá ~8% más rápido que la velocidad base del jugador
        base = max(0.1, player.base_speed * 1.08)
        if self.route == "ground":
            self.speed = base
        elif self.route == "platforms":
            self.speed = base * 1.03
        elif self.route == "zigzag":
            self.speed = base * 1.08

        # Reducir la velocidad final un 10% para ajustar dificultad
        self.speed *= 0.9

        self.rect.x += self.speed

        # Decide saltos
        # Si la ruta es 'platforms', intenta subir a la próxima plataforma que esté
        # ligeramente por encima y cerca.
        if self.on_ground:
            if self.route == "platforms":
                target = None
                for p in platforms:
                    # plataforma por delante entre 20 y 220 px
                    if p.rect.left > self.rect.right and p.rect.left - self.rect.right < 220:
                        # preferir plataformas más altas (y no la plataforma del suelo muy ancha)
                        if p.rect.top < self.rect.top - 10:
                            target = p
                            break
                if target:
                    # si estamos cerca del borde, saltar
                    if target.rect.left - self.rect.right < 60:
                        self.vel_y = JUMP_FORCE
                        self.on_ground = False
            elif self.route == "zigzag":
                # saltos frecuentes pero con cooldown
                if now - self.last_jump_time > 700 and random.random() < 0.45:
                    self.vel_y = JUMP_FORCE
                    self.on_ground = False
                    self.last_jump_time = now
            else:
                # ground: puede saltar puntualmente para esquivar obstáculos (aleatorio pequeño)
                if random.random() < 0.02:
                    self.vel_y = JUMP_FORCE
                    self.on_ground = False

        # Aplicar gravedad y movimiento vertical
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        # Resolver colisiones con plataformas (vertical)
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0

        # Límite final del nivel: si llega, indica que escapó
        if self.rect.right >= level_width:
            return True

        # Evitar caer fuera del mundo (por si)
        if self.rect.top > 1000:
            # reiniciar un poco arriba del suelo para evitar que desaparezca
            self.rect.y = 300
            self.vel_y = 0

        return False


if __name__ == "__main__":
    pass