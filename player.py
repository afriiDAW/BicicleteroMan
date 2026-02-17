import pygame

# ---------------- CONSTANTES ----------------
GRAVITY = 0.8
JUMP_FORCE = -14

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Sprite
        self.image = pygame.Surface((40, 60))
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect(topleft=(x, y))

        # Movimiento
        self.base_speed = 5
        self.speed = self.base_speed
        # tiempo (ms) en el que termina el efecto de velocidad actual
        self.speed_end_time = 0

        self.vel_y = 0
        self.on_ground = False

    def update(self, platforms, level_width):
        """Actualizar posición y manejar colisiones con plataformas.

        platforms: lista de objetos con atributo rect
        level_width: ancho total del nivel (para limitar posición x)
        """
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0

        # Movimiento horizontal
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.speed

        # Salto
        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
            self.vel_y = JUMP_FORCE
            self.on_ground = False

        # Aplicar gravedad
        self.vel_y += GRAVITY
        dy += self.vel_y

        # Mover en x y resolver colisiones separadas
        # Movimiento horizontal
        self.rect.x += dx
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if dx > 0:  # moviéndose a la derecha
                    self.rect.right = platform.rect.left
                elif dx < 0:  # moviéndose a la izquierda
                    self.rect.left = platform.rect.right

        # Movimiento vertical
        self.rect.y += dy
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # caída sobre la plataforma
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    # golpeando cabeza
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0

        # Limitar dentro del ancho del nivel
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > level_width:
            self.rect.right = level_width

        # Manejar temporizadores de velocidad
        now = pygame.time.get_ticks()
        if self.speed != self.base_speed and now >= self.speed_end_time:
            self.speed = self.base_speed

    # ----- Efectos de velocidad -----
    def speed_up(self, duration_seconds: float, factor: float = 1.8):
        """Aumenta la velocidad durante `duration_seconds` segundos.

        Si ya hay un efecto activo, se alarga solo si el nuevo tiempo es mayor.
        ``factor`` multiplica la `base_speed`.
        """
        now = pygame.time.get_ticks()
        end_time = now + int(duration_seconds * 1000)
        # aplicar nuevo efecto solo si alarga o no hay efecto
        if end_time > self.speed_end_time:
            self.speed = self.base_speed * factor
            self.speed_end_time = end_time

    def slow_down(self, duration_seconds: float, factor: float = 0.5):
        """Reduce la velocidad durante `duration_seconds` segundos.

        ``factor`` es multiplicador sobre `base_speed` (p. ej. 0.5 para mitad de velocidad).
        """
        now = pygame.time.get_ticks()
        end_time = now + int(duration_seconds * 1000)
        if end_time > self.speed_end_time:
            self.speed = self.base_speed * factor
            self.speed_end_time = end_time


