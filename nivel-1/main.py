import pygame
import sys

from player import Player
from camera import Camera
from level1 import load_level, LEVEL_LENGTH
from plataformas import Platform, MovingPlatform
from obstacle import Obstacle
from powerup import PowerUp
from thief import Thief
import json
import os

pygame.init()

# ---------------- FUNCIONES DE UTILIDAD ----------------
def load_sound(filename, volume=1.0):
    """Carga un archivo de sonido con manejo de errores unificado."""
    try:
        sound_path = os.path.join(os.path.dirname(__file__), 'sonidos', filename)
        if os.path.exists(sound_path):
            sound = pygame.mixer.Sound(sound_path)
            sound.set_volume(volume)
            print(f"Sonido cargado: {sound_path}")
            return sound
        else:
            print(f"Archivo de sonido no encontrado: {sound_path}")
            return None
    except Exception as e:
        print(f"Error cargando sonido {filename}: {e}")
        return None

def load_game_level():
    """Carga el nivel apropiado (personalizado o por defecto)."""
    custom_path = os.path.join(os.path.dirname(__file__), "level_custom.json")
    if os.path.exists(custom_path):
        try:
            return load_level_from_file(custom_path)
        except Exception as e:
            print("Error cargando nivel personalizado, cargando por defecto:", e)
    return load_level()

def reset_game_state():
    """Reinicia el estado del juego (jugador, cámara, música)."""
    player = Player(50, 843, jump_sound)
    camera = Camera(WIDTH, LEVEL_LENGTH)
    try:
        thief.rect.topleft = (400, 843)
    except Exception:
        pass
    # Reiniciar música de fondo
    try:
        pygame.mixer.music.play(-1)
    except Exception:
        pass
    return player, camera

# ---------------- MÚSICA Y SONIDOS ----------------
# Cargar y reproducir música de fondo
try:
    sound_dir = os.path.join(os.path.dirname(__file__), 'sonidos')
    music_path = os.path.join(sound_dir, 'nivel1.mp3')
    if os.path.exists(music_path):
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.7)
        pygame.mixer.music.play(-1)
        print(f"Música cargada: {music_path}")
    else:
        print(f"Archivo de música no encontrado: {music_path}")
except Exception as e:
    print(f"Error cargando música: {e}")

# Cargar sonidos de efectos usando la función optimizada
jump_sound = load_sound('salto.mp3', 0.8)
obstacle_sound = load_sound('obstaculo.mp3', 0.9)
gameover_sound = load_sound('gameover.mp3', 0.8)
powerup_sound = load_sound('powerup.mp3', 0.8)

# ---------------- CONFIGURACIÓN ----------------
# Resolución de referencia para el juego (base design resolution)
REFERENCE_WIDTH = 1920
REFERENCE_HEIGHT = 1080
# Dimensiones por defecto en ventana (usadas al salir de fullscreen)
WINDOWED_SIZE = (900, 500)

# Inicializar pantalla física
# Usar DOUBLEBUF para buffer doble y, si está disponible, habilitar vsync (mejora fluidez en fullscreen)
try:
    PHYSICAL_SCREEN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF, vsync=1)
except TypeError:
    # pygame puede no soportar el argumento vsync en todas las builds; caer al modo sin vsync
    PHYSICAL_SCREEN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF)

PHYSICAL_WIDTH, PHYSICAL_HEIGHT = PHYSICAL_SCREEN.get_size()

# Crear superficie virtual para el juego
VIRTUAL_SCREEN = pygame.Surface((REFERENCE_WIDTH, REFERENCE_HEIGHT))

# Calcular factor de escala manteniendo aspect ratio
scale_x = PHYSICAL_WIDTH / REFERENCE_WIDTH
scale_y = PHYSICAL_HEIGHT / REFERENCE_HEIGHT
SCALE_FACTOR = min(scale_x, scale_y)

# Calcular dimensiones escaladas y posición para centrar
SCALED_WIDTH = int(REFERENCE_WIDTH * SCALE_FACTOR)
SCALED_HEIGHT = int(REFERENCE_HEIGHT * SCALE_FACTOR)
OFFSET_X = (PHYSICAL_WIDTH - SCALED_WIDTH) // 2
OFFSET_Y = (PHYSICAL_HEIGHT - SCALED_HEIGHT) // 2

# Para compatibilidad con código existente
SCREEN = VIRTUAL_SCREEN
WIDTH, HEIGHT = REFERENCE_WIDTH, REFERENCE_HEIGHT

pygame.display.set_caption(f"Nivel 1 - Plataformas con Cámara ({PHYSICAL_WIDTH}x{PHYSICAL_HEIGHT} -> {REFERENCE_WIDTH}x{REFERENCE_HEIGHT})")

CLOCK = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Fuente para HUD/debug
FONT = pygame.font.Font(None, 24)
BIG_FONT = pygame.font.Font(None, 48)
BUTTON_FONT = pygame.font.Font(None, 30)

# ---------------- BACKGROUND (tileable + loop) ----------------
# Ruta esperada: nivel1_prototipo/assets/background.png
BG_PARALLAX = 0.6
# velocidad de auto-scroll en píxeles/segundo (0 = desactivado)
BG_AUTO_SCROLL_SPEED = 0.0
# combinar desplazamiento de cámara con auto-scroll (False = fondo estático)
BG_USE_CAMERA_PARALLAX = True
bg_image = None
bg_w = bg_h = 0
bg_scroll_x = 0.0
try:
    assets_dir = os.path.join(os.path.dirname(__file__), 'imagenes')
    bg_path = os.path.join(assets_dir, 'fondo5.png')
    if os.path.exists(bg_path):
        bg_image = pygame.image.load(bg_path).convert_alpha()
        bg_w, bg_h = bg_image.get_size()
    else:
        # generador simple de tile (fallback 128x128)
        bg_w, bg_h = 128, 128
        tile = pygame.Surface((bg_w, bg_h), pygame.SRCALPHA)
        tile.fill((135, 206, 235))  # cielo
        pygame.draw.rect(tile, (85, 107, 47), (0, int(bg_h * 0.75), bg_w, int(bg_h * 0.25)))
        pygame.draw.circle(tile, (255, 223, 0), (int(bg_w * 0.8), int(bg_h * 0.2)), 12)
        bg_image = tile
except Exception as e:
    print('Error cargando background:', e)
    bg_image = None

def draw_tiled_background(surface, camera, scroll_offset=0.0):
    """Dibuja `bg_image` repetido para cubrir la pantalla. scroll_offset en píxeles."""
    if not bg_image:
        surface.fill(WHITE)
        return

    parallax_offset = int(camera.offset_x * BG_PARALLAX) if BG_USE_CAMERA_PARALLAX else 0
    parallax_offset += int(scroll_offset)
    start_x = - (parallax_offset % bg_w)

    x = start_x - bg_w
    while x < WIDTH:
        y = 0
        while y < HEIGHT:
            surface.blit(bg_image, (x, y))
            y += bg_h
        x += bg_w


def convert_mouse_pos(physical_pos):
    """Convierte coordenadas del ratón de la pantalla física a la virtual."""
    px, py = physical_pos
    
    # Ajustar por el offset de centrado
    vx = (px - OFFSET_X) / SCALE_FACTOR
    vy = (py - OFFSET_Y) / SCALE_FACTOR
    
    # Clampear a los límites de la pantalla virtual
    vx = max(0, min(REFERENCE_WIDTH - 1, vx))
    vy = max(0, min(REFERENCE_HEIGHT - 1, vy))
    
    return (int(vx), int(vy))


def update_display_scaling():
    """Actualiza los factores de escala después de un cambio de resolución."""
    global PHYSICAL_WIDTH, PHYSICAL_HEIGHT, SCALE_FACTOR, SCALED_WIDTH, SCALED_HEIGHT, OFFSET_X, OFFSET_Y
    
    PHYSICAL_WIDTH, PHYSICAL_HEIGHT = PHYSICAL_SCREEN.get_size()
    
    # Calcular factor de escala manteniendo aspect ratio
    scale_x = PHYSICAL_WIDTH / REFERENCE_WIDTH
    scale_y = PHYSICAL_HEIGHT / REFERENCE_HEIGHT
    SCALE_FACTOR = min(scale_x, scale_y)
    
    # Calcular dimensiones escaladas y posición para centrar
    SCALED_WIDTH = int(REFERENCE_WIDTH * SCALE_FACTOR)
    SCALED_HEIGHT = int(REFERENCE_HEIGHT * SCALE_FACTOR)
    OFFSET_X = (PHYSICAL_WIDTH - SCALED_WIDTH) // 2
    OFFSET_Y = (PHYSICAL_HEIGHT - SCALED_HEIGHT) // 2


def present_screen():
    """Renderiza la superficie virtual escalada en la pantalla física."""
    # Llenar la pantalla física con negro para las barras letterbox/pillarbox
    PHYSICAL_SCREEN.fill(BLACK)
    
    # Escalar y centrar la superficie virtual
    if SCALE_FACTOR != 1.0:
        scaled_surface = pygame.transform.smoothscale(VIRTUAL_SCREEN, (SCALED_WIDTH, SCALED_HEIGHT))
        PHYSICAL_SCREEN.blit(scaled_surface, (OFFSET_X, OFFSET_Y))
    else:
        PHYSICAL_SCREEN.blit(VIRTUAL_SCREEN, (OFFSET_X, OFFSET_Y))
    
    pygame.display.flip()


def toggle_fullscreen():
    """Alterna entre fullscreen y ventana definida en WINDOWED_SIZE.

    Actualiza las variables globales PHYSICAL_SCREEN y factores de escala, 
    y actualiza camera.screen_width para que la cámara use el nuevo ancho.
    """
    global PHYSICAL_SCREEN, bg_scroll_x
    is_full = bool(pygame.display.get_surface().get_flags() & pygame.FULLSCREEN)
    if is_full:
        # cambiar a ventana (usar DOUBLEBUF también en ventana)
        PHYSICAL_SCREEN = pygame.display.set_mode(WINDOWED_SIZE, pygame.DOUBLEBUF)
    else:
        try:
            PHYSICAL_SCREEN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF, vsync=1)
        except TypeError:
            PHYSICAL_SCREEN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF)

    # Actualizar factores de escala
    update_display_scaling()
    
    # Actualizar caption
    pygame.display.set_caption(f"Nivel 1 - Plataformas con Cámara ({PHYSICAL_WIDTH}x{PHYSICAL_HEIGHT} -> {REFERENCE_WIDTH}x{REFERENCE_HEIGHT})")
    
    # Actualizar cámara si existe (WIDTH siempre es REFERENCE_WIDTH)
    try:
        camera.screen_width = WIDTH
    except Exception:
        # camera puede no existir al arrancar
        pass



def show_level_designer(platforms, obstacles, powerups, thief, player, camera):
    """Modo diseñador: pausa el juego y permite añadir/quitar/mover objetos.

    Controles:
    - Click y arrastrar: mover objetos
    - A: añadir plataforma en cursor
    - O: añadir obstáculo en cursor
    - P: añadir powerup en cursor
    - Suprimir / Backspace: borrar objeto seleccionado
    - Shift+J: salir del diseñador
    """
    selected_objects = []  # lista de objetos seleccionados
    dragging = False
    drag_start_pos = None  # posición inicial del arrastre
    initial_positions = {}  # posiciones iniciales de los objetos al empezar arrastre
    info_lines = [
        "Shift+J: salir del diseñador",
        "Click: seleccionar | Ctrl+Click: selección múltiple | Arrastrar: mover",
        "A: añadir Platform | O: añadir Obstacle | P: añadir PowerUp | M: añadir MovingPlatform",
        "Suprimir/Backspace: eliminar seleccionados | S: guardar | L: recargar",
        "Si seleccionas MovingPlatform: X toggle axis, R/T range -/+ , F/G speed -/+",
        "Flechas izquierda/derecha o A/D: mover la cámara",
    ]

    while True:
        CLOCK.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # salir con Shift+J
                if event.key == pygame.K_j and (event.mod & pygame.KMOD_SHIFT):
                    return
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_a:
                    mx, my = convert_mouse_pos(pygame.mouse.get_pos())
                    wx = mx + camera.offset_x
                    # añadir plataforma por defecto
                    newp = Platform(wx - 50, my - 10, 100, 20)
                    platforms.append(newp)
                    selected_objects = [newp]
                    dragging = True
                    drag_start_pos = (wx, my)
                    initial_positions = {newp: (newp.rect.x, newp.rect.y)}
                if event.key == pygame.K_o:
                    mx, my = convert_mouse_pos(pygame.mouse.get_pos())
                    wx = mx + camera.offset_x
                    newo = Obstacle(wx - 20, my - 20)
                    obstacles.append(newo)
                    selected_objects = [newo]
                    dragging = True
                    drag_start_pos = (wx, my)
                    initial_positions = {newo: (newo.rect.x, newo.rect.y)}
                if event.key == pygame.K_p:
                    mx, my = convert_mouse_pos(pygame.mouse.get_pos())
                    wx = mx + camera.offset_x
                    newpow = PowerUp(wx - 15, my - 15)
                    powerups.append(newpow)
                    selected_objects = [newpow]
                    dragging = True
                    drag_start_pos = (wx, my)
                    initial_positions = {newpow: (newpow.rect.x, newpow.rect.y)}
                if event.key == pygame.K_m:
                    mx, my = convert_mouse_pos(pygame.mouse.get_pos())
                    wx = mx + camera.offset_x
                    # añadir plataforma móvil por defecto
                    newm = MovingPlatform(wx - 50, my - 10, 100, 20, axis='x', range_px=120, speed=1.0)
                    platforms.append(newm)
                    selected_objects = [newm]
                    dragging = True
                    drag_start_pos = (wx, my)
                    initial_positions = {newm: (newm.rect.x, newm.rect.y)}
                if event.key in (pygame.K_DELETE, pygame.K_BACKSPACE):
                    for obj in selected_objects[:]:
                        # eliminar del contenedor correspondiente
                        if isinstance(obj, Platform):
                            if obj in platforms:
                                platforms.remove(obj)
                        elif isinstance(obj, Obstacle):
                            if obj in obstacles:
                                obstacles.remove(obj)
                        elif isinstance(obj, PowerUp):
                            if obj in powerups:
                                powerups.remove(obj)
                    selected_objects.clear()
                    dragging = False
                if event.key == pygame.K_s:
                    # guardar nivel a JSON
                    save_path = os.path.join(os.path.dirname(__file__), "level_custom.json")
                    try:
                        save_level_to_file(save_path, platforms, obstacles, powerups, thief)
                        print(f"Nivel guardado en {save_path}")
                    except Exception as e:
                        print("Error guardando nivel:", e)
                if event.key == pygame.K_l:
                    # recargar desde archivo si existe
                    load_path = os.path.join(os.path.dirname(__file__), "level_custom.json")
                    if os.path.exists(load_path):
                        try:
                            lp, lo, lpu, lth = load_level_from_file(load_path)
                            # reemplazar contenido de las listas pasadas por referencia
                            platforms.clear(); platforms.extend(lp)
                            obstacles.clear(); obstacles.extend(lo)
                            powerups.clear(); powerups.extend(lpu)
                            # actualizar posición del ladrón
                            thief.rect.topleft = (lth.rect.x, lth.rect.y)
                            selected_objects.clear()
                            dragging = False
                            print("Nivel recargado desde archivo")
                        except Exception as e:
                            print("Error cargando nivel:", e)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = convert_mouse_pos(event.pos)
                    wx = mx + camera.offset_x
                    wy = my
                    
                    # detectar si Ctrl está presionado para selección múltiple
                    keys = pygame.key.get_pressed()
                    ctrl_held = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]
                    
                    # buscar objeto bajo el cursor
                    clicked_obj = None
                    for lst in (powerups, obstacles, platforms):
                        for obj in reversed(lst):
                            if obj.rect.collidepoint((wx, wy)):
                                clicked_obj = obj
                                break
                        if clicked_obj:
                            break
                    
                    if clicked_obj:
                        if ctrl_held:
                            # selección múltiple: agregar/quitar del conjunto
                            if clicked_obj in selected_objects:
                                selected_objects.remove(clicked_obj)
                            else:
                                selected_objects.append(clicked_obj)
                        else:
                            # selección simple: reemplazar selección
                            selected_objects = [clicked_obj]
                        
                        if selected_objects:
                            dragging = True
                            drag_start_pos = (wx, wy)
                            # guardar posiciones iniciales de todos los objetos seleccionados
                            initial_positions = {obj: (obj.rect.x, obj.rect.y) for obj in selected_objects}
                    elif not ctrl_held:
                        # click en vacío sin Ctrl: deseleccionar todo
                        selected_objects.clear()
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
            if event.type == pygame.MOUSEMOTION:
                if dragging and selected_objects and drag_start_pos:
                    mx, my = convert_mouse_pos(event.pos)
                    wx = mx + camera.offset_x
                    wy = my
                    # calcular desplazamiento desde la posición inicial
                    dx = wx - drag_start_pos[0]
                    dy = wy - drag_start_pos[1]
                    # aplicar desplazamiento a todos los objetos seleccionados
                    for obj in selected_objects:
                        if obj in initial_positions:
                            orig_x, orig_y = initial_positions[obj]
                            obj.rect.x = orig_x + dx
                            obj.rect.y = orig_y + dy

        # manejo de teclas específicas para objeto seleccionado (fuera del loop de eventos)
        keys = pygame.key.get_pressed()
        # propiedades específicas solo si hay un solo MovingPlatform seleccionado
        if len(selected_objects) == 1 and isinstance(selected_objects[0], MovingPlatform):
            selected_platform = selected_objects[0]
            # toggle axis
            if keys[pygame.K_x]:
                selected_platform.axis = 'y' if selected_platform.axis == 'x' else 'x'
                # pequeña espera para evitar toggle continuo
                pygame.time.wait(150)
            # range +/-
            if keys[pygame.K_r]:
                selected_platform.range = max(8, selected_platform.range - 10)
                pygame.time.wait(120)
            if keys[pygame.K_t]:
                selected_platform.range = selected_platform.range + 10
                pygame.time.wait(120)
            # speed +/-
            if keys[pygame.K_f]:
                selected_platform.speed = max(0.1, selected_platform.speed - 0.2)
                pygame.time.wait(120)
            if keys[pygame.K_g]:
                selected_platform.speed = selected_platform.speed + 0.2
                pygame.time.wait(120)

        # Movimiento de cámara dentro del diseñador (WASD o flechas)
        cam_keys = pygame.key.get_pressed()
        cam_speed = 12
        if cam_keys[pygame.K_LEFT] or cam_keys[pygame.K_a]:
            camera.offset_x = max(0, camera.offset_x - cam_speed)
        if cam_keys[pygame.K_RIGHT] or cam_keys[pygame.K_d]:
            camera.offset_x = min(LEVEL_LENGTH - WIDTH, camera.offset_x + cam_speed)

        # Si hay un objeto seleccionado y es MovingPlatform, mostrar sus propiedades
        prop_lines = []
        if len(selected_objects) == 1 and isinstance(selected_objects[0], MovingPlatform):
            selected_platform = selected_objects[0]
            prop_lines.append(f"MovingPlatform axis={selected_platform.axis} range={int(selected_platform.range)} speed={round(selected_platform.speed,2)}")
            prop_lines.append("X: toggle axis | R/T: range -/+ 10 | F/G: speed -/+ 0.2")


        # Dibujar nivel actual con overlay
        draw_tiled_background(SCREEN, camera, bg_scroll_x)
        # dibujar plataformas, obstáculos y powerups
        for plat in platforms:
            SCREEN.blit(plat.image, camera.apply(plat.rect))
        for obs in obstacles:
            SCREEN.blit(obs.image, camera.apply(obs.rect))
        for pu in powerups:
            SCREEN.blit(pu.image, camera.apply(pu.rect))

        # resaltar seleccionados
        for obj in selected_objects:
            sel_rect = camera.apply(obj.rect)
            pygame.draw.rect(SCREEN, (255, 0, 0), sel_rect, 3)

        # instrucciones
        y = 8
        for line in info_lines:
            txt = FONT.render(line, True, BLACK)
            SCREEN.blit(txt, (8, y))
            y += 20
        # propiedades si aplican
        for pl in prop_lines:
            txt = FONT.render(pl, True, (200, 200, 255))
            SCREEN.blit(txt, (8, y))
            y += 20

        present_screen()


def save_level_to_file(path, platforms, obstacles, powerups, thief):
    data = {}
    data['level_length'] = LEVEL_LENGTH
    data['platforms'] = []
    for p in platforms:
        if isinstance(p, MovingPlatform):
            data['platforms'].append({
                'type': 'moving',
                'x': p.start_x,
                'y': p.start_y,
                'w': p.rect.width,
                'h': p.rect.height,
                'axis': p.axis,
                'range': p.range,
                'speed': p.speed,
                'texture': getattr(p, 'texture_path', None),
                'tile': getattr(p, 'tile', False),
            })
        else:
            data['platforms'].append({
                'type': 'static',
                'x': p.rect.x,
                'y': p.rect.y,
                'w': p.rect.width,
                'h': p.rect.height,
                'texture': getattr(p, 'texture_path', None),
                'tile': getattr(p, 'tile', False),
            })

    data['obstacles'] = [{'x': o.rect.x, 'y': o.rect.y} for o in obstacles]
    # persistir textura de obstáculos si existe
    data['obstacles'] = []
    for o in obstacles:
        data['obstacles'].append({
            'x': o.rect.x,
            'y': o.rect.y,
            'texture': getattr(o, 'texture_path', None),
            'w': getattr(o, 'size', (o.rect.width, o.rect.height))[0],
            'h': getattr(o, 'size', (o.rect.width, o.rect.height))[1],
        })
    # persistir powerups con posibles texturas y tamaño
    data['powerups'] = []
    for p in powerups:
        data['powerups'].append({
            'x': p.rect.x,
            'y': p.rect.y,
            'texture': getattr(p, 'texture_path', None),
            'w': getattr(p, 'size', (p.rect.width, p.rect.height))[0],
            'h': getattr(p, 'size', (p.rect.width, p.rect.height))[1],
        })
    data['thief'] = {'x': thief.rect.x, 'y': 843}

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def load_level_from_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    platforms = []
    for p in data.get('platforms', []):
        if p.get('type') == 'moving':
            mp = MovingPlatform(int(p['x']), int(p['y']), int(p['w']), int(p['h']), axis=p.get('axis','x'), range_px=int(p.get('range',120)), speed=float(p.get('speed',1.0)), texture_path=p.get('texture'), tile=bool(p.get('tile', False)))
            platforms.append(mp)
        else:
            platforms.append(Platform(int(p['x']), int(p['y']), int(p['w']), int(p['h']), texture_path=p.get('texture'), tile=bool(p.get('tile', False))))

    obstacles = []
    for o in data.get('obstacles', []):
        ox = int(o.get('x', 0))
        oy = int(o.get('y', 0))
        tex = o.get('texture')
        w = int(o.get('w', 40))
        h = int(o.get('h', 40))
        obstacles.append(Obstacle(ox, oy, texture_path=tex, size=(w, h)))
    powerups = []
    for p in data.get('powerups', []):
        px = int(p.get('x', 0))
        py = int(p.get('y', 0))
        tex = p.get('texture')
        w = int(p.get('w', 30))
        h = int(p.get('h', 30))
        powerups.append(PowerUp(px, py, texture_path=tex, size=(w, h)))
    thief_data = data.get('thief', {'x': 400, 'y': 843})
    thief = Thief(int(thief_data.get('x', 400)), int(thief_data.get('y', 843)))

    return platforms, obstacles, powerups, thief


# ---------------- CARGAR NIVEL ----------------
# Cargar el nivel apropiado usando la función optimizada
platforms, obstacles, powerups, thief = load_game_level()

# Forzar la posición por defecto del ladrón al iniciar la partida
try:
    thief.rect.topleft = (400, 843)
except Exception:
    pass

player = Player(50, 843, jump_sound)
camera = Camera(WIDTH, LEVEL_LENGTH)


def show_end_screen(message: str) -> bool:
    """Muestra una pantalla de fin con un botón de reinicio.

    Devuelve True si el jugador pulsa Reiniciar, False si cierra la ventana o
    pulsa Escape.
    """
    button_w, button_h = 220, 50
    button_rect = pygame.Rect((WIDTH - button_w) // 2, (HEIGHT // 2) + 120, button_w, button_h)
    
    # Cargar imagen de nivel completado si es pantalla de victoria
    victory_background = None
    is_victory = "ATRAPADO" in message.upper()
    
    if is_victory:
        try:
            assets_dir = os.path.join(os.path.dirname(__file__), 'imagenes')
            bg_path = os.path.join(assets_dir, 'nivel1completado.png')
            if os.path.exists(bg_path):
                victory_background = pygame.image.load(bg_path).convert()
                victory_background = pygame.transform.scale(victory_background, (WIDTH, HEIGHT))
                print(f"Imagen de victoria cargada: {bg_path}")
            else:
                print(f"Imagen de victoria no encontrada: {bg_path}")
        except Exception as e:
            print(f"Error cargando imagen de victoria: {e}")

    while True:
        CLOCK.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_r:
                    return True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_rect.collidepoint(convert_mouse_pos(event.pos)):
                    return True

        # Mostrar fondo personalizado o overlay por defecto
        if is_victory and victory_background:
            # Mostrar imagen de victoria como fondo completo
            SCREEN.blit(victory_background, (0, 0))
        else:
            # Fondo semitransparente por defecto
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((30, 30, 30))
            SCREEN.blit(overlay, (0, 0))

        # Mensaje centrado (solo para pantallas que no sean victoria)
        if not (is_victory and victory_background):
            text = BIG_FONT.render(message, True, (255, 255, 255))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
            SCREEN.blit(text, text_rect)

        # Botón
        pygame.draw.rect(SCREEN, (70, 130, 180), button_rect)
        btn_text = BUTTON_FONT.render("Reiniciar (R)", True, (255, 255, 255))
        btn_rect = btn_text.get_rect(center=button_rect.center)
        SCREEN.blit(btn_text, btn_rect)

        present_screen()

# ---------------- BUCLE PRINCIPAL ----------------
running = True
while running:
    dt_ms = CLOCK.tick(FPS)
    dt = dt_ms / 1000.0
    # actualizar desplazamiento automático del fondo
    if BG_AUTO_SCROLL_SPEED != 0.0:
        bg_scroll_x += BG_AUTO_SCROLL_SPEED * dt

    # dibujar fondo tileable (combina parallax de cámara y auto-scroll)
    draw_tiled_background(SCREEN, camera, bg_scroll_x)

    # -------- EVENTOS --------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # abrir diseñador con Shift+J
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_j and (event.mod & pygame.KMOD_SHIFT):
                # pausa el juego y abre la herramienta de diseño
                show_level_designer(platforms, obstacles, powerups, thief, player, camera)
            # toggle música con tecla M
            if event.key == pygame.K_m:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()
            # alternar fullscreen con F11
            if event.key == pygame.K_F11:
                toggle_fullscreen()
            # Escape: volver a modo ventana si está en fullscreen
            if event.key == pygame.K_ESCAPE:
                if SCREEN.get_flags() & pygame.FULLSCREEN:
                    toggle_fullscreen()

    # -------- UPDATE --------
    # Actualizar plataformas móviles antes del jugador para que las colisiones
    # se resuelvan correctamente con su nueva posición
    for plat in platforms:
        if hasattr(plat, 'update'):
            try:
                plat.update()
            except TypeError:
                # plataformas estáticas no esperan argumentos
                plat.update()
                
    # Actualizar powerups con efecto de flotación
    for powerup in powerups:
        powerup.update(dt)

    player.update(platforms, LEVEL_LENGTH)
    # Pasamos las plataformas y el jugador para que el ladrón ajuste su velocidad
    thief_escaped = thief.update(platforms, LEVEL_LENGTH, player)
    # pasar dt para que la cámara pueda suavizar el seguimiento de forma dependiente del tiempo
    camera.update(player, dt)

    # -------- COLISIONES --------
    # Comprobar colisiones con obstáculos: si el jugador colisiona, eliminar el obstáculo
    for obstacle in obstacles[:]:
        if player.rect.colliderect(obstacle.rect):
            # Reproducir sonido y aplicar efecto
            if obstacle_sound:
                obstacle_sound.play()
            try:
                player.slow_down(2)
            except Exception:
                pass
            # Eliminar obstáculo del nivel
            try:
                obstacles.remove(obstacle)
            except ValueError:
                pass

    # Comprobar colisiones con powerups
    for powerup in powerups[:]:
        if player.rect.colliderect(powerup.rect):
            # Reproducir sonido del powerup
            if powerup_sound:
                powerup_sound.play()
            player.speed_up(3)
            powerups.remove(powerup)

    # -------- DIBUJO (con cámara) --------
    for platform in platforms:
        SCREEN.blit(platform.image, camera.apply(platform.rect))

    for obstacle in obstacles:
        SCREEN.blit(obstacle.image, camera.apply(obstacle.rect))

    for powerup in powerups:
        SCREEN.blit(powerup.image, camera.apply(powerup.rect))

    # Dibujar el jugador usando su imagen visual escalada (display_image)
    SCREEN.blit(player.display_image, camera.apply(player.display_rect))
    SCREEN.blit(thief.image, camera.apply(thief.rect))

    # -------- DEBUG / HUD: mostrar ruta actual del ladrón --------
    # Texto en la esquina superior
    route_text = FONT.render(f"Ruta ladrón: {getattr(thief, 'route', 'N/A')}", True, BLACK)
    SCREEN.blit(route_text, (10, 10))
    # Texto sobre el ladrón eliminado (no mostrar etiqueta encima de su sprite)
    # Contador de FPS (esquina superior derecha)
    try:
        fps_val = int(CLOCK.get_fps())
    except Exception:
        fps_val = 0
    fps_text = FONT.render(f"FPS: {fps_val}", True, BLACK)
    SCREEN.blit(fps_text, (WIDTH - fps_text.get_width() - 8, 8))

    # -------- CONDICIÓN DE VICTORIA --------
    if player.rect.colliderect(thief.rect):
        restart = show_end_screen("¡HAS ATRAPADO AL LADRÓN!")
        if restart:
            platforms, obstacles, powerups, thief = load_game_level()
            player, camera = reset_game_state()
            continue
            camera = Camera(WIDTH, LEVEL_LENGTH)
            # reiniciar música de fondo
            try:
                pygame.mixer.music.play(-1)
            except Exception:
                pass
            continue
        else:
            pygame.quit()
            sys.exit()

    # -------- CONDICIÓN DE DERROTA: ladrón llega al final --------
    if thief_escaped:
        # detener la música de fondo
        pygame.mixer.music.stop()
        # reproducir sonido de game over
        if gameover_sound:
            gameover_sound.play()
        restart = show_end_screen("EL LADRÓN ESCAPÓ. FIN DE LA PARTIDA.")
        if restart:
            platforms, obstacles, powerups, thief = load_game_level()
            player, camera = reset_game_state()
            continue
        else:
            pygame.quit()
            sys.exit()

    # presentar la pantalla virtual escalada
    present_screen()