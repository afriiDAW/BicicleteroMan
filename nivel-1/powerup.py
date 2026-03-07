import pygame
import os
import math

# ---------------- FUNCIONES DE UTILIDAD ----------------  
def load_animated_textures(assets_dir, texture_base_name=None):
    """Carga texturas de animación para powerups (3 frames)."""
    textures = []
    
    if texture_base_name:
        # Intentar cargar frames específicos (ej: powerup_1.png, powerup_2.png, powerup_3.png)
        base = texture_base_name.replace('.png', '')
        for i in range(1, 4):
            path = os.path.join(assets_dir, f"{base}_{i}.png")
            if os.path.exists(path):
                try:
                    texture = pygame.image.load(path).convert_alpha()
                    textures.append(texture)
                except Exception:
                    continue
    
    # Si no se encontraron frames específicos, intentar nombres por defecto
    if len(textures) == 0:
        fallback_names = ['powerup1.png', 'powerup1.5.png', 'powerup2.png', 'powerup3.png']
        for fname in fallback_names:
            path = os.path.join(assets_dir, fname)
            if os.path.exists(path):
                try:
                    texture = pygame.image.load(path).convert_alpha()
                    textures.append(texture)
                except Exception:
                    continue
    
    # Si aún no hay texturas, intentar una sola textura y replicarla
    if len(textures) == 0:
        single_names = ['powerup.png', 'powerup_green.png']
        for fname in single_names:
            path = os.path.join(assets_dir, fname)
            if os.path.exists(path):
                try:
                    texture = pygame.image.load(path).convert_alpha()
                    textures = [texture, texture, texture]  # Replicar la misma textura
                    break
                except Exception:
                    continue
    
    return textures

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
        """PowerUp con sprite animado opcional y extensión hacia arriba.
        
        extend_up: porcentaje adicional de altura para alargar el sprite hacia arriba.
        """
        super().__init__()
        w, h = size
        display_h = max(1, int(h * (1.0 + float(extend_up))))
        
        assets_dir = os.path.join(os.path.dirname(__file__), 'imagenes')
        
        # Cargar texturas para animación
        self.textures = load_animated_textures(assets_dir, texture_path)
        
        if self.textures:
            # Escalar todas las texturas
            self.scaled_textures = []
            for texture in self.textures:
                try:
                    scaled = pygame.transform.smoothscale(texture, (w, display_h)).convert_alpha()
                    self.scaled_textures.append(scaled)
                except Exception:
                    surface = pygame.Surface((w, display_h), pygame.SRCALPHA)
                    surface.blit(texture, (0, 0))
                    self.scaled_textures.append(surface)
        else:
            # Fallback: crear 3 variaciones de color verde
            self.scaled_textures = []
            colors = [(0, 255, 0), (50, 255, 50), (100, 255, 100)]  # Verde oscuro a claro
            for color in colors:
                surface = pygame.Surface((w, display_h), pygame.SRCALPHA)
                surface.fill(color)
                self.scaled_textures.append(surface)
        
        # Animación
        self.current_frame = 0
        self.animation_speed = 0.15  # Tiempo entre frames en segundos
        self.animation_timer = 0.0
        self.image = self.scaled_textures[self.current_frame]
        
        # Posicionar para que se alargue hacia arriba manteniendo la base
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.bottom = y + h
        
        # Variables para flotación
        self.float_y = y  # Posición Y inicial para flotación
        self.float_amplitude = 8  # Amplitud del movimiento (píxeles)
        self.float_speed = 2.0  # Velocidad de flotación
        self.float_time = 0.0  # Tiempo transcurrido
        
        # Metadatos para persistencia
        self.texture_path = texture_path
        self.size = (w, h)
        self.extend_up = float(extend_up)
        
    def update(self, dt=0.016):
        """Actualiza la animación y el efecto de flotación del powerup."""
        # Actualizar animación
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0.0
            self.current_frame = (self.current_frame + 1) % len(self.scaled_textures)
            self.image = self.scaled_textures[self.current_frame]
        
        # Actualizar flotación
        self.float_time += dt
        # Usar seno para crear movimiento suave de arriba a abajo
        offset_y = math.sin(self.float_time * self.float_speed) * self.float_amplitude
        self.rect.bottom = self.float_y + self.size[1] + offset_y


if __name__ == "__main__":
    pass