import pygame
import sys
import os
import subprocess
import time
from typing import Optional

class GameMenu:
    def __init__(self):
        pygame.init()
        
        # Obtener resolución nativa de la pantalla
        info = pygame.display.Info()
        self.screen_width = info.current_w
        self.screen_height = info.current_h
        
        # Crear pantalla en modo completo
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        pygame.display.set_caption('Bicicletero Man')
        self.clock = pygame.time.Clock()
        
        # Estados del juego
        self.state = "splash"  # splash -> menu -> options / nivel
        self.splash_timer = 0
        self.splash_duration = 3000  # 3 segundos
        self.fade_alpha = 0
        self.fade_speed = 3
        
        # Volumen de música (0.0 - 1.0)
        self.music_volume = 0.7
        self.music_muted = False
        
        # Selección del menú
        self.selected_option = 0
        self.menu_options = ["PLAY", "CONTINUE", "OPTIONS", "EXIT"]
        
        # Imágenes de los botones del menú
        self.menu_button_images = {}
        
        # Cargar imágenes
        self.load_images()

        # Música del menú
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(os.path.join('assets', 'Inicio.mp3'))
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"Error cargando música del menú: {e}")
        
    def load_images(self):
        """Cargar todas las imágenes necesarias"""
        try:
            # Pantalla de inicio
            splash_img = pygame.image.load("assets/PANTALLA-PRINCIPAL.png").convert()
            self.splash_image = pygame.transform.scale(splash_img, (self.screen_width, self.screen_height))
            
            # Fondo del menú
            menu_bg_img = pygame.image.load("assets/fondo-menu.png").convert()
            self.menu_background = pygame.transform.scale(menu_bg_img, (self.screen_width, self.screen_height))
            
            # Fondo del menú de opciones
            options_bg_img = pygame.image.load("assets/opciones.png").convert()
            self.options_background = pygame.transform.scale(options_bg_img, (self.screen_width, self.screen_height))
            
            # Botones del menú
            button_files = {
                "PLAY": "play-menu.png",
                "CONTINUE": "continue-menu.png",
                "OPTIONS": "options-menu.png",
                "EXIT": "exit-menu.png"
            }
            
            # Calcular tamaño de botones basado en resolución
            button_scale = min(self.screen_width/1920, self.screen_height/1080)
            button_width = int(300 * button_scale)
            button_height = int(80 * button_scale)
            
            for option, filename in button_files.items():
                try:
                    button_img = pygame.image.load(f"assets/{filename}").convert_alpha()
                    scaled_button = pygame.transform.scale(button_img, (button_width, button_height))
                    self.menu_button_images[option] = scaled_button
                except pygame.error as e:
                    print(f"Error cargando botón {filename}: {e}")
                    # Crear botón de respaldo
                    fallback_button = pygame.Surface((button_width, button_height))
                    fallback_button.fill((100, 100, 100))
                    self.menu_button_images[option] = fallback_button
            
        except pygame.error as e:
            print(f"Error cargando imágenes: {e}")
            # Crear imágenes de respaldo si no se pueden cargar
            self.splash_image = pygame.Surface((self.screen_width, self.screen_height))
            self.splash_image.fill((0, 100, 200))  # Azul
            
            self.menu_background = pygame.Surface((self.screen_width, self.screen_height))
            self.menu_background.fill((20, 20, 50))  # Azul oscuro
            
            self.options_background = pygame.Surface((self.screen_width, self.screen_height))
            self.options_background.fill((20, 40, 20))  # Verde oscuro
            
            # Crear botones de respaldo
            button_scale = min(self.screen_width/1920, self.screen_height/1080)
            button_width = int(300 * button_scale)
            button_height = int(80 * button_scale)
            
            for option in self.menu_options:
                fallback_button = pygame.Surface((button_width, button_height))
                fallback_button.fill((100, 100, 100))
                self.menu_button_images[option] = fallback_button
            
        # Superficie para el fundido
        self.fade_surface = pygame.Surface((self.screen_width, self.screen_height))
        self.fade_surface.fill((0, 0, 0))
        
    def handle_events(self):
        """Manejar eventos del teclado"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                # ESC: volver atrás o salir según el estado
                if event.key == pygame.K_ESCAPE:
                    if self.state == "options":
                        self.state = "menu"
                        self.selected_option = 0
                    else:
                        return False
                
                # En el estado de menú
                if self.state == "menu":
                    if event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.select_option()
                
                # En el menú de opciones
                elif self.state == "options":
                    options_list = self.get_options_list()
                    if event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % len(options_list)
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % len(options_list)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_LEFT, pygame.K_RIGHT):
                        self.execute_option_action(event.key)
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "menu"
                        self.selected_option = 0
                        return True  # No salir del juego
                        
                # En pantalla de inicio, saltar al menú con cualquier tecla
                elif self.state == "splash":
                    self.state = "menu"
                    self.fade_alpha = 0
                    
        return True
    
    def select_option(self):
        """Ejecutar la opción seleccionada del menú"""
        option = self.menu_options[self.selected_option]
        
        if option == "PLAY":
            # Iniciar progresión desde el nivel 1
            self.launch_level_progression()
        elif option == "CONTINUE":
            # Lanzar el segundo nivel
            self.launch_level("nivel-2")
        elif option == "OPTIONS":
            # Ir al menú de opciones
            self.state = "options"
            self.selected_option = 0
        elif option == "EXIT":
            pygame.quit()
            sys.exit()
    
    def launch_level_progression(self):
        """Lanzar niveles en secuencia automática empezando desde nivel 1"""
        levels = ["nivel-1", "nivel-2", "nivel-3"]
        
        for i, level in enumerate(levels):
            print(f"=== Iniciando {level} (nivel {i+1}/3) ===")
            
            if not self.launch_level_with_result(level):
                print(f"Nivel {level} no completado. Regresando al menú.")
                self._start_menu_music()
                break
            else:
                print(f"¡Nivel {level} completado! Continuando...")
                if i < len(levels) - 1:  # No es el último nivel
                    pass  # Pasar directamente al siguiente nivel sin pausa
        else:
            # Si llegamos aquí, se completaron todos los niveles
            print("¡Felicitaciones! Has completado todos los niveles.")
            self._start_menu_music()
    
    def launch_level_with_result(self, level_folder: str) -> bool:
        """Lanzar un nivel y devolver True si se completó exitosamente"""
        try:
            print(f"=== Iniciando {level_folder} ===")
            
            # Nombre del archivo principal del nivel (sin la carpeta, porque cwd ya será la carpeta)
            level_files = {
                "nivel-1": "main.py",
                "nivel-2": "LVL2_1.py",
                "nivel-3": "main.py"
            }
            level_file = level_files.get(level_folder)
            if not level_file:
                print(f"Nivel no reconocido: {level_folder}")
                return False
            
            # Ruta completa para verificar existencia
            full_path = os.path.join(level_folder, level_file)
            if not os.path.exists(full_path):
                print(f"ERROR: No se encontró: {os.path.abspath(full_path)}")
                return False
            
            # Cerrar pygame del menú completamente
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            pygame.quit()
            
            # Ejecutar el nivel: cwd es la carpeta del nivel, ejecutar solo el archivo
            result = subprocess.run(
                [sys.executable, level_file],
                cwd=level_folder
            )
            
            print(f"Nivel {level_folder} terminó con código: {result.returncode}")
            
            # Reinicializar pygame del menú
            self._reinit_pygame()
            
            # Código 0 = nivel completado exitosamente
            return result.returncode == 0
                
        except Exception as e:
            print(f"ERROR ejecutando {level_folder}: {e}")
            self._reinit_pygame()
            return False
    
    def launch_level(self, level_folder: str):
        """Lanzar un nivel específico sin tracking de resultado"""
        self.launch_level_with_result(level_folder)
    
    def _reinit_pygame(self):
        """Reinicializar pygame después de volver de un nivel"""
        try:
            pygame.init()
            pygame.mixer.init()
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
            pygame.display.set_caption('Bicicletero Man')
            self.load_images()
            print("Menú reinicializado correctamente")
        except Exception as e:
            print(f"Error crítico al reinicializar menú: {e}")
            sys.exit(1)

    def _start_menu_music(self):
        """Iniciar la música del menú"""
        try:
            pygame.mixer.music.load(os.path.join('assets', 'Inicio.mp3'))
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"Error recargando música del menú: {e}")
    
    def update(self, dt):
        """Actualizar la lógica del juego"""
        if self.state == "splash":
            self.splash_timer += dt
            if self.splash_timer >= self.splash_duration:
                self.state = "menu"
                self.fade_alpha = 0
        
        elif self.state == "menu":
            # Efecto de fundido gradual
            if self.fade_alpha < 255:
                self.fade_alpha = min(255, self.fade_alpha + self.fade_speed)
    
    def draw(self):
        """Dibujar la pantalla actual"""
        if self.state == "splash":
            self.draw_splash()
        elif self.state == "menu":
            self.draw_menu()
        elif self.state == "options":
            self.draw_options_menu()
            
        pygame.display.flip()
    
    def get_options_list(self):
        """Devuelve la lista de opciones con sus valores actuales"""
        vol_pct = int(self.music_volume * 100)
        musica = f"Música: {'Silenciada' if self.music_muted else f'{vol_pct}%'}"
        fullscreen = "Pantalla: Completa" if self.screen.get_flags() & pygame.FULLSCREEN else "Pantalla: Ventana"
        return [musica, fullscreen, "Volver"]

    def execute_option_action(self, key):
        """Ejecutar la acción de la opción seleccionada en el menú de opciones"""
        options = self.get_options_list()
        sel = self.selected_option

        if options[sel].startswith("Música"):
            if key in (pygame.K_LEFT,):
                self.music_volume = max(0.0, round(self.music_volume - 0.1, 1))
                self.music_muted = self.music_volume == 0.0
            elif key in (pygame.K_RIGHT,):
                self.music_volume = min(1.0, round(self.music_volume + 0.1, 1))
                self.music_muted = False
            elif key in (pygame.K_RETURN, pygame.K_SPACE):
                self.music_muted = not self.music_muted
            # Aplicar volumen
            vol = 0.0 if self.music_muted else self.music_volume
            try:
                pygame.mixer.music.set_volume(vol)
            except Exception:
                pass

        elif options[sel].startswith("Pantalla"):
            if key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_LEFT, pygame.K_RIGHT):
                if self.screen.get_flags() & pygame.FULLSCREEN:
                    self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
                else:
                    self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)

        elif options[sel] == "Volver":
            self.state = "menu"
            self.selected_option = 0

    def draw_options_menu(self):
        """Dibujar el menú de opciones"""
        self.screen.blit(self.options_background, (0, 0))

        scale = min(self.screen_width / 1920, self.screen_height / 1080)
        fuente_titulo = pygame.font.SysFont(None, int(90 * scale))
        fuente_opcion = pygame.font.SysFont(None, int(55 * scale))
        fuente_ayuda  = pygame.font.SysFont(None, int(30 * scale))

        options = self.get_options_list()
        start_y = int(self.screen_height * 0.42)
        spacing = int(90 * scale)

        for i, texto in enumerate(options):
            if i == self.selected_option:
                color = (255, 220, 50)
            else:
                color = (255, 255, 255)
            surf = fuente_opcion.render(texto, True, color)
            rect = surf.get_rect(center=(self.screen_width // 2, start_y + i * spacing))
            self.screen.blit(surf, rect)

            if i == self.selected_option:
                border = rect.inflate(24, 12)
                pygame.draw.rect(self.screen, (255, 220, 50), border, 3, border_radius=6)

        ayuda = fuente_ayuda.render("←→ ajustar  |  Enter activar/desactivar  |  Esc volver", True, (200, 200, 200))
        self.screen.blit(ayuda, ayuda.get_rect(center=(self.screen_width // 2, self.screen_height - int(60 * scale))))

    def draw_splash(self):
        self.screen.blit(self.splash_image, (0, 0))
        
        # Texto opcional en la pantalla de inicio
        font = pygame.font.SysFont(None, int(48 * min(self.screen_width/1920, self.screen_height/1080)))
        text = font.render("Presiona cualquier tecla para continuar", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.screen_width//2, self.screen_height - 100))
        
        # Efecto parpadeante
        if (pygame.time.get_ticks() // 500) % 2:
            self.screen.blit(text, text_rect)
    
    def draw_menu(self):
        """Dibujar el menú principal"""
        # Fondo del menú
        self.screen.blit(self.menu_background, (0, 0))
        
        # Aplicar fundido si es necesario
        if self.fade_alpha < 255:
            fade_surface_alpha = pygame.Surface((self.screen_width, self.screen_height))
            fade_surface_alpha.fill((0, 0, 0))
            fade_surface_alpha.set_alpha(255 - self.fade_alpha)
            self.screen.blit(fade_surface_alpha, (0, 0))
        
        # Título del juego - ELIMINADO
        # title_font = pygame.font.SysFont(None, int(96 * min(self.screen_width/1920, self.screen_height/1080)))
        # title_text = title_font.render("BICICLETERO MAN", True, (255, 255, 255))
        # title_rect = title_text.get_rect(center=(self.screen_width//2, self.screen_height//4))
        
        # Sombra del título - ELIMINADO
        # shadow_text = title_font.render("BICICLETERO MAN", True, (0, 0, 0))
        # shadow_rect = shadow_text.get_rect(center=(self.screen_width//2 + 3, self.screen_height//4 + 3))
        # self.screen.blit(shadow_text, shadow_rect)
        # self.screen.blit(title_text, title_rect)
        
        # Opciones del menú (usando imágenes)
        start_y = self.screen_height // 2 - 100  # Ajustado para centrar mejor
        option_spacing = int(120 * min(self.screen_width/1920, self.screen_height/1080))
        
        for i, option in enumerate(self.menu_options):
            # Obtener imagen del botón
            button_img = self.menu_button_images.get(option)
            
            if button_img:
                # Escalar ligeramente si está seleccionado
                if i == self.selected_option:
                    scaled_width = int(button_img.get_width() * 1.08)
                    scaled_height = int(button_img.get_height() * 1.08)
                    display_img = pygame.transform.scale(button_img, (scaled_width, scaled_height))
                else:
                    display_img = button_img
                
                # Posicionar botón centrado
                button_rect = display_img.get_rect(center=(self.screen_width//2, start_y + i * option_spacing))
                
                # Dibujar botón
                self.screen.blit(display_img, button_rect)
                
                # Si está seleccionado, dibujar contorno resaltado
                if i == self.selected_option:
                    border_thickness = 4
                    border_rect = button_rect.inflate(border_thickness * 2, border_thickness * 2)
                    pygame.draw.rect(self.screen, (32, 108, 120), border_rect, border_thickness, border_radius=8)
        
        # Instrucciones
        instruction_font = pygame.font.SysFont(None, int(32 * min(self.screen_width/1920, self.screen_height/1080)))
        instructions = [
            "↑↓ - Navegar",
            "ENTER/ESPACIO - Seleccionar",
            "ESC - Salir"
        ]
        
        instruction_y = self.screen_height - 150
        for instruction in instructions:
            inst_text = instruction_font.render(instruction, True, (200, 200, 200))
            inst_rect = inst_text.get_rect(center=(self.screen_width//2, instruction_y))
            self.screen.blit(inst_text, inst_rect)
            instruction_y += 35
    
    def run(self):
        """Bucle principal del juego"""
        running = True
        while running:
            dt = self.clock.tick(60)  # 60 FPS
            
            running = self.handle_events()
            self.update(dt)
            self.draw()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    menu = GameMenu()
    menu.run()