import pygame
import sys
import os
import random

from constants import (
    WIDTH,
    HEIGHT,
    FPS,
    DOG_SPAWN_MS,
    LEVEL_TIME_MS,
    INVULNERABILITY_MS,
    START_LIVES,
    DOG_VISIBLE_MS,
    SCREEN_INVULNERABILITY_MS,
    DOG_ATTACK_DELAY_MS,
    VISION_ANGLE,
    VISION_DISTANCE,
    SHOW_VISION_CONE,
    NIGHT_COLOR,
    NIGHT_OPACITY,
    DOG_FRAME_DURATION_MS # Importamos la nueva constante
)
from entities import Player, Obstacle, Dog
from utils import draw_road, draw_ui, load_backgrounds


class Game:
    def __init__(self):
        pygame.init()
        
        # Obtener resolución nativa de la pantalla
        info = pygame.display.Info()
        self.screen_width = info.current_w
        self.screen_height = info.current_h
        
        # Crear pantalla en modo completo
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        
        # Crear superficie del juego con las dimensiones originales
        self.game_surface = pygame.Surface((WIDTH, HEIGHT))
        
        # Calcular factor de escala para mantener aspecto ratio
        scale_x = self.screen_width / WIDTH
        scale_y = self.screen_height / HEIGHT
        self.scale = min(scale_x, scale_y)  # Usar el menor para no distorsionar
        
        # Calcular dimensiones escaladas
        self.scaled_width = int(WIDTH * self.scale)
        self.scaled_height = int(HEIGHT * self.scale)
        
        # Calcular posición para centrar
        self.offset_x = (self.screen_width - self.scaled_width) // 2
        self.offset_y = (self.screen_height - self.scaled_height) // 2
        
        pygame.display.set_caption('Bici Obstáculos')
        self.clock = pygame.time.Clock()

        base = os.path.dirname(__file__)
        # Cargar fondos con las dimensiones originales del juego
        self.backgrounds = load_backgrounds(base, ('backgrounds/camino1.png', 'backgrounds/camino2.png', 'backgrounds/camino3.png'), (WIDTH, HEIGHT))
        self.bg_index = 0

        # --- SISTEMA DE AUDIO ---
        # 1. Música de fondo
        try:
            music_path = os.path.join(base, 'music', 'musicaNivel3.mp3')
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.5) 
            pygame.mixer.music.play(-1) # Bucle infinito
        except pygame.error as e:
            print(f"Error música: {e}")

        # 2. Sonido del perro y variables de control
        try:
            sound_path = os.path.join(base, 'music', 'perroNivel3.mp3')
            self.sonido_perro = pygame.mixer.Sound(sound_path)
        except Exception as e:
            print(f"Error sonido perro: {e}")
            self.sonido_perro = None
            
        self.ladrido_timer = 0       # Cronómetro para el ciclo de 3s
        self.ladrido_pendiente = False # Control de ráfaga
        # ------------------------

        self.player = Player()
        self.dog = None
        self.dog_timer = 0
        self.dog_visible_until = 0
        self.player_history = []  
        self.obstacles = self.generate_obstacles(avoid_rects=[self.player.rect])

        self.level_time_left = LEVEL_TIME_MS
        self.level_complete = False
        self.lives = START_LIVES
        self.invulnerable = False
        self.invulnerable_start = 0
        self.invulnerable_duration = 0
        self.game_over = False
        self.score = 0
        self.lives_earned_from_score = 0

        # Imagen de game over
        self.gameover_img = None
        try:
            go_path = os.path.join(os.path.dirname(__file__), 'imagenes', 'gameover3.png')
            if os.path.exists(go_path):
                self.gameover_img = pygame.image.load(go_path).convert()
        except Exception as e:
            print(f"Error cargando gameover3.png: {e}")
        self.boton_reiniciar_rect = None

        # Imagen de nivel completado
        self.victoria_img = None
        try:
            vic_path = os.path.join(os.path.dirname(__file__), 'imagenes', 'nivel3completado.png')
            if os.path.exists(vic_path):
                self.victoria_img = pygame.image.load(vic_path).convert()
        except Exception as e:
            print(f"Error cargando nivel3completado.png: {e}")
        self.victoria_parpadeo_inicio = 0
        
        self.night_filter = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.night_filter.fill((*NIGHT_COLOR, NIGHT_OPACITY))
        
        # Estado de pausa
        self.pausa_activa = False
        self.indice_pausa = 0
        self.vol_musica = 0.5
        self.vol_efectos = 0.8
        self.musica_silenciada = False
        self.efectos_silenciados = False
        self.NUM_OPCIONES_PAUSA = 6
        self._aplicar_vol_musica()
        self._aplicar_vol_efectos()
        
    def generate_obstacles(self, avoid_rects=None, min_count=3, max_count=7):
        obs = []
        count = random.randint(min_count, max_count)
        attempts = 0
        min_gap = getattr(self.player.rect, 'height', 60) + 20
        while len(obs) < count and attempts < count * 30:
            attempts += 1
            o = Obstacle()
            o_y = random.randint(60, HEIGHT - o.height - 60)
            o.rect.y = o_y
            o.y = o_y + o.radius  
            collides = False

            for existing in obs:
                if o.rect.colliderect(existing.rect):
                    collides = True
                    break
                vert_gap = abs(o.rect.centery - existing.rect.centery) - (o.height + existing.height) / 2
                if vert_gap < min_gap:
                    collides = True
                    break

            if not collides and avoid_rects:
                for r in avoid_rects:
                    if o.rect.colliderect(r):
                        collides = True
                        break
                    vert_gap = abs(o.rect.centery - r.centery) - (o.height + r.height) / 2
                    if vert_gap < min_gap:
                        collides = True
                        break

            if not collides:
                obs.append(o)

        return obs

    def reset_game(self):
        self.player = Player()
        self.dog = None
        self.dog_timer = 0
        self.obstacles = self.generate_obstacles(avoid_rects=[self.player.rect])
        self.lives = START_LIVES
        self.invulnerable = False
        self.invulnerable_duration = 0
        self.game_over = False
        self.level_time_left = LEVEL_TIME_MS
        self.level_complete = False
        self.score = 0
        self.victoria_parpadeo_inicio = 0
        self.lives_earned_from_score = 0
        # Reiniciar música al resetear
        pygame.mixer.music.play(-1)
        # Reiniciar pausa
        self.pausa_activa = False
        self.indice_pausa = 0

    def _aplicar_vol_musica(self):
        v = 0.0 if self.musica_silenciada else self.vol_musica
        try:
            pygame.mixer.music.set_volume(v)
        except Exception:
            pass

    def _aplicar_vol_efectos(self):
        vol = 0.0 if self.efectos_silenciados else self.vol_efectos
        if self.sonido_perro:
            self.sonido_perro.set_volume(vol)

    def _get_opciones_pausa(self):
        m_str = "Silenciada" if self.musica_silenciada else f"{int(self.vol_musica * 100)}%"
        e_str = "Silenciados" if self.efectos_silenciados else f"{int(self.vol_efectos * 100)}%"
        flags = self.screen.get_flags()
        pantalla = "Completa" if flags & pygame.FULLSCREEN else "Ventana"
        return [
            "Continuar",
            f"Vol. Música: {m_str}",
            f"Vol. Efectos: {e_str}",
            f"Pantalla: {pantalla}",
            "Reiniciar nivel",
            "Salir",
        ]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                # Toggle pausa con ESC o P
                if event.key in (pygame.K_ESCAPE, pygame.K_p):
                    if not self.game_over and not self.level_complete:
                        self.pausa_activa = not self.pausa_activa
                        if self.pausa_activa:
                            pygame.mixer.music.pause()
                        else:
                            pygame.mixer.music.unpause()
                    elif self.game_over or self.level_complete:
                        return False  # Salir si el juego terminó
                # Navegación en menú de pausa
                elif self.pausa_activa:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.indice_pausa = (self.indice_pausa - 1) % self.NUM_OPCIONES_PAUSA
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.indice_pausa = (self.indice_pausa + 1) % self.NUM_OPCIONES_PAUSA
                    elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        delta = 0.1 if event.key == pygame.K_RIGHT else -0.1
                        if self.indice_pausa == 1:  # Vol. Música
                            self.vol_musica = max(0.0, min(1.0, round(self.vol_musica + delta, 1)))
                            self.musica_silenciada = self.vol_musica == 0.0
                            self._aplicar_vol_musica()
                        elif self.indice_pausa == 2:  # Vol. Efectos
                            self.vol_efectos = max(0.0, min(1.0, round(self.vol_efectos + delta, 1)))
                            self.efectos_silenciados = self.vol_efectos == 0.0
                            self._aplicar_vol_efectos()
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if self.indice_pausa == 0:  # Continuar
                            self.pausa_activa = False
                            pygame.mixer.music.unpause()
                        elif self.indice_pausa == 1:  # Vol. Música: silenciar/activar
                            self.musica_silenciada = not self.musica_silenciada
                            self._aplicar_vol_musica()
                            if not self.musica_silenciada:
                                pygame.mixer.music.unpause()
                        elif self.indice_pausa == 2:  # Vol. Efectos: silenciar/activar
                            self.efectos_silenciados = not self.efectos_silenciados
                            self._aplicar_vol_efectos()
                        elif self.indice_pausa == 3:  # Pantalla
                            flags = self.screen.get_flags()
                            if flags & pygame.FULLSCREEN:
                                self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
                            else:
                                self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
                        elif self.indice_pausa == 4:  # Reiniciar nivel
                            self.reset_game()
                        elif self.indice_pausa == 5:  # Salir
                            print("Nivel 3 abandonado desde pausa")
                            return False
                else:
                    # Reiniciar juego con R cuando está en game over o level complete
                    if (self.game_over or self.level_complete) and event.key == pygame.K_r:
                        self.reset_game()
                    if self.level_complete and event.key == pygame.K_RETURN:
                        # Fundido de salida (imagen → negro) antes de la pantalla final
                        fade_surface = pygame.Surface((self.screen_width, self.screen_height))
                        fade_surface.fill((0, 0, 0))
                        clock_out = pygame.time.Clock()
                        for alpha in range(0, 256, 5):
                            clock_out.tick(FPS)
                            fade_surface.set_alpha(alpha)
                            self.screen.blit(fade_surface, (0, 0))
                            pygame.display.flip()
                        self.show_final_screen()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.game_over and self.boton_reiniciar_rect and self.boton_reiniciar_rect.collidepoint(event.pos):
                    self.reset_game()
        return True

    def update(self, dt):
        if self.pausa_activa:
            return
        now = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        
        if not self.game_over and not self.level_complete:
            self.player.handle_input(keys)
            self.level_time_left -= dt
            if self.level_time_left <= 0:
                self.level_time_left = 0
                self.level_complete = True

            # Aparición del perro
            if self.dog is None:
                self.dog_timer += dt
                if self.dog_timer >= DOG_SPAWN_MS:
                    self.dog = Dog(self.player)
                    self.dog_spawn_time = now
                    self.dog_visible_until = now + DOG_VISIBLE_MS
                    self.dog_timer = 0
                    
                    # Activar secuencia de ladridos
                    self.ladrido_pendiente = True
                    self.ladrido_timer = 3000 # Para que suene la primera ráfaga al instante

            # Lógica de ráfaga de ladridos (3 veces cada 3 segundos)
            if self.ladrido_pendiente and self.dog and not self.game_over:
                self.ladrido_timer += dt
                if self.ladrido_timer >= 3000:
                    if self.sonido_perro:
                        # Suenan 3 veces seguidas
                        for _ in range(3):
                            self.sonido_perro.play()
                    self.ladrido_timer = 0 
            else:
                self.ladrido_pendiente = False

            # Cambio de pantalla / nivel
            if self.player.rect.top <= 0:
                if self.backgrounds:
                    self.bg_index = (self.bg_index + 1) % len(self.backgrounds)
                self.player.rect.bottom = HEIGHT - 10
                self.invulnerable = True
                self.invulnerable_start = now
                self.invulnerable_duration = SCREEN_INVULNERABILITY_MS
                self.score += 10
                if self.dog:
                    self.dog = Dog(self.player)
                    self.dog_spawn_time = now
                    self.obstacles = self.generate_obstacles(avoid_rects=[self.player.rect, self.dog.rect])
                else:
                    self.obstacles = self.generate_obstacles(avoid_rects=[self.player.rect])

            # Movimiento del perro
            if self.dog:
                if now >= self.dog_spawn_time + DOG_ATTACK_DELAY_MS:
                    delayed_target = self._get_player_rect_with_delay(500, now)
                    # --- NUEVO: Pasamos dt para la animación ---
                    self.dog.update(delayed_target, dt)
                    
                if now >= self.dog_visible_until:
                    self.dog = None
                    self.dog_timer = 0

            # Obstáculos e historial
            self.obstacles = [o for o in self.obstacles if o.rect.top <= HEIGHT and o.rect.bottom >= 0]
            self.player_history.append((now, self.player.rect.copy()))
            cutoff = now - 2000
            self.player_history = [(t, r) for (t, r) in self.player_history if t >= cutoff]

            # Colisiones
            def take_damage():
                if self.invulnerable:
                    return False
                self.lives -= 1
                self.score -= 30
                self.invulnerable = True
                self.invulnerable_start = now
                self.invulnerable_duration = INVULNERABILITY_MS
                if self.lives <= 0:
                    self.game_over = True
                    pygame.mixer.music.stop()
                    try:
                        go_sound_path = os.path.join(os.path.dirname(__file__), 'music', 'gameover.mp3')
                        go_sound = pygame.mixer.Sound(go_sound_path)
                        go_sound.set_volume(self.vol_efectos)
                        go_sound.play()
                    except Exception as e:
                        print(f"Error reproduciendo gameover.mp3: {e}")
                return True

            for ob in self.obstacles:
                if self.player.rect.colliderect(ob.rect):
                    if take_damage():
                        break

            if self.dog and self.player.rect.colliderect(self.dog.rect):
                take_damage()

            if self.invulnerable and now - self.invulnerable_start >= self.invulnerable_duration:
                self.invulnerable = False

            # Vidas extras
            lives_to_grant = self.score // 50
            if lives_to_grant > self.lives_earned_from_score:
                self.lives += lives_to_grant - self.lives_earned_from_score
                self.lives_earned_from_score = lives_to_grant

    def _get_player_rect_with_delay(self, delay_ms: int, now: int):
        target_time = now - delay_ms
        for t, rect in reversed(self.player_history):
            if t <= target_time:
                return rect.copy()
        return self.player.rect.copy()

    def _is_in_vision(self, rect: pygame.Rect) -> bool:
        p = pygame.math.Vector2(self.player.rect.center)
        o = pygame.math.Vector2(rect.center)
        vec = o - p
        dist = vec.length()
        if dist == 0: return True
        if dist > VISION_DISTANCE: return False
        angle = self.player.facing.angle_to(vec)
        return abs(angle) <= VISION_ANGLE / 2

    def _draw_vision_cone(self):
        p = pygame.math.Vector2(self.player.rect.center)
        half = VISION_ANGLE / 2
        left = self.player.facing.rotate(half)
        right = self.player.facing.rotate(-half)
        dist = VISION_DISTANCE
        left_pt = p + left * dist
        right_pt = p + right * dist
        cone_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(cone_surf, (255, 255, 255, 40), [p, left_pt, right_pt])
        self.game_surface.blit(cone_surf, (0, 0))

    def draw_pause_menu(self):
        """Dibujar menú de pausa sobre la escena del juego"""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.game_surface.blit(overlay, (0, 0))

        fuente_titulo = pygame.font.SysFont(None, 80)
        fuente_menu = pygame.font.SysFont(None, 50)
        fuente_ayuda = pygame.font.SysFont(None, 28)

        titulo = fuente_titulo.render("PAUSA", True, (255, 255, 255))
        self.game_surface.blit(titulo, titulo.get_rect(center=(WIDTH // 2, int(HEIGHT * 0.15))))

        opciones = self._get_opciones_pausa()
        start_y = int(HEIGHT * 0.35)
        spacing = int(HEIGHT * 0.1)
        for i, texto in enumerate(opciones):
            color = (255, 230, 120) if i == self.indice_pausa else (255, 255, 255)
            linea = fuente_menu.render(texto, True, color)
            self.game_surface.blit(linea, linea.get_rect(center=(WIDTH // 2, start_y + i * spacing)))

        ayuda = fuente_ayuda.render("↑↓ navegar  |  ←→ ajustar volumen  |  Enter confirmar  |  Esc/P continuar", True, (200, 200, 200))
        self.game_surface.blit(ayuda, ayuda.get_rect(center=(WIDTH // 2, HEIGHT - 30)))

    def draw(self):
        if self.backgrounds:
            self.game_surface.blit(self.backgrounds[self.bg_index], (0, 0))
        else:
            draw_road(self.game_surface)

        self.game_surface.blit(self.night_filter, (0, 0))

        if VISION_ANGLE and SHOW_VISION_CONE:
            self._draw_vision_cone()

        for ob in self.obstacles:
            if self._is_in_vision(ob.rect):
                ob.draw(self.game_surface)
                
        if self.dog:
            self.dog.draw(self.game_surface)
            
        self.player.draw(self.game_surface, invulnerable=self.invulnerable)

        font = pygame.font.SysFont(None, 28)
        time_txt = font.render(f'Tiempo: {self.level_time_left//1000}s', True, (255, 255, 255))
        self.game_surface.blit(time_txt, (WIDTH - time_txt.get_width() - 10, 10))
        draw_ui(self.game_surface, self.lives, self.score)

        if self.game_over:
            pass  # Se dibuja sobre self.screen tras el escalado

        if self.level_complete:
            pass  # Se dibuja sobre self.screen tras el escalado

        # Limpiar la pantalla completa con negro
        self.screen.fill((0, 0, 0))
        
        # Dibujar menú de pausa si está activo
        if self.pausa_activa:
            self.draw_pause_menu()
        
        # Escalar y centrar la superficie del juego en la pantalla completa
        scaled_surface = pygame.transform.scale(self.game_surface, (self.scaled_width, self.scaled_height))
        self.screen.blit(scaled_surface, (self.offset_x, self.offset_y))

        # Dibujar game over directamente en pantalla (coordenadas reales)
        if self.game_over:
            if self.gameover_img:
                go_scaled = pygame.transform.scale(self.gameover_img, (self.screen_width, self.screen_height))
                self.screen.blit(go_scaled, (0, 0))
            else:
                overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.screen.blit(overlay, (0, 0))
                font = pygame.font.SysFont(None, 72)
                txt = font.render('GAME OVER', True, (255, 0, 0))
                self.screen.blit(txt, (self.screen_width // 2 - txt.get_width() // 2, self.screen_height // 2 - 40))

            btn_w, btn_h = 220, 50
            btn_x = (self.screen_width - btn_w) // 2
            btn_y = (self.screen_height // 2) + 180
            self.boton_reiniciar_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
            pygame.draw.rect(self.screen, (70, 130, 180), self.boton_reiniciar_rect)
            fuente_btn = pygame.font.Font(None, 30)
            texto_btn = fuente_btn.render('Reiniciar (R)', True, (255, 255, 255))
            self.screen.blit(texto_btn, texto_btn.get_rect(center=self.boton_reiniciar_rect.center))

        # Dibujar nivel completado directamente en pantalla
        if self.level_complete:
            if self.victoria_parpadeo_inicio == 0:
                self.victoria_parpadeo_inicio = pygame.time.get_ticks()
            if self.victoria_img:
                vic_scaled = pygame.transform.scale(self.victoria_img, (self.screen_width, self.screen_height))
                self.screen.blit(vic_scaled, (0, 0))
            else:
                overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.screen.blit(overlay, (0, 0))
                font = pygame.font.SysFont(None, 72)
                txt = font.render('¡NIVEL COMPLETADO!', True, (0, 255, 0))
                self.screen.blit(txt, (self.screen_width // 2 - txt.get_width() // 2, self.screen_height // 2 - 40))
            # Texto parpadeante
            if (pygame.time.get_ticks() - self.victoria_parpadeo_inicio) % 1000 < 500:
                fuente_p = pygame.font.Font(None, 42)
                texto_p = fuente_p.render('Pulsa ENTER para terminar', True, (255, 255, 255))
                sombra_p = fuente_p.render('Pulsa ENTER para terminar', True, (0, 0, 0))
                rect_p = texto_p.get_rect(bottomright=(self.screen_width - 30, int(self.screen_height * 0.95)))
                self.screen.blit(sombra_p, (rect_p.x + 2, rect_p.y + 2))
                self.screen.blit(texto_p, rect_p)

        pygame.display.flip()

    def show_final_screen(self):
        base = os.path.dirname(__file__)
        final_img = None
        try:
            img_path = os.path.join(base, 'imagenes', 'final-bicicleteroman.png')
            if os.path.exists(img_path):
                final_img = pygame.image.load(img_path).convert()
        except Exception as e:
            print(f"Error cargando final-bicicleteroman.png: {e}")

        # Reproducir música final
        try:
            pygame.mixer.music.stop()
            music_path = os.path.join(base, 'music', 'Final.mp3')
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(self.vol_musica)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"Error reproduciendo Final.mp3: {e}")

        # Fundido de entrada (negro → imagen final)
        fade_surface = pygame.Surface((self.screen_width, self.screen_height))
        fade_surface.fill((0, 0, 0))
        clock_fade = pygame.time.Clock()
        for alpha in range(255, -1, -5):
            clock_fade.tick(FPS)
            if final_img:
                img_scaled = pygame.transform.scale(final_img, (self.screen_width, self.screen_height))
                self.screen.blit(img_scaled, (0, 0))
            else:
                self.screen.fill((0, 0, 0))
            fade_surface.set_alpha(alpha)
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.flip()

        fuente_p = pygame.font.Font(None, 42)
        tiempo_inicio = pygame.time.get_ticks()
        clock = pygame.time.Clock()

        while True:
            clock.tick(FPS)
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN:
                    print("¡Nivel 3 completado exitosamente!")
                    pygame.quit()
                    sys.exit(0)

            if final_img:
                img_scaled = pygame.transform.scale(final_img, (self.screen_width, self.screen_height))
                self.screen.blit(img_scaled, (0, 0))
            else:
                self.screen.fill((0, 0, 0))

            # Texto parpadeante
            if (pygame.time.get_ticks() - tiempo_inicio) % 1000 < 500:
                texto_p = fuente_p.render('Pulsa ENTER para volver al menú', True, (255, 255, 255))
                sombra_p = fuente_p.render('Pulsa ENTER para volver al menú', True, (0, 0, 0))
                rect_p = texto_p.get_rect(bottomright=(self.screen_width - 30, int(self.screen_height * 0.95)))
                self.screen.blit(sombra_p, (rect_p.x + 2, rect_p.y + 2))
                self.screen.blit(texto_p, rect_p)

            pygame.display.flip()

    def show_dialog(self):
        base = os.path.dirname(__file__)
        dialogo_img = None
        try:
            img_path = os.path.join(base, 'imagenes', 'dialogo3.png')
            if os.path.exists(img_path):
                dialogo_img = pygame.image.load(img_path).convert()
        except Exception as e:
            print(f"Error cargando dialogo3.png: {e}")

        fuente_parpadeo = pygame.font.Font(None, 42)
        tiempo_inicio = pygame.time.get_ticks()
        clock = pygame.time.Clock()

        while True:
            clock.tick(FPS)
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(1)
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_RETURN:
                        return
                    elif evento.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit(1)

            if dialogo_img:
                img_scaled = pygame.transform.scale(dialogo_img, (self.screen_width, self.screen_height))
                self.screen.blit(img_scaled, (0, 0))
            else:
                self.screen.fill((0, 0, 0))

            # Texto parpadeante cada 500ms
            if (pygame.time.get_ticks() - tiempo_inicio) % 1000 < 500:
                texto = fuente_parpadeo.render("Pulsa ENTER para comenzar", True, (255, 255, 255))
                sombra = fuente_parpadeo.render("Pulsa ENTER para comenzar", True, (0, 0, 0))
                rect_t = texto.get_rect(bottomright=(self.screen_width - 30, int(self.screen_height * 0.95)))
                self.screen.blit(sombra, (rect_t.x + 2, rect_t.y + 2))
                self.screen.blit(texto, rect_t)

            pygame.display.flip()

    def run(self):
        self.show_dialog()
        # Reiniciar el timer para que el tiempo empiece justo al cerrar el diálogo
        self.level_time_left = LEVEL_TIME_MS
        # Consumir el dt acumulado durante el diálogo para que no descuente del nivel
        self.clock.tick()
        running = True
        while running:
            dt = self.clock.tick(FPS)
            running = self.handle_events()
            self.update(dt)
            self.draw()

            # El game over y nivel completado no cierran automáticamente
                
        # Si sale del loop por ESC u otra razón
        pygame.quit()
        sys.exit(1)  # Código 1 indica abandono