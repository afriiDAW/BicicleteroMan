import pygame
import random
import os

# ---------------- CONSTANTES ----------------
GRAVITY = 0.8
JUMP_FORCE = -12

# Configuración de rutas y velocidades
ROUTE_CONFIGS = {
    'ground': {'speed_multiplier': 1.0, 'jump_probability': 0.02},
    'platforms': {'speed_multiplier': 1.03, 'jump_probability': 0.0},  # Solo saltos tácticos
    'zigzag': {'speed_multiplier': 1.08, 'jump_probability': 0.45}
}

# ---------------- FUNCIONES DE UTILIDAD ----------------
def load_thief_sprite(assets_dir, base_w, base_h):
    """Carga el sprite del ladrón con fallback automático."""
    try:
        ladron_path = os.path.join(assets_dir, 'ladron.png')
        if os.path.exists(ladron_path):
            img = pygame.image.load(ladron_path).convert_alpha()
            return pygame.transform.scale(img, (base_w, base_h))
    except Exception:
        pass
    
    # Fallback: rect negro
    fallback = pygame.Surface((base_w, base_h), pygame.SRCALPHA)
    fallback.fill((0, 0, 0))
    return fallback


class Thief(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Configuración básica
        base_w, base_h = 40, 60
        self.rect = pygame.Rect(x, y, base_w, base_h)
        
        # Cargar sprite
        assets_dir = os.path.join(os.path.dirname(__file__), 'imagenes')
        sprite = load_thief_sprite(assets_dir, base_w, base_h)
        
        self.image = pygame.Surface((base_w, base_h), pygame.SRCALPHA)
        self.image.blit(sprite, (0, 0))
        
        # Física y movimiento
        self.base_speed = 2.4
        self.speed = self.base_speed
        self.vel_y = 0
        self.on_ground = False
        
        # IA / Sistema de rutas
        self.route = None
        self.next_route_change = 0
        self.last_jump_time = 0
        self.choose_route()

    def choose_route(self):
        """Selecciona una ruta aleatoria con duración variable."""
        self.route = random.choice(list(ROUTE_CONFIGS.keys()))
        self.next_route_change = pygame.time.get_ticks() + random.randint(2500, 7000)
    
    def _calculate_speed(self, player):
        """Calcula la velocidad basada en la ruta actual y el jugador."""
        config = ROUTE_CONFIGS[self.route]
        base_multiplier = max(0.1, player.base_speed * 1.08)
        speed = base_multiplier * config['speed_multiplier']
        return speed * 0.9  # Ajuste de dificultad final
    
    def _should_jump(self, platforms):
        """Determina si el ladrón debe saltar según la ruta actual."""
        if not self.on_ground:
            return False
            
        config = ROUTE_CONFIGS[self.route]
        now = pygame.time.get_ticks()
        
        if self.route == 'platforms':
            # Saltos tácticos para subir plataformas
            return self._find_jump_target(platforms) is not None
        elif self.route == 'zigzag':
            # Saltos frecuentes con cooldown
            return (now - self.last_jump_time > 700 and 
                   random.random() < config['jump_probability'])
        else:  # ground
            # Saltos ocasionales aleatorios
            return random.random() < config['jump_probability']
    
    def _find_jump_target(self, platforms):
        """Busca una plataforma objetivo para saltar."""
        for platform in platforms:
            # Plataforma por delante entre 20 y 220 px
            if (platform.rect.left > self.rect.right and 
                platform.rect.left - self.rect.right < 220):
                # Preferir plataformas más altas
                if platform.rect.top < self.rect.top - 10:
                    return platform
        return None

    def update(self, platforms: list, level_width: int, player) -> bool:
        """Actualiza la posición del ladrón.
        
        Devuelve True si el ladrón llega al final del nivel (escapa).
        """
        now = pygame.time.get_ticks()
        
        # Cambiar ruta si es momento
        if now >= self.next_route_change:
            self.choose_route()
        
        # Actualizar velocidad y movimiento horizontal
        self.speed = self._calculate_speed(player)
        self.rect.x += self.speed
        
        # Determinar si saltar
        if self._should_jump(platforms):
            self.vel_y = JUMP_FORCE
            self.on_ground = False
            if self.route == 'platforms':
                target = self._find_jump_target(platforms)
                if target and target.rect.left - self.rect.right < 60:
                    self.last_jump_time = now
            elif self.route == 'zigzag':
                self.last_jump_time = now
        
        # Aplicar gravedad y movimiento vertical
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        
        # Resolver colisiones verticales
        self._handle_platform_collisions(platforms)
        
        # Verificar límites del nivel
        return self._check_level_bounds(level_width)
    
    def _handle_platform_collisions(self, platforms):
        """Maneja las colisiones con plataformas."""
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:  # Cayendo
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:  # Subiendo
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0
    
    def _check_level_bounds(self, level_width):
        """Verifica límites del nivel y maneja caídas."""
        # Verificar escape
        if self.rect.right >= level_width:
            return True
        
        # Evitar caídas fuera del mundo
        if self.rect.top > 1000:
            self.rect.y = 300
            self.vel_y = 0
            
        return False


if __name__ == "__main__":
    pass