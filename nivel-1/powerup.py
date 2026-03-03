import pygame
import os


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, texture_path: str = None, size: tuple = (30, 30), extend_up: float = 0.25):
        """PowerUp con sprite opcional.

        texture_path: nombre de archivo dentro de imagenes/ (ej. 'powerup.png')
        size: (w,h) tamaño visual nominal del powerup (ancho, alto)
        extend_up: porcentaje adicional de altura para alargar el sprite hacia arriba
                   (por ejemplo 0.25 añade un 25% de altura encima).
        """
        super().__init__()
        w, h = size
        # altura visual final (alargada hacia arriba)
        display_h = max(1, int(h * (1.0 + float(extend_up))))

        assets_dir = os.path.join(os.path.dirname(__file__), 'imagenes')
        texture = None

        # intentar cargar la ruta proporcionada
        if texture_path:
            candidate = os.path.join(assets_dir, texture_path)
            if os.path.exists(candidate):
                try:
                    texture = pygame.image.load(candidate).convert_alpha()
                except Exception:
                    texture = None

        # intentar nombres por defecto si no se cargó textura
        if texture is None:
            for fname in ('powerup.png', 'powerup_green.png', 'powerup1.png'):
                p = os.path.join(assets_dir, fname)
                if os.path.exists(p):
                    try:
                        texture = pygame.image.load(p).convert_alpha()
                        texture_path = fname
                        break
                    except Exception:
                        texture = None

        if texture:
            try:
                # escalamos la textura a la anchura solicitada y a la altura extendida
                self.image = pygame.transform.smoothscale(texture, (w, display_h)).convert_alpha()
            except Exception:
                self.image = pygame.Surface((w, display_h), pygame.SRCALPHA)
                self.image.blit(texture, (0, 0))
        else:
            self.image = pygame.Surface((w, display_h), pygame.SRCALPHA)
            self.image.fill((0, 255, 0))

        # colocamos el sprite de forma que su base (bottom) quede donde
        # originalmente estaría con la altura nominal h; así el sprite "se
        # alarga hacia arriba" manteniendo la posición de la base.
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.bottom = y + h
        self.texture_path = texture_path
        self.size = (w, h)
        self.extend_up = float(extend_up)


if __name__ == "__main__":
    pass