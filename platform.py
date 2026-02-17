import pygame
import math


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill((139, 69, 19))
        self.rect = self.image.get_rect(topleft=(x, y))


class MovingPlatform(Platform):
    """Plataforma que se mueve en un eje (horizontal o vertical) en modo ping-pong.

    axis: 'x' o 'y'
    range_px: distancia máxima desde la posición inicial
    speed: píxeles por frame
    """
    def __init__(self, x, y, w, h, axis='x', range_px=120, speed=1.0):
        super().__init__(x, y, w, h)
        # visual distinctiva
        self.image = pygame.Surface((w, h))
        self.image.fill((100, 149, 237))  # azul claro

        self.start_x = x
        self.start_y = y
        self.axis = axis
        self.range = range_px
        self.speed = speed

        self.offset = 0
        self.direction = 1

    def update(self):
        # actualizar offset
        self.offset += self.direction * self.speed
        if abs(self.offset) >= self.range:
            # clamp y cambia dirección
            self.offset = max(-self.range, min(self.offset, self.range))
            self.direction *= -1

        if self.axis == 'x':
            self.rect.x = int(self.start_x + self.offset)
        else:
            self.rect.y = int(self.start_y + self.offset)


if __name__ == "__main__":
    pass