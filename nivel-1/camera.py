import math

# ---------------- CONFIGURACIÓN DE CÁMARA ----------------
DEFAULT_SMOOTH_SPEED = 12.0  # Mayor valor = cámara más reactiva

class Camera:
    """Cámara con seguimiento suavizado framerate-independiente."""
    
    def __init__(self, screen_width, level_width):
        self.offset_x = 0.0  # Usar float para suavizado preciso
        self.screen_width = screen_width
        self.level_width = level_width
        self.smooth_speed = DEFAULT_SMOOTH_SPEED

    def update(self, target, dt: float = 1/60):
        """Actualiza la cámara para seguir al objetivo con suavizado.

        Args:
            target: Objeto con `rect.centerx` (ej. Player)
            dt: Tiempo transcurrido en segundos desde el último frame
        """
        # Calcular offset objetivo
        target_offset = float(target.rect.centerx) - (self.screen_width / 2.0)
        
        # Aplicar límites del nivel
        min_offset = 0.0
        max_offset = max(0.0, float(self.level_width - self.screen_width))
        target_offset = max(min_offset, min(target_offset, max_offset))
        
        # Suavizado exponencial framerate-independiente
        alpha = 1.0 - math.exp(-self.smooth_speed * max(0.0, dt))
        self.offset_x += (target_offset - self.offset_x) * alpha

    def apply(self, rect):
        """Aplica el offset de la cámara a un rect.
        
        Returns:
            Nuevo rect desplazado por el offset de la cámara
        """
        offset_rounded = int(round(self.offset_x))
        return rect.move(-offset_rounded, 0)
    
    def reset(self):
        """Reinicia la posición de la cámara."""
        self.offset_x = 0.0
