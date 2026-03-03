import pygame
import os


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, texture_path: str = None, size: tuple = (40, 40)):
        """Obstacle con soporte opcional de sprite.

        texture_path: nombre de archivo dentro de imagenes/ (p. ej. 'obstaculo.png').
        size: (w,h) tamaño de la caja/imagen final.
        """
        super().__init__()
        w, h = size

        assets_dir = os.path.join(os.path.dirname(__file__), 'imagenes')
        texture = None

        # si se proporcionó ruta específica, intentar cargarla
        if texture_path:
            candidate = os.path.join(assets_dir, texture_path)
            if os.path.exists(candidate):
                try:
                    texture = pygame.image.load(candidate).convert_alpha()
                except Exception:
                    texture = None

        # si no hay texture todavía, intentar nombres por defecto
        if texture is None:
            for fname in ('obstaculo.png', 'obstacle.png'):
                path = os.path.join(assets_dir, fname)
                if os.path.exists(path):
                    try:
                        texture = pygame.image.load(path).convert_alpha()
                        texture_path = fname
                        break
                    except Exception:
                        texture = None

        if texture:
            # escalar la textura al tamaño indicado
            try:
                self.image = pygame.transform.smoothscale(texture, (w, h)).convert_alpha()
            except Exception:
                self.image = pygame.Surface((w, h), pygame.SRCALPHA)
                self.image.blit(texture, (0, 0))
        else:
            # fallback: cuadro rojo
            self.image = pygame.Surface((w, h))
            self.image.fill((255, 0, 0))

        self.rect = self.image.get_rect(topleft=(x, y))
        # exponer metadatos para persistencia
        self.texture_path = texture_path
        self.size = (w, h)

if __name__ == "__main__":
    pass