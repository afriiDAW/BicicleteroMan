import pygame
import os

# ---------------- CONSTANTES ----------------
GRAVITY = 0.8
JUMP_FORCE = -14
DISPLAY_SCALE = 1.35  # Escala visual del sprite (no afecta hitbox)

# ---------------- FUNCIONES DE UTILIDAD ----------------
def load_sprite_animations(assets_dir, base_w, base_h, display_w, display_h):
    """Carga las animaciones del jugador desde archivos individuales o sprite sheet."""
    animations = {'idle': [], 'run': [], 'jump': []}
    
    try:
        # Intentar archivos individuales primero
        sprite_files = {
            'idle': 'idle.png',
            'run': ['run1.png', 'run2.png', 'run3.png'],
            'jump': 'jump.png'
        }
        
        idle_path = os.path.join(assets_dir, sprite_files['idle'])
        run_paths = [os.path.join(assets_dir, f) for f in sprite_files['run']]
        jump_path = os.path.join(assets_dir, sprite_files['jump'])
        
        if os.path.exists(idle_path) and all(os.path.exists(p) for p in run_paths) and os.path.exists(jump_path):
            animations['idle'] = [pygame.image.load(idle_path).convert_alpha()]
            animations['run'] = [pygame.image.load(p).convert_alpha() for p in run_paths]
            animations['jump'] = [pygame.image.load(jump_path).convert_alpha()]
        else:
            # Usar sprite sheet como alternativa
            _load_from_sprite_sheet(assets_dir, base_w, base_h, animations)
            
        # Escalar todos los frames al tamaño visual
        for anim_name, frames in animations.items():
            animations[anim_name] = [pygame.transform.scale(f, (display_w, display_h)) for f in frames]
            
    except Exception as e:
        print('Warning: no se pudieron cargar sprites del jugador:', e)
        # Crear frame por defecto
        default_frame = pygame.Surface((display_w, display_h), pygame.SRCALPHA)
        default_frame.fill((0, 0, 255))
        animations = {'idle': [default_frame], 'run': [default_frame], 'jump': [default_frame]}
        
    return animations

def _load_from_sprite_sheet(assets_dir, base_w, base_h, animations):
    """Carga animaciones desde un sprite sheet."""
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
            animations['run'] = frames[0:cols]
            animations['idle'] = [frames[0]]
            animations['jump'] = [frames[cols]] if rows >= 2 else [frames[0]]


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, jump_sound=None):
        super().__init__()
        
        # Configuración básica
        base_w, base_h = 40, 60
        self.rect = pygame.Rect(x, y, base_w, base_h)
        self.jump_sound = jump_sound
        
        # Tamaño visual
        self.display_w = int(base_w * DISPLAY_SCALE)
        self.display_h = int(base_h * DISPLAY_SCALE)
        
        # Cargar animaciones
        assets_dir = os.path.join(os.path.dirname(__file__), 'imagenes', 'BICICLETERO')
        self.animations = load_sprite_animations(assets_dir, base_w, base_h, self.display_w, self.display_h)
        
        # Estado de animación
        self.current_anim = 'idle'
        self.anim_index = 0
        self.last_anim_time = 0
        self.frame_duration = 100
        self.facing_right = True
        
        # Imagen inicial
        self.display_image = self.animations['idle'][0] if self.animations['idle'] else pygame.Surface((self.display_w, self.display_h), pygame.SRCALPHA)
        self.display_rect = self.display_image.get_rect(midbottom=self.rect.midbottom)
        
        # Física y movimiento
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
            # reproducir sonido de salto
            if self.jump_sound:
                self.jump_sound.play()

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

    def _modify_speed(self, duration_seconds: float, factor: float):
        """Método unificado para modificar la velocidad temporalmente."""
        now = pygame.time.get_ticks()
        end_time = now + int(duration_seconds * 1000)
        if end_time > self.speed_end_time:
            self.speed = self.base_speed * factor
            self.speed_end_time = end_time

    def speed_up(self, duration_seconds: float, factor: float = 1.8):
        """Acelera al jugador temporalmente."""
        self._modify_speed(duration_seconds, factor)

    def slow_down(self, duration_seconds: float, factor: float = 0.5):
        """Ralentiza al jugador temporalmente."""
        self._modify_speed(duration_seconds, factor)

    def _update_animation(self, dx):
        """Actualiza la animación y dirección del jugador."""
        now = pygame.time.get_ticks()
        
        # Determinar animación apropiada
        anim = 'jump' if not self.on_ground else ('run' if dx != 0 else 'idle')
        
        # Cambiar animación si es necesario
        if anim != self.current_anim:
            self.current_anim = anim
            self.anim_index = 0
            self.last_anim_time = now

        frames = self.animations.get(self.current_anim, [])
        if not frames:
            return

        # Avanzar frame si es tiempo
        if now - self.last_anim_time >= self.frame_duration:
            self.anim_index = (self.anim_index + 1) % len(frames)
            self.last_anim_time = now

        # Actualizar dirección
        if dx != 0:
            self.facing_right = dx > 0

        # Aplicar imagen (con flip si es necesario)
        frame = frames[self.anim_index]
        self.display_image = pygame.transform.flip(frame, True, False) if not self.facing_right else frame
        self.display_rect = self.display_image.get_rect(midbottom=self.rect.midbottom)


