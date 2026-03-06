import pygame
import os

# ---------------- FUNCIONES DE UTILIDAD ----------------
def load_texture(assets_dir, texture_path=None, fallback_names=None):
    """Carga una textura con fallbacks opcionales."""
    texture = None
    
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

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, texture_path: str = None, size: tuple = (40, 40)):
        """Obstáculo con soporte de sprite y tamaño personalizable."""
        super().__init__()
        w, h = size
        
        assets_dir = os.path.join(os.path.dirname(__file__), 'imagenes')
        texture, final_path = load_texture(assets_dir, texture_path, ['obstaculo.png', 'obstacle.png'])
        
        if texture:
            try:
                self.image = pygame.transform.smoothscale(texture, (w, h)).convert_alpha()
            except Exception:
                self.image = pygame.Surface((w, h), pygame.SRCALPHA)
                self.image.blit(texture, (0, 0))
        else:
            # Fallback: cuadro rojo
            self.image = pygame.Surface((w, h))
            self.image.fill((255, 0, 0))
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.texture_path = final_path
        self.size = (w, h)

if __name__ == "__main__":
    pass