import pygame
import os

# ---------------- FUNCIONES DE UTILIDAD ----------------  
def load_texture_with_fallbacks(assets_dir, texture_path=None, fallback_names=None):
    """Carga una textura con fallbacks opcionales (versión para powerups)."""
    # Intentar ruta específica primero
    if texture_path:
        candidate = os.path.join(assets_dir, texture_path)
        if os.path.exists(candidate):
            try:
                return pygame.image.load(candidate).convert_alpha(), texture_path
            except Exception:
                pass
    
    # Intentar nombres de fallback
    if fallback_names:
        for fname in fallback_names:
            path = os.path.join(assets_dir, fname)
            if os.path.exists(path):
                try:
                    return pygame.image.load(path).convert_alpha(), fname
                except Exception:
                    continue
    
    return None, texture_path

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, texture_path: str = None, size: tuple = (30, 30), extend_up: float = 0.25):
        """PowerUp con sprite opcional y extensión hacia arriba.
        
        extend_up: porcentaje adicional de altura para alargar el sprite hacia arriba.
        """
        super().__init__()
        w, h = size
        display_h = max(1, int(h * (1.0 + float(extend_up))))
        
        assets_dir = os.path.join(os.path.dirname(__file__), 'imagenes')
        fallback_names = ['powerup.png', 'powerup_green.png', 'powerup1.png']
        texture, final_path = load_texture_with_fallbacks(assets_dir, texture_path, fallback_names)
        
        if texture:
            try:
                self.image = pygame.transform.smoothscale(texture, (w, display_h)).convert_alpha()
            except Exception:
                self.image = pygame.Surface((w, display_h), pygame.SRCALPHA)
                self.image.blit(texture, (0, 0))
        else:
            # Fallback: verde
            self.image = pygame.Surface((w, display_h), pygame.SRCALPHA)
            self.image.fill((0, 255, 0))
        
        # Posicionar para que se alargue hacia arriba manteniendo la base
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.bottom = y + h
        
        # Metadatos para persistencia
        self.texture_path = final_path
        self.size = (w, h)
        self.extend_up = float(extend_up)


if __name__ == "__main__":
    pass