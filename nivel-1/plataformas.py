import pygame
import os
import math

# ---------------- FUNCIONES DE UTILIDAD ----------------
def load_platform_texture(assets_dir, texture_path=None):
    """Carga una textura para plataforma con fallback automático."""
    texture = None
    
    # Intentar ruta proporcionada
    if texture_path:
        candidate = os.path.join(assets_dir, texture_path)
        if os.path.exists(candidate):
            try:
                return pygame.image.load(candidate).convert_alpha()
            except Exception:
                pass
    
    # Fallback a cesped2.png por compatibilidad
    fallback_path = os.path.join(assets_dir, 'cesped2.png')
    if os.path.exists(fallback_path):
        try:
            return pygame.image.load(fallback_path).convert_alpha()
        except Exception:
            pass
            
    return None

def create_platform_surface(w, h, texture=None, tile=False):
    """Crea la superficie de la plataforma con textura o color sólido."""
    if texture:
        if tile:
            # Crear superficie transparente y rellenar en mosaico
            surface = pygame.Surface((w, h), pygame.SRCALPHA)
            tw, th = texture.get_size()
            if tw > 0 and th > 0:
                for yy in range(0, h, th):
                    for xx in range(0, w, tw):
                        surface.blit(texture, (xx, yy))
            else:
                surface.fill((139, 69, 19))  # Fallback madera
            return surface
        else:
            # Estirar textura al tamaño exacto
            return pygame.transform.smoothscale(texture, (w, h)).convert_alpha()
    else:
        # Fallback: color sólido madera
        surface = pygame.Surface((w, h))
        surface.fill((139, 69, 19))
        return surface


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, texture_path: str = None, tile: bool = False):
        """Plataforma opcionalmente texturizada.
        
        texture_path: nombre de archivo dentro de carpeta imagenes/
        tile: si True, repite la textura en mosaico; si False, estira para cubrir (w,h)
        """
        super().__init__()
        
        assets_dir = os.path.join(os.path.dirname(__file__), 'imagenes')
        texture = load_platform_texture(assets_dir, texture_path)
        
        self.image = create_platform_surface(w, h, texture, tile)
        
        # Guardar metadatos para persistencia
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