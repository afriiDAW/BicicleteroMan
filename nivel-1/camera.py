import math


class Camera:
    def __init__(self, screen_width, level_width):
        # usar float para offset interno para suavizado
        self.offset_x = 0.0
        self.screen_width = screen_width
        self.level_width = level_width
        # velocidad de suavizado (mayor = cámara más reactiva)
        self.smooth_speed = 12.0

    def update(self, target, dt: float = 1/60):
        """Actualizar la cámara para seguir al objetivo con suavizado.

        target: objeto con `rect.centerx` (por ejemplo Player)
        dt: tiempo en segundos transcurrido desde el último frame
        """
        # offset objetivo (float)
        target_offset = float(target.rect.centerx) - (self.screen_width / 2.0)

        # límites del target_offset
        min_off = 0.0
        max_off = max(0.0, float(self.level_width - self.screen_width))
        if target_offset < min_off:
            target_offset = min_off
        if target_offset > max_off:
            target_offset = max_off

        # suavizado exponencial dependiente de dt (framerate-independiente)
        # alpha en (0,1): cuánto acercarse al objetivo este frame
        alpha = 1.0 - math.exp(-self.smooth_speed * max(0.0, dt))
        self.offset_x += (target_offset - self.offset_x) * alpha

    def apply(self, rect):
        # devolver un rect movido por el offset (usar rounding al blit para evitar jitter)
        ox = int(round(self.offset_x))
        return rect.move(-ox, 0)
