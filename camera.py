class Camera:
    def __init__(self, screen_width, level_width):
        self.offset_x = 0
        self.screen_width = screen_width
        self.level_width = level_width

    def update(self, target):
        # El jugador empieza a mover la cámara cuando pasa la mitad de la pantalla
        self.offset_x = target.rect.centerx - self.screen_width // 2

        # Límites de la cámara
        if self.offset_x < 0:
            self.offset_x = 0
        if self.offset_x > self.level_width - self.screen_width:
            self.offset_x = self.level_width - self.screen_width

    def apply(self, rect):
        return rect.move(-self.offset_x, 0)
