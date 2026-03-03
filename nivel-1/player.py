import pygame
import os

# ---------------- CONSTANTES ----------------
GRAVITY = 0.8
JUMP_FORCE = -14

# Escala visual del sprite (no afecta a la hitbox).
# 1 = tamaño base 40x60; 2 = 80x120, etc. Cambia según prefieras.
DISPLAY_SCALE = 1.35


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # tamaño base de la hitbox y de los frames fuente
        base_w, base_h = 40, 60

        # hitbox para físicas (se mantiene en base_w x base_h)
        self.rect = pygame.Rect(x, y, base_w, base_h)

        # tamaño visual (no afecta la hitbox)
        self.display_w = int(base_w * DISPLAY_SCALE)
        self.display_h = int(base_h * DISPLAY_SCALE)

        # imagen visual por defecto y rect de dibujo (alineado por los pies)
        self.display_image = pygame.Surface((self.display_w, self.display_h), pygame.SRCALPHA)
        self.display_image.fill((0, 0, 255))
        self.display_rect = self.display_image.get_rect(midbottom=self.rect.midbottom)

        # animaciones
        self.animations = {'idle': [], 'run': [], 'jump': []}
        self.current_anim = 'idle'
        self.anim_index = 0
        self.last_anim_time = 0
        self.frame_duration = 100
        self.facing_right = True

        # intentar cargar sprites desde imagenes/BICICLETERO
        try:
            assets_dir = os.path.join(os.path.dirname(__file__), 'imagenes', 'BICICLETERO')
            idle_path = os.path.join(assets_dir, 'idle.png')
            run_paths = [os.path.join(assets_dir, f'run{i}.png') for i in (1, 2, 3)]
            jump_path = os.path.join(assets_dir, 'jump.png')

            have_separate = os.path.exists(idle_path) and all(os.path.exists(p) for p in run_paths) and os.path.exists(jump_path)
            if have_separate:
                self.animations['idle'] = [pygame.image.load(idle_path).convert_alpha()]
                self.animations['run'] = [pygame.image.load(p).convert_alpha() for p in run_paths]
                self.animations['jump'] = [pygame.image.load(jump_path).convert_alpha()]
            else:
                # intentar sprite sheet player_sprites.png
                sheet_path = os.path.join(assets_dir, 'player_sprites.png')
                if os.path.exists(sheet_path):
                    sheet = pygame.image.load(sheet_path).convert_alpha()
                    sw, sh = sheet.get_size()
                    cols = max(1, sw // base_w)
                    rows = max(1, sh // base_h)
                    frames = []
                    for ry in range(rows):
                        for cx in range(cols):
                            rect = pygame.Rect(cx * base_w, ry * base_h, base_w, base_h)
                            frames.append(sheet.subsurface(rect).copy())
                    if frames:
                        self.animations['run'] = frames[0:cols]
                        self.animations['idle'] = [frames[0]]
                        if rows >= 2:
                            self.animations['jump'] = [frames[cols]]
                        else:
                            self.animations['jump'] = [frames[0]]

            # escalar frames a tamaño visual
            for k, lst in self.animations.items():
                self.animations[k] = [pygame.transform.scale(f, (self.display_w, self.display_h)) for f in lst]
            if self.animations['idle']:
                self.display_image = self.animations['idle'][0]
                self.display_rect = self.display_image.get_rect(midbottom=self.rect.midbottom)
        except Exception as e:
            print('Warning: no se pudieron cargar sprites del jugador:', e)

        # movimiento
        self.base_speed = 5
        self.speed = self.base_speed
        self.speed_end_time = 0
        self.vel_y = 0
        self.on_ground = False

    def update(self, platforms, level_width):
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.speed

        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
            self.vel_y = JUMP_FORCE
            self.on_ground = False

        self.vel_y += GRAVITY
        dy += self.vel_y

        # horizontal
        self.rect.x += dx
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if dx > 0:
                    self.rect.right = platform.rect.left
                elif dx < 0:
                    self.rect.left = platform.rect.right

        # vertical
        self.rect.y += dy
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0

        # límites
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > level_width:
            self.rect.right = level_width

        # temporizadores
        now = pygame.time.get_ticks()
        if self.speed != self.base_speed and now >= self.speed_end_time:
            self.speed = self.base_speed

        # animación y alineación visual
        self._update_animation(dx)
        self.display_rect = self.display_image.get_rect(midbottom=self.rect.midbottom)

    def speed_up(self, duration_seconds: float, factor: float = 1.8):
        now = pygame.time.get_ticks()
        end_time = now + int(duration_seconds * 1000)
        if end_time > self.speed_end_time:
            self.speed = self.base_speed * factor
            self.speed_end_time = end_time

    def slow_down(self, duration_seconds: float, factor: float = 0.5):
        now = pygame.time.get_ticks()
        end_time = now + int(duration_seconds * 1000)
        if end_time > self.speed_end_time:
            self.speed = self.base_speed * factor
            self.speed_end_time = end_time

    def _update_animation(self, dx):
        now = pygame.time.get_ticks()
        if not self.on_ground:
            anim = 'jump'
        elif dx != 0:
            anim = 'run'
        else:
            anim = 'idle'

        if anim != self.current_anim:
            self.current_anim = anim
            self.anim_index = 0
            self.last_anim_time = now

        frames = self.animations.get(self.current_anim, [])
        if not frames:
            return

        if now - self.last_anim_time >= self.frame_duration:
            self.anim_index = (self.anim_index + 1) % len(frames)
            self.last_anim_time = now

        frame = frames[self.anim_index]

        if dx < 0:
            self.facing_right = False
        elif dx > 0:
            self.facing_right = True

        img = frame
        if not self.facing_right:
            img = pygame.transform.flip(frame, True, False)

        # actualizar solo la imagen visual (no la hitbox)
        self.display_image = img
        self.display_rect = self.display_image.get_rect(midbottom=self.rect.midbottom)


