import pygame
import sys

from player import Player
from camera import Camera
from level1 import load_level, LEVEL_LENGTH
from platform import Platform, MovingPlatform
from obstacle import Obstacle
from powerup import PowerUp
from thief import Thief
import json
import os

pygame.init()

# ---------------- CONFIGURACIÓN ----------------
# Dimensiones por defecto en ventana (usadas al salir de fullscreen)
WINDOWED_SIZE = (900, 500)
# Inicializar pantalla en modo FULLSCREEN por defecto
SCREEN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = SCREEN.get_size()
pygame.display.set_caption("Nivel 1 - Plataformas con Cámara")

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
    bg_path = os.path.join(assets_dir, 'fondo_bicicletero.png')
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


def toggle_fullscreen():
    """Alterna entre fullscreen y ventana definida en WINDOWED_SIZE.

    Actualiza las variables globales SCREEN, WIDTH, HEIGHT y, si existe,
    actualiza camera.screen_width para que la cámara use el nuevo ancho.
    """
    global SCREEN, WIDTH, HEIGHT, bg_scroll_x
    is_full = bool(pygame.display.get_surface().get_flags() & pygame.FULLSCREEN)
    if is_full:
        # cambiar a ventana
        SCREEN = pygame.display.set_mode(WINDOWED_SIZE)
    else:
        SCREEN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    WIDTH, HEIGHT = SCREEN.get_size()
    # actualizar variables que dependen del tamaño de la pantalla
    pygame.display.set_caption(f"Nivel 1 - Plataformas con Cámara ({WIDTH}x{HEIGHT})")
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
    selecting = None  # objeto seleccionado (reference)
    dragging = False
    info_lines = [
        "Shift+J: salir del diseñador",
        "Click: seleccionar / arrastrar",
        "A: añadir Platform | O: añadir Obstacle | P: añadir PowerUp | M: añadir MovingPlatform",
        "Suprimir/Backspace: eliminar seleccionado | S: guardar | L: recargar",
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
                    mx, my = pygame.mouse.get_pos()
                    wx = mx + camera.offset_x
                    # añadir plataforma por defecto
                    newp = Platform(wx - 50, my - 10, 100, 20)
                    platforms.append(newp)
                    selecting = newp
                    dragging = True
                if event.key == pygame.K_o:
                    mx, my = pygame.mouse.get_pos()
                    wx = mx + camera.offset_x
                    newo = Obstacle(wx - 20, my - 20)
                    obstacles.append(newo)
                    selecting = newo
                    dragging = True
                if event.key == pygame.K_p:
                    mx, my = pygame.mouse.get_pos()
                    wx = mx + camera.offset_x
                    newpow = PowerUp(wx - 15, my - 15)
                    powerups.append(newpow)
                    selecting = newpow
                    dragging = True
                if event.key == pygame.K_m:
                    mx, my = pygame.mouse.get_pos()
                    wx = mx + camera.offset_x
                    # añadir plataforma móvil por defecto
                    newm = MovingPlatform(wx - 50, my - 10, 100, 20, axis='x', range_px=120, speed=1.0)
                    platforms.append(newm)
                    selecting = newm
                    dragging = True
                if event.key in (pygame.K_DELETE, pygame.K_BACKSPACE):
                    if selecting:
                        # eliminar del contenedor correspondiente
                        if isinstance(selecting, Platform):
                            if selecting in platforms:
                                platforms.remove(selecting)
                        elif isinstance(selecting, Obstacle):
                            if selecting in obstacles:
                                obstacles.remove(selecting)
                        elif isinstance(selecting, PowerUp):
                            if selecting in powerups:
                                powerups.remove(selecting)
                        selecting = None
                        dragging = False
                if event.key == pygame.K_s:
                    # guardar nivel a JSON
                    save_path = os.path.join(os.getcwd(), "level_custom.json")
                    try:
                        save_level_to_file(save_path, platforms, obstacles, powerups, thief)
                        print(f"Nivel guardado en {save_path}")
                    except Exception as e:
                        print("Error guardando nivel:", e)
                if event.key == pygame.K_l:
                    # recargar desde archivo si existe
                    load_path = os.path.join(os.getcwd(), "level_custom.json")
                    if os.path.exists(load_path):
                        try:
                            lp, lo, lpu, lth = load_level_from_file(load_path)
                            # reemplazar contenido de las listas pasadas por referencia
                            platforms.clear(); platforms.extend(lp)
                            obstacles.clear(); obstacles.extend(lo)
                            powerups.clear(); powerups.extend(lpu)
                            # actualizar posición del ladrón
                            thief.rect.topleft = (lth.rect.x, lth.rect.y)
                            selecting = None
                            dragging = False
                            print("Nivel recargado desde archivo")
                        except Exception as e:
                            print("Error cargando nivel:", e)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = event.pos
                    wx = mx + camera.offset_x
                    wy = my
                    # seleccionar el primer objeto bajo el cursor (prioridad: powerups, obstacles, platforms)
                    selecting = None
                    for lst in (powerups, obstacles, platforms):
                        for obj in reversed(lst):
                            if obj.rect.collidepoint((wx, wy)):
                                selecting = obj
                                dragging = True
                                break
                        if selecting:
                            break
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
            if event.type == pygame.MOUSEMOTION:
                if dragging and selecting:
                    mx, my = event.pos
                    wx = mx + camera.offset_x
                    wy = my
                    # mover el objeto centrando según su tamaño
                    w, h = selecting.rect.size
                    selecting.rect.topleft = (int(wx - w / 2), int(wy - h / 2))

        # manejo de teclas específicas para objeto seleccionado (fuera del loop de eventos)
        keys = pygame.key.get_pressed()
        if selecting and isinstance(selecting, MovingPlatform):
            # toggle axis
            if keys[pygame.K_x]:
                selecting.axis = 'y' if selecting.axis == 'x' else 'x'
                # pequeña espera para evitar toggle continuo
                pygame.time.wait(150)
            # range +/-
            if keys[pygame.K_r]:
                selecting.range = max(8, selecting.range - 10)
                pygame.time.wait(120)
            if keys[pygame.K_t]:
                selecting.range = selecting.range + 10
                pygame.time.wait(120)
            # speed +/-
            if keys[pygame.K_f]:
                selecting.speed = max(0.1, selecting.speed - 0.2)
                pygame.time.wait(120)
            if keys[pygame.K_g]:
                selecting.speed = selecting.speed + 0.2
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
        if selecting and isinstance(selecting, MovingPlatform):
            prop_lines.append(f"MovingPlatform axis={selecting.axis} range={int(selecting.range)} speed={round(selecting.speed,2)}")
            prop_lines.append("X: toggle axis | R/T: range -/+ 10 | F/G: speed -/+ 0.2")


        # Dibujar nivel actual con overlay
        SCREEN.fill(WHITE)
        # dibujar plataformas, obstáculos y powerups
        for plat in platforms:
            SCREEN.blit(plat.image, camera.apply(plat.rect))
        for obs in obstacles:
            SCREEN.blit(obs.image, camera.apply(obs.rect))
        for pu in powerups:
            SCREEN.blit(pu.image, camera.apply(pu.rect))

        # resaltar seleccionado
        if selecting:
            sel_rect = camera.apply(selecting.rect)
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

        pygame.display.update()


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
            })
        else:
            data['platforms'].append({
                'type': 'static',
                'x': p.rect.x,
                'y': p.rect.y,
                'w': p.rect.width,
                'h': p.rect.height,
            })

    data['obstacles'] = [{'x': o.rect.x, 'y': o.rect.y} for o in obstacles]
    data['powerups'] = [{'x': p.rect.x, 'y': p.rect.y} for p in powerups]
    data['thief'] = {'x': thief.rect.x, 'y': thief.rect.y}

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def load_level_from_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    platforms = []
    for p in data.get('platforms', []):
        if p.get('type') == 'moving':
            mp = MovingPlatform(int(p['x']), int(p['y']), int(p['w']), int(p['h']), axis=p.get('axis','x'), range_px=int(p.get('range',120)), speed=float(p.get('speed',1.0)))
            platforms.append(mp)
        else:
            platforms.append(Platform(int(p['x']), int(p['y']), int(p['w']), int(p['h'])))

    obstacles = [Obstacle(int(o['x']), int(o['y'])) for o in data.get('obstacles', [])]
    powerups = [PowerUp(int(p['x']), int(p['y'])) for p in data.get('powerups', [])]
    thief_data = data.get('thief', {'x': 400, 'y': 390})
    thief = Thief(int(thief_data.get('x', 400)), int(thief_data.get('y', 390)))

    return platforms, obstacles, powerups, thief


# ---------------- CARGAR NIVEL ----------------
# Si existe un nivel personalizado guardado, cargarlo automáticamente
custom_path = os.path.join(os.getcwd(), "level_custom.json")
if os.path.exists(custom_path):
    try:
        platforms, obstacles, powerups, thief = load_level_from_file(custom_path)
        print(f"Nivel personalizado cargado desde {custom_path}")
    except Exception as e:
        print("Error cargando nivel personalizado, cargando por defecto:", e)
        platforms, obstacles, powerups, thief = load_level()
else:
    platforms, obstacles, powerups, thief = load_level()

player = Player(50, 300)
camera = Camera(WIDTH, LEVEL_LENGTH)


def show_end_screen(message: str) -> bool:
    """Muestra una pantalla de fin con un botón de reinicio.

    Devuelve True si el jugador pulsa Reiniciar, False si cierra la ventana o
    pulsa Escape.
    """
    button_w, button_h = 220, 50
    button_rect = pygame.Rect((WIDTH - button_w) // 2, (HEIGHT // 2) + 40, button_w, button_h)

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
                if button_rect.collidepoint(event.pos):
                    return True

        # Fondo semitransparente
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((30, 30, 30))
        SCREEN.blit(overlay, (0, 0))

        # Mensaje centrado
        text = BIG_FONT.render(message, True, (255, 255, 255))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        SCREEN.blit(text, text_rect)

        # Botón
        pygame.draw.rect(SCREEN, (70, 130, 180), button_rect)
        btn_text = BUTTON_FONT.render("Reiniciar (R)", True, (255, 255, 255))
        btn_rect = btn_text.get_rect(center=button_rect.center)
        SCREEN.blit(btn_text, btn_rect)

        pygame.display.update()

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

    player.update(platforms, LEVEL_LENGTH)
    # Pasamos las plataformas y el jugador para que el ladrón ajuste su velocidad
    thief_escaped = thief.update(platforms, LEVEL_LENGTH, player)
    camera.update(player)

    # -------- COLISIONES --------
    for obstacle in obstacles:
        if player.rect.colliderect(obstacle.rect):
            player.slow_down(2)

    for powerup in powerups[:]:
        if player.rect.colliderect(powerup.rect):
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

    # Texto sobre el ladrón (convertir rect al espacio de la cámara)
    thief_screen_rect = camera.apply(thief.rect)
    route_on_thief = FONT.render(f"{getattr(thief, 'route', '')}", True, (255, 255, 255))
    # dibujar fondo pequeño para legibilidad
    bg = pygame.Surface((route_on_thief.get_width() + 6, route_on_thief.get_height() + 4))
    bg.set_alpha(180)
    bg.fill((0, 0, 0))
    SCREEN.blit(bg, (thief_screen_rect.x, thief_screen_rect.y - 22))
    SCREEN.blit(route_on_thief, (thief_screen_rect.x + 3, thief_screen_rect.y - 20))

    # -------- CONDICIÓN DE VICTORIA --------
    if player.rect.colliderect(thief.rect):
        restart = show_end_screen("¡HAS ATRAPADO AL LADRÓN!")
        if restart:
            # recargar nivel
            platforms, obstacles, powerups, thief = load_level()
            player = Player(50, 300)
            camera = Camera(WIDTH, LEVEL_LENGTH)
            continue
        else:
            pygame.quit()
            sys.exit()

    # -------- CONDICIÓN DE DERROTA: ladrón llega al final --------
    if thief_escaped:
        restart = show_end_screen("EL LADRÓN ESCAPÓ. FIN DE LA PARTIDA.")
        if restart:
            platforms, obstacles, powerups, thief = load_level()
            player = Player(50, 300)
            camera = Camera(WIDTH, LEVEL_LENGTH)
            continue
        else:
            pygame.quit()
            sys.exit()

    pygame.display.update()