import pygame
import os
import math


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, texture_path: str = None, tile: bool = False):
        """Platform opcionalmente texturizada.

        texture_path: nombre de archivo dentro de carpeta imagenes/ (por ejemplo 'plataforma.png' o 'suelo_tile.png').
        tile: si True, repetirá la textura en mosaico; si False, la estirará para cubrir (w,h).
        """
        super().__init__()

        assets_dir = os.path.join(os.path.dirname(__file__), 'imagenes')
        texture = None

        if texture_path:
            candidate = os.path.join(assets_dir, texture_path)
            if os.path.exists(candidate):
                try:
                    texture = pygame.image.load(candidate).convert_alpha()
                except Exception:
                    texture = None

        # si no se proporcionó texture_path, intentar por compatibilidad con 'plataforma.png'
        if texture is None:
            platform_path = os.path.join(assets_dir, 'plataforma.png')
            if os.path.exists(platform_path):
                try:
                    texture = pygame.image.load(platform_path).convert_alpha()
                except Exception:
                    texture = None

        if texture:
            if tile:
                # crear superficie transparente y rellenar en mosaico
                self.image = pygame.Surface((w, h), pygame.SRCALPHA)
                tw, th = texture.get_size()
                if tw == 0 or th == 0:
                    # safety fallback
                    self.image.fill((139, 69, 19))
                else:
                    for yy in range(0, h, th):
                        for xx in range(0, w, tw):
                            self.image.blit(texture, (xx, yy))
            else:
                # estirar la textura exactamente al tamaño de la plataforma
                self.image = pygame.transform.smoothscale(texture, (w, h)).convert_alpha()
        else:
            # fallback: color sólido madera
            self.image = pygame.Surface((w, h))
            self.image.fill((139, 69, 19))

        # guardar metadatos para poder persistir/leer texturas desde JSON
        self.texture_path = texture_path
        self.tile = bool(tile)

        self.rect = self.image.get_rect(topleft=(x, y))


class MovingPlatform(Platform):
    """Plataforma que se mueve en un eje (horizontal o vertical) en modo ping-pong.

    axis: 'x' o 'y'
    range_px: distancia máxima desde la posición inicial
    speed: píxeles por frame
    """
    def __init__(self, x, y, w, h, axis='x', range_px=120, speed=1.0, texture_path: str = None, tile: bool = False):
        # pasar los parámetros de textura hacia el constructor de Platform
        super().__init__(x, y, w, h, texture_path=texture_path, tile=tile)

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