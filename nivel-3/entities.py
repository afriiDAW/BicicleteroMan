import pygame
import random
import os
from constants import (
    WIDTH,
    HEIGHT,
    ROAD_WIDTH,
    ROAD_X,
    DOG_FRAME_DURATION_MS, # Nueva constante
)

class Player:
    def __init__(self):
        # 1. TAMAÑOS
        # Dimensiones visuales (más grandes)
        self.visual_width = 120
        self.visual_height = 150
        # Dimensiones de la caja de colisión (más pequeña)
        self.width = 40
        self.height = 60
        
        # Posición inicial
        self.x = WIDTH // 2 - self.visual_width // 2
        self.y = HEIGHT - self.visual_height - 30

        # 2. Carga y Escalado del Sprite
        base_dir = os.path.dirname(__file__)
        ruta_sprite = os.path.join(base_dir, 'backgrounds', 'player.png')
        try:
            img_original = pygame.image.load(ruta_sprite).convert_alpha()
            self.image = pygame.transform.scale(img_original, (self.visual_width, self.visual_height))
            
            # 3. AJUSTE DE LA CAJA DE COLISIÓN (Hitbox)
            # Primero obtenemos el rect del tamaño de la imagen
            full_rect = self.image.get_rect()
            full_rect.topleft = (self.x, self.y)
            
            # 'inflate' reduce el rect. Valores negativos lo hacen más pequeño.
            # Aquí reducimos 15 píxeles de cada lado horizontal y 10 vertical.
            # Mantenemos los valores de reducción originales:
            self.rect = full_rect.inflate(-90, -80)
            
        except Exception as e:
            print(f"Error cargando el sprite: {e}")
            self.image = None
            self.rect = pygame.Rect(self.x, self.y, 40, 60)

        self.speed = 5
        self.facing = pygame.math.Vector2(0, -1)

    def handle_input(self, keys):
        dx = 0
        dy = 0
        if keys[pygame.K_LEFT]:
            dx -= self.speed
        if keys[pygame.K_RIGHT]:
            dx += self.speed
        if keys[pygame.K_UP]:
            dy -= self.speed
        if keys[pygame.K_DOWN]:
            dy += self.speed

        # Movemos la hitbox
        self.rect.x += dx
        self.rect.y += dy

        # Restricciones de la carretera basadas en la hitbox
        if self.rect.left < ROAD_X + 10:
            self.rect.left = ROAD_X + 10
        if self.rect.right > ROAD_X + ROAD_WIDTH - 10:
            self.rect.right = ROAD_X + ROAD_WIDTH - 10
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT - 10:
            self.rect.bottom = HEIGHT - 10

    def draw(self, surface, invulnerable=False):
        if invulnerable and (pygame.time.get_ticks() // 100) % 2 == 0:
            return

        if self.image:
            # IMPORTANTE: Dibujamos la imagen centrada en la hitbox.
            # Como la hitbox es más pequeña, calculamos el offset para que la imagen 
            # "envuelva" a la colisión de forma centrada.
            img_rect = self.image.get_rect(center=self.rect.center)
            surface.blit(self.image, img_rect)
            
            # DESCOMENTA LA LÍNEA DE ABAJO PARA VER LA CAJA DE COLISIÓN MIENTRAS PRUEBAS:
            # pygame.draw.rect(surface, (255, 0, 0), self.rect, 1)
        else:
            pygame.draw.rect(surface, (30, 144, 255), self.rect, border_radius=6)

class Obstacle:
    def __init__(self):
        # 1. Seleccionar tipo de sprite
        self.tipo = random.choice(['obstaculo1.png', 'obstaculo2.png'])
        
        # 2. DETERMINAR TAMAÑO ALEATORIO
        escala = random.uniform(0.7, 1.5)
        self.width = int(50 * escala)
        self.height = int(50 * escala)
        
        # 3. Cargar y escalar la imagen
        base_dir = os.path.dirname(__file__)
        ruta = os.path.join(base_dir, 'obstacles', self.tipo)
        try:
            self.image = pygame.image.load(ruta).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except:
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((255, 0, 0))

        # 4. Posición aleatoria
        self.x = random.randint(ROAD_X, ROAD_X + ROAD_WIDTH - self.width)
        self.y = random.randint(-HEIGHT, -50)
        
        # 5. Rectángulo de colisión
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.radius = self.width // 2

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# --- REESCRITURA COMPLETA DE LA CLASE DOG PARA ANIMACIÓN ---
class Dog:
    def __init__(self, player):
        # 1. TAMAÑOS (Ajustados para que sea más largo)
        # Dimensiones visuales: Aumentamos mucho el alto (visual_height)
        self.visual_width = 60
        self.visual_height = 110  # Antes era 60, ahora es casi el doble
        
        # Dimensiones de la caja de colisión: También la alargamos
        self.width = 40
        self.height = 85   # Ajustada para que coincida con el cuerpo largo
        
        # 2. CARGA Y RECORTE DEL SPRITE (ANIMACIÓN)
        base_dir = os.path.dirname(__file__)
        ruta_sprite = os.path.join(base_dir, 'backgrounds', 'perro.png')
        self.frames = []
        try:
            sprite_sheet = pygame.image.load(ruta_sprite).convert_alpha()
            orig_width = sprite_sheet.get_width()
            orig_height = sprite_sheet.get_height()
            
            num_frames = 4
            frame_width = orig_width // num_frames
            frame_height = orig_height
            
            for i in range(num_frames):
                frame_surf = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame_surf.blit(sprite_sheet, (0, 0), (i * frame_width, 0, frame_width, frame_height))
                
                # USAMOS LAS NUEVAS DIMENSIONES LARGAS AQUÍ
                scaled_frame = pygame.transform.scale(frame_surf, (self.visual_width, self.visual_height))
                self.frames.append(scaled_frame)
            
        except Exception as e:
            print(f"Error cargando el sprite del perro: {e}")
            self.frames = [pygame.Surface((self.visual_width, self.visual_height), pygame.SRCALPHA)]
            self.frames[0].fill((200, 0, 0, 150))

        # 3. CONTROL DE ANIMACIÓN
        self.current_frame = 0
        self.animation_timer = 0

        # 4. POSICIÓN Y MOVIMIENTO
        side = random.choice(('left', 'right'))
        if side == 'left':
            self.x = ROAD_X + 10
        else:
            self.x = ROAD_X + ROAD_WIDTH - self.width - 10
        
        self.original_y = HEIGHT - self.height - 30
        
        # Definimos el hitbox alargado
        self.rect = pygame.Rect(self.x, self.original_y, self.width, self.height)
        self.speed = player.speed

    def update(self, target_rect, dt):
        # 1. ACTUALIZACIÓN DE ANIMACIÓN
        self.animation_timer += dt
        if self.animation_timer >= DOG_FRAME_DURATION_MS:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.animation_timer = 0

        # 2. ACTUALIZACIÓN DE MOVIMIENTO
        dx = target_rect.centerx - self.rect.centerx
        dy = target_rect.centery - self.rect.centery
        dist = (dx * dx + dy * dy) ** 0.5
        if dist <= 0:
            return
        step = min(self.speed, dist)
        self.rect.x += int(dx / dist * step)
        self.rect.y += int(dy / dist * step)
        
        # Límites de la carretera (ajustados al nuevo largo)
        if self.rect.left < ROAD_X + 10:
            self.rect.left = ROAD_X + 10
        if self.rect.right > ROAD_X + ROAD_WIDTH - 10:
            self.rect.right = ROAD_X + ROAD_WIDTH - 10
        if self.rect.top < 10:
            self.rect.top = 10
        if self.rect.bottom > HEIGHT - 10:
            self.rect.bottom = HEIGHT - 10

    def draw(self, surface):
        # Dibujamos el frame de animación centrado en el hitbox
        # Como el perro es largo, el centro del rect asegurará que se vea bien
        img_rect = self.frames[self.current_frame].get_rect(center=self.rect.center)
        surface.blit(self.frames[self.current_frame], img_rect)