import os
import pygame
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

def resolver_recurso_audio(nombre):
    if not nombre:
        return nombre

    nombre_normalizado = nombre.replace('\\', os.sep).replace('/', os.sep)
    if os.path.isabs(nombre_normalizado) and os.path.exists(nombre_normalizado):
        return nombre_normalizado

    nombre_archivo = os.path.basename(nombre_normalizado)
    nombre_archivo_lower = nombre_archivo.lower()

    for carpeta in (BASE_DIR, ROOT_DIR):
        ruta_relativa = os.path.join(carpeta, nombre_normalizado)
        if os.path.exists(ruta_relativa):
            return ruta_relativa

        ruta_por_nombre = os.path.join(carpeta, nombre_archivo)
        if os.path.exists(ruta_por_nombre):
            return ruta_por_nombre

    for carpeta in (BASE_DIR, ROOT_DIR):
        for raiz, directorios, archivos in os.walk(carpeta):
            directorios[:] = [d for d in directorios if d not in ('__pycache__', '.git', '.venv', 'venv')]
            for archivo in archivos:
                if archivo.lower() == nombre_archivo_lower:
                    return os.path.join(raiz, archivo)

    return nombre

HIT_SOUND_FILE = 'crash.mp3'
hit_sound = None
hit_sound_loaded = False
HORN_SOUND_FILES = ['claxon.mp3', 'claxon2.mp3']
horn_sounds = []
horn_sound_loaded = False
horn_turn_index = 0
HORN_PROBABILIDAD = 0.22
HORN_MIN_INTERVAL_MS = 4500
last_horn_time_ms = -HORN_MIN_INTERVAL_MS
horn_channel = None

# --- INICIALIZACIÓN ---
pygame.init()
# Inicializar el mezclador de audio y reproducir música de fondo (si existe)
try:
    pygame.mixer.init()
    MUSIC_FILE = 'NIVEL2.mp3'  # Música del nivel
    GAMEOVER_MUSIC_FILE = 'GAME_OVER.mp3'  # Música de game over
    WIN_MUSIC_FILE = 'WIN.mp3'  # Música al ganar
    music_loaded = False
    gameover_music_loaded = False
    win_music_loaded = False
    try:
        pygame.mixer.music.load(resolver_recurso_audio(MUSIC_FILE))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)  # Reproducir en bucle infinito
        music_loaded = True
    except Exception as e:
        print(f"No se pudo cargar la música '{MUSIC_FILE}':", e)
    try:
        gameover_music_loaded = True  # Flag para comprobar si se puede cargar
    except Exception as e:
        print(f"No se pudo cargar la música '{GAMEOVER_MUSIC_FILE}':", e)
        gameover_music_loaded = False
    try:
        win_music_loaded = True  # Flag para comprobar si se puede cargar
    except Exception as e:
        print(f"No se pudo cargar la música '{WIN_MUSIC_FILE}':", e)
        win_music_loaded = False
except Exception:
    music_loaded = False
    gameover_music_loaded = False
    win_music_loaded = False
ANCHO_BASE, ALTO_BASE = 800, 600
ANCHO, ALTO = ANCHO_BASE, ALTO_BASE
MODOS_PANTALLA = ["Pantalla completa", "Ventana"]
modo_pantalla_actual = "Pantalla completa"

def aplicar_modo_pantalla(modo):
    global ANCHO, ALTO
    if modo == "Pantalla completa":
        try:
            ANCHO, ALTO = pygame.display.get_desktop_sizes()[0]
        except Exception:
            info = pygame.display.Info()
            ANCHO, ALTO = info.current_w, info.current_h
        return pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
    ANCHO, ALTO = ANCHO_BASE, ALTO_BASE
    return pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)

VENTANA = aplicar_modo_pantalla(modo_pantalla_actual)
pygame.display.set_caption("Misión: Camino a la Escuela")

# --- CONFIGURACIÓN DE LA CARRETERA (Ajustado a la imagen de Cádiz) ---
NUM_CARRILES = 4
ALTURA_CARRIL_BASE = 60   # Píxeles de ancho de cada carril gris en 800x600
LANE_START_Y_BASE = 275   # Dónde empieza el asfalto en la imagen en 800x600

def actualizar_parametros_carriles():
    global ALTURA_CARRIL, LANE_START_Y, LANE_AREA_BOTTOM
    escala_y = ALTO / ALTO_BASE if ALTO_BASE else 1.0
    ALTURA_CARRIL = max(1, int(ALTURA_CARRIL_BASE * escala_y))
    LANE_START_Y = int(LANE_START_Y_BASE * escala_y)
    LANE_AREA_BOTTOM = LANE_START_Y + (NUM_CARRILES * ALTURA_CARRIL)

actualizar_parametros_carriles()

# Colores de respaldo
BLANCO = (255, 255, 255)
ROJO = (200, 0, 0)
AZUL = (0, 0, 200)

PERFILES_DIFICULTAD = {
    "Fácil": {
        "vel_base": (3, 6),
        "vel_alta": (3, 8),
        "obstaculos_base": 3,
        "obstaculos_max": 4,
        "mult_dificultad_max": 1.45,
        "segundo_subida": 42000,
    },
    "Normal": {
        "vel_base": (4, 7),
        "vel_alta": (4, 9),
        "obstaculos_base": 4,
        "obstaculos_max": 5,
        "mult_dificultad_max": 1.65,
        "segundo_subida": 36000,
    },
    "Difícil": {
        "vel_base": (5, 8),
        "vel_alta": (5, 10),
        "obstaculos_base": 5,
        "obstaculos_max": 6,
        "mult_dificultad_max": 1.85,
        "segundo_subida": 30000,
    },
}
DIFICULTADES = list(PERFILES_DIFICULTAD.keys())
dificultad_actual = "Normal"

VEL_MIN_BASE = 4
VEL_MAX_BASE = 7
VEL_MIN_ALTA = 4
VEL_MAX_ALTA = 9
OBSTACULOS_BASE = 4
OBSTACULOS_MAX = 5
MULT_DIFICULTAD_MAX = 1.65
SEGUNDO_SUBIDA_DENSIDAD = 36000

music_volume = 0.5
music_muted = False

def aplicar_volumen_musica():
    if music_loaded:
        pygame.mixer.music.set_volume(0.0 if music_muted else music_volume)

def aplicar_dificultad(nombre):
    global dificultad_actual
    global VEL_MIN_BASE, VEL_MAX_BASE, VEL_MIN_ALTA, VEL_MAX_ALTA
    global OBSTACULOS_BASE, OBSTACULOS_MAX, MULT_DIFICULTAD_MAX, SEGUNDO_SUBIDA_DENSIDAD

    if nombre not in PERFILES_DIFICULTAD:
        return

    cfg = PERFILES_DIFICULTAD[nombre]
    dificultad_actual = nombre
    VEL_MIN_BASE, VEL_MAX_BASE = cfg["vel_base"]
    VEL_MIN_ALTA, VEL_MAX_ALTA = cfg["vel_alta"]
    OBSTACULOS_BASE = cfg["obstaculos_base"]
    OBSTACULOS_MAX = cfg["obstaculos_max"]
    MULT_DIFICULTAD_MAX = cfg["mult_dificultad_max"]
    SEGUNDO_SUBIDA_DENSIDAD = cfg["segundo_subida"]

def velocidad_obstaculo(tiempo_transcurrido):
    if tiempo_transcurrido >= 30000:
        return random.randint(VEL_MIN_ALTA, VEL_MAX_ALTA)
    return random.randint(VEL_MIN_BASE, VEL_MAX_BASE)

def cantidad_obstaculos_inicial():
    minimo = min(OBSTACULOS_BASE, OBSTACULOS_MAX)
    maximo = max(OBSTACULOS_BASE, OBSTACULOS_MAX)
    return random.randint(minimo, maximo)

recurso_cache = {}

def resolver_recurso(nombre):
    if not nombre:
        return nombre

    nombre_normalizado = nombre.replace('\\', os.sep).replace('/', os.sep)

    if os.path.isabs(nombre_normalizado) and os.path.exists(nombre_normalizado):
        return nombre_normalizado

    nombre_archivo = os.path.basename(nombre_normalizado)
    nombre_archivo_lower = nombre_archivo.lower()

    for carpeta in (BASE_DIR, ROOT_DIR):
        ruta_relativa = os.path.join(carpeta, nombre_normalizado)
        if os.path.exists(ruta_relativa):
            return ruta_relativa

        ruta_por_nombre = os.path.join(carpeta, nombre_archivo)
        if os.path.exists(ruta_por_nombre):
            return ruta_por_nombre

    ruta_cache = recurso_cache.get(nombre_archivo_lower)
    if ruta_cache and os.path.exists(ruta_cache):
        return ruta_cache

    for carpeta in (BASE_DIR, ROOT_DIR):
        for raiz, directorios, archivos in os.walk(carpeta):
            directorios[:] = [d for d in directorios if d not in ('__pycache__', '.git', '.venv', 'venv')]
            for archivo in archivos:
                if archivo.lower() == nombre_archivo_lower:
                    ruta_encontrada = os.path.join(raiz, archivo)
                    recurso_cache[nombre_archivo_lower] = ruta_encontrada
                    return ruta_encontrada

    return nombre

def cargar_sonido(nombre):
    try:
        return pygame.mixer.Sound(resolver_recurso(nombre))
    except:
        return None

if pygame.mixer.get_init():
    horn_channel = pygame.mixer.Channel(2)
    hit_sound = cargar_sonido(HIT_SOUND_FILE)
    hit_sound_loaded = hit_sound is not None
    if hit_sound:
        hit_sound.set_volume(0.7)

    horn_sounds = [sonido for sonido in (cargar_sonido(nombre) for nombre in HORN_SOUND_FILES) if sonido is not None]
    horn_sound_loaded = len(horn_sounds) > 0
    for sonido in horn_sounds:
        sonido.set_volume(0.55)

def reproducir_sonido_choque():
    if hit_sound_loaded and hit_sound:
        try:
            hit_sound.play()
        except:
            pass

def reproducir_claxon_ambiental():
    global horn_turn_index, last_horn_time_ms
    if 'nivel_iniciado' in globals() and not nivel_iniciado:
        return
    if not horn_sound_loaded or not horn_sounds:
        return
    ahora = pygame.time.get_ticks()
    if ahora - last_horn_time_ms < HORN_MIN_INTERVAL_MS:
        return
    if horn_channel and horn_channel.get_busy():
        return
    if random.random() > HORN_PROBABILIDAD:
        return
    try:
        if horn_channel:
            horn_channel.play(horn_sounds[horn_turn_index])
        else:
            horn_sounds[horn_turn_index].play()
        last_horn_time_ms = ahora
        horn_turn_index = (horn_turn_index + 1) % len(horn_sounds)
    except:
        pass

# --- CARGA DE RECURSOS ---
def cargar_recurso(nombre, escala):
    try:
        img = pygame.image.load(resolver_recurso(nombre)).convert_alpha()
        return pygame.transform.smoothscale(img, escala)
    except:
        return None

def cargar_recurso_original(nombre):
    try:
        return pygame.image.load(resolver_recurso(nombre)).convert_alpha()
    except:
        return None

def escalar_sin_deformar(img, max_ancho, max_alto):
    if img is None:
        return None
    ancho, alto = img.get_size()
    if ancho <= max_ancho and alto <= max_alto:
        return img

    factor = min(max_ancho / ancho, max_alto / alto)
    nuevo_ancho = max(1, int(ancho * factor))
    nuevo_alto = max(1, int(alto * factor))
    return pygame.transform.smoothscale(img, (nuevo_ancho, nuevo_alto))

def cargar_spritesheet(nombre, frame_ancho, frame_alto, num_frames, escala):
    try:
        sheet = pygame.image.load(resolver_recurso(nombre)).convert_alpha()
        ancho_sheet = sheet.get_width()

        if not num_frames or num_frames <= 0:
            num_frames = max(1, ancho_sheet // frame_ancho)

        if ancho_sheet < frame_ancho:
            return []

        frames = []
        for i in range(num_frames):
            if (i + 1) * frame_ancho > ancho_sheet:
                break
            frame = pygame.Surface((frame_ancho, frame_alto), pygame.SRCALPHA)
            frame.blit(sheet, (0, 0), pygame.Rect(i * frame_ancho, 0, frame_ancho, frame_alto))
            frame = pygame.transform.smoothscale(frame, escala)
            frames.append(frame)
        return frames
    except:
        return []

# Cargamos el fondo y los personajes
bg_img = cargar_recurso('cadiz9.png', (ANCHO, ALTO))
player_img_original = cargar_recurso_original('lvl2.png')
player_img = player_img_original
vida_img = cargar_recurso('vida.png', (32, 32))

PLAYER_MAX_ANCHO_BASE = 76
PLAYER_MAX_ANCHO = PLAYER_MAX_ANCHO_BASE
PLAYER_MAX_ALTO = ALTURA_CARRIL - 14
player_img = escalar_sin_deformar(player_img_original, PLAYER_MAX_ANCHO, PLAYER_MAX_ALTO)

# Animación del jugador con 3 sprites separados
PLAYER_ANIM_MS = 80

player_idle_original = cargar_recurso_original('1.png')
player_move_originals = [
    cargar_recurso_original('2.png'),
    cargar_recurso_original('3.png'),
]

player_idle_frame = escalar_sin_deformar(player_idle_original, PLAYER_MAX_ANCHO, PLAYER_MAX_ALTO) if player_idle_original else player_img
player_move_frames = [escalar_sin_deformar(frame, PLAYER_MAX_ANCHO, PLAYER_MAX_ALTO) for frame in player_move_originals]
player_move_frames = [frame for frame in player_move_frames if frame is not None]
if not player_move_frames and player_idle_frame is not None:
    player_move_frames = [player_idle_frame]

player_frames = [player_idle_frame] + player_move_frames if player_idle_frame else player_move_frames
player_anim_frames = [frame for frame in [player_idle_frame] + player_move_frames if frame is not None]

OBSTACULO_ESCALA = 0.98
CAR_BASE_ANCHO, CAR_BASE_ALTO = 80, 40
BUS_BASE_ANCHO, BUS_BASE_ALTO = 140, 50
CAR_ANCHO = max(1, int(CAR_BASE_ANCHO * OBSTACULO_ESCALA))
CAR_ALTO = max(1, int(CAR_BASE_ALTO * OBSTACULO_ESCALA))
BUS_ANCHO = max(1, int(BUS_BASE_ANCHO * OBSTACULO_ESCALA))
BUS_ALTO = max(1, int(BUS_BASE_ALTO * OBSTACULO_ESCALA))

# Cargar múltiples sprites de coches
car_images_original = [
    cargar_recurso_original('car1.png'),
    cargar_recurso_original('car2.png'),
    cargar_recurso_original('car3.png'),
    cargar_recurso_original('car4.png')
]
car_images = [
    escalar_sin_deformar(img, CAR_ANCHO, CAR_ALTO) if img else None
    for img in car_images_original
]
car_images = [img for img in car_images if img is not None]

# Cargar múltiples sprites de autobuses
bus_images_original = [
    cargar_recurso_original('bus1.png'),
    cargar_recurso_original('bus2.png'),
    cargar_recurso_original('bus3.png'),
    cargar_recurso_original('bus4.png'),
]
bus_images = [
    escalar_sin_deformar(img, BUS_ANCHO, BUS_ALTO) if img else None
    for img in bus_images_original
]
bus_images = [img for img in bus_images if img is not None]

def recalcular_escalado_elementos():
    global PLAYER_MAX_ANCHO, PLAYER_MAX_ALTO, JUGADOR_HITBOX_SIZE
    global CAR_ANCHO, CAR_ALTO, BUS_ANCHO, BUS_ALTO
    global player_img, player_frames, player_idle_frame, player_move_frames, player_anim_frames, car_images, bus_images

    escala_resolucion = ALTO / ALTO_BASE if ALTO_BASE else 1.0

    PLAYER_MAX_ANCHO = max(1, int(PLAYER_MAX_ANCHO_BASE * escala_resolucion))
    PLAYER_MAX_ALTO = max(1, ALTURA_CARRIL - max(8, int(14 * escala_resolucion)))
    player_img = escalar_sin_deformar(player_img_original, PLAYER_MAX_ANCHO, PLAYER_MAX_ALTO)

    player_idle_frame = escalar_sin_deformar(player_idle_original, PLAYER_MAX_ANCHO, PLAYER_MAX_ALTO) if player_idle_original else player_img
    player_move_frames = [escalar_sin_deformar(frame, PLAYER_MAX_ANCHO, PLAYER_MAX_ALTO) for frame in player_move_originals]
    player_move_frames = [frame for frame in player_move_frames if frame is not None]
    if not player_move_frames and player_idle_frame is not None:
        player_move_frames = [player_idle_frame]
    player_frames = [player_idle_frame] + player_move_frames if player_idle_frame else player_move_frames
    player_anim_frames = [frame for frame in [player_idle_frame] + player_move_frames if frame is not None]

    CAR_ANCHO = max(1, int(CAR_BASE_ANCHO * OBSTACULO_ESCALA * escala_resolucion))
    CAR_ALTO = max(1, int(CAR_BASE_ALTO * OBSTACULO_ESCALA * escala_resolucion))
    BUS_ANCHO = max(1, int(BUS_BASE_ANCHO * OBSTACULO_ESCALA * escala_resolucion))
    BUS_ALTO = max(1, int(BUS_BASE_ALTO * OBSTACULO_ESCALA * escala_resolucion))

    car_images = [escalar_sin_deformar(img, CAR_ANCHO, CAR_ALTO) if img else None for img in car_images_original]
    car_images = [img for img in car_images if img is not None]

    bus_images = [escalar_sin_deformar(img, BUS_ANCHO, BUS_ALTO) if img else None for img in bus_images_original]
    bus_images = [img for img in bus_images if img is not None]

    if player_frames:
        base_w, base_h = player_frames[0].get_size()
    elif player_img:
        base_w, base_h = player_img.get_size()
    else:
        base_w, base_h = (80, 40)
    JUGADOR_HITBOX_SIZE = min(base_w, base_h)

recalcular_escalado_elementos()

# --- CLASE PARA LOS OBSTÁCULOS ---
class Obstaculo:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.rect = pygame.Rect(0, 0, CAR_ANCHO, CAR_ALTO)
        self.vel = 5
        self.es_bus = False
        self.image = None
        self.carril = 0
        self.carril_objetivo = 0
        self.y_objetivo = 0
        self.cambiando_carril = False
        self.vel_cambio_carril = 4
        self.ya_cambio_carril = False

    def reset(self, lista_obstaculos=None, tiempo_transcurrido=0, jugador=None):
        colision = True
        intentos = 0
        max_intentos = 30
        huecos_objetivo = self._huecos_objetivo_spawn(tiempo_transcurrido)
        
        while colision and intentos < max_intentos:
            carril = random.randint(0, NUM_CARRILES - 1)
            self.carril = carril
            self.carril_objetivo = carril
            self.es_bus = random.random() > 0.7
            self.ancho = BUS_ANCHO if self.es_bus else CAR_ANCHO
            self.alto = BUS_ALTO if self.es_bus else CAR_ALTO
            # Posición inicial fuera de pantalla a la derecha
            if tiempo_transcurrido >= 30000:
                self.x = ANCHO + random.randint(80, 220)
            else:
                self.x = ANCHO + random.randint(100, 500)
            # Centrar en el carril
            self.y = LANE_START_Y + (carril * ALTURA_CARRIL) + (ALTURA_CARRIL//2 - self.alto//2)
            self.y_objetivo = self.y
            self.cambiando_carril = False
            self.ya_cambio_carril = False
            self.rect = pygame.Rect(self.x, self.y, self.ancho, self.alto)
            self.vel = velocidad_obstaculo(tiempo_transcurrido)
            
            # Elegir sprite aleatorio
            if self.es_bus and bus_images:
                self.image = random.choice(bus_images)
            elif car_images:
                self.image = random.choice(car_images)
            else:
                self.image = None
            
            # Verificar colisiones con otros obstáculos
            colision = False
            if lista_obstaculos:
                for otro_obs in lista_obstaculos:
                    if otro_obs is self:
                        continue
                    if self.rect.colliderect(otro_obs.rect):
                        colision = True
                        break
                    if otro_obs.carril == self.carril and abs(self.rect.centerx - otro_obs.rect.centerx) < 150:
                        colision = True
                        break

            if not colision and not self._spawn_deja_huecos(lista_obstaculos, jugador, huecos_objetivo):
                colision = True
            
            intentos += 1

        # Fallback seguro: nunca dejar un spawn inválido que bloquee todos los carriles
        if colision:
            ocupacion = {c: 0 for c in range(NUM_CARRILES)}
            x_max = ANCHO
            if lista_obstaculos:
                for obs in lista_obstaculos:
                    if obs is self:
                        continue
                    ocupacion[obs.carril] += 1
                    x_max = max(x_max, obs.rect.right)

            carril_seguro = min(ocupacion, key=ocupacion.get)
            self.carril = carril_seguro
            self.carril_objetivo = carril_seguro
            self.es_bus = random.random() > 0.7
            self.ancho = BUS_ANCHO if self.es_bus else CAR_ANCHO
            self.alto = BUS_ALTO if self.es_bus else CAR_ALTO
            self.x = x_max + random.randint(180, 320)
            self.y = LANE_START_Y + (carril_seguro * ALTURA_CARRIL) + (ALTURA_CARRIL // 2 - self.alto // 2)
            self.y_objetivo = self.y
            self.cambiando_carril = False
            self.ya_cambio_carril = False
            self.rect = pygame.Rect(self.x, self.y, self.ancho, self.alto)
            self.vel = velocidad_obstaculo(tiempo_transcurrido)

            if self.es_bus and bus_images:
                self.image = random.choice(bus_images)
            elif car_images:
                self.image = random.choice(car_images)
            else:
                self.image = None

        if not self.es_bus:
            reproducir_claxon_ambiental()

    def _huecos_objetivo_spawn(self, tiempo_transcurrido):
        if NUM_CARRILES < 3:
            return 1

        mitad_nivel = duracion_nivel // 2 if 'duracion_nivel' in globals() else 30000
        if tiempo_transcurrido < mitad_nivel:
            return 2 if random.random() < 0.65 else 1
        return 1

    def _spawn_deja_huecos(self, lista_obstaculos, jugador, huecos_objetivo):
        if jugador is None:
            return True

        margen = max(32, jugador.width)
        rango_x = max(self.ancho, 220) + margen
        carriles_bloqueados = {self.carril}

        if lista_obstaculos:
            for obs in lista_obstaculos:
                if obs is self:
                    continue
                if abs(obs.rect.centerx - self.rect.centerx) < rango_x:
                    carriles_bloqueados.add(obs.carril)

        huecos_libres = NUM_CARRILES - len(carriles_bloqueados)
        minimo_huecos = max(1, min(huecos_objetivo, NUM_CARRILES - 1))
        return huecos_libres >= minimo_huecos

    def _carril_de_jugador(self, jugador):
        if not jugador:
            return None
        carril = (jugador.centery - LANE_START_Y) // ALTURA_CARRIL
        return max(0, min(NUM_CARRILES - 1, int(carril)))

    def _hay_hueco_libre(self, lista_obstaculos, carril_destino):
        carriles_ocupados = set()
        for obs in lista_obstaculos:
            if obs is self:
                continue
            if abs(obs.rect.centerx - self.rect.centerx) < 170:
                carriles_ocupados.add(obs.carril)
        carriles_ocupados.add(carril_destino)
        return len(carriles_ocupados) < NUM_CARRILES

    def actualizar_cambio_carril(self):
        if not self.cambiando_carril:
            return

        distancia = self.y_objetivo - self.y
        if abs(distancia) <= self.vel_cambio_carril:
            self.y = self.y_objetivo
            self.cambiando_carril = False
        else:
            self.y += self.vel_cambio_carril if distancia > 0 else -self.vel_cambio_carril

        self.rect.y = int(self.y)

    def intentar_cambiar_carril(self, lista_obstaculos, jugador):
        if self.ya_cambio_carril:
            return False

        opciones = [self.carril - 1, self.carril + 1]
        opciones = [c for c in opciones if 0 <= c < NUM_CARRILES]
        random.shuffle(opciones)

        carril_jugador = self._carril_de_jugador(jugador)
        for nuevo_carril in opciones:
            if carril_jugador is not None and nuevo_carril == carril_jugador:
                continue

            nuevo_y = LANE_START_Y + (nuevo_carril * ALTURA_CARRIL) + (ALTURA_CARRIL // 2 - self.alto // 2)
            nuevo_rect = pygame.Rect(self.rect.x, nuevo_y, self.ancho, self.alto)

            colisiona = False
            for otro_obs in lista_obstaculos:
                if otro_obs is self:
                    continue
                if nuevo_rect.colliderect(otro_obs.rect):
                    colisiona = True
                    break
            if colisiona:
                continue

            if not self._hay_hueco_libre(lista_obstaculos, nuevo_carril):
                continue

            self.carril = nuevo_carril
            self.carril_objetivo = nuevo_carril
            self.y_objetivo = nuevo_y
            self.cambiando_carril = True
            self.ya_cambio_carril = True
            self.vel = velocidad_obstaculo(0)
            return True

        return False

    def ajustar_trafico(self, otro_obs):
        if self.x >= otro_obs.x:
            separacion_segura = 18
            self.x = otro_obs.x + otro_obs.ancho + separacion_segura
            self.rect.x = int(self.x)
            self.vel = max(2.0, min(float(self.vel), float(otro_obs.vel) - 0.2))
        else:
            self.vel = max(2.0, float(self.vel))

    def mover(self, lista_obstaculos=None, tiempo_transcurrido=0, factor_velocidad=1.0, jugador=None):
        self.x -= self.vel * factor_velocidad
        self.rect.x = self.x
        self.actualizar_cambio_carril()
        
        # Detectar colisiones con otros obstáculos durante el movimiento
        if lista_obstaculos:
            for otro_obs in lista_obstaculos:
                if otro_obs is not self and self.rect.colliderect(otro_obs.rect):
                    # Si no puede cambiar de carril, ajusta velocidad para no quedarse bloqueado
                    self.ajustar_trafico(otro_obs)
                    return
        
        # Si no hay colisión, recuperar velocidad gradualmente para evitar trenes pegados
        vel_objetivo = float(velocidad_obstaculo(tiempo_transcurrido))
        if self.vel < vel_objetivo:
            self.vel = min(vel_objetivo, self.vel + 0.12)
        elif self.vel <= 0:
            self.vel = vel_objetivo
        
        # Si salimos de pantalla, reiniciar solo si no han pasado 56 segundos
        if self.x + self.ancho < 0:
            if tiempo_transcurrido < 56000:
                self.reset(lista_obstaculos, tiempo_transcurrido, jugador)

def desatascar_obstaculos(lista_obstaculos):
    separacion_min = 18
    for carril in range(NUM_CARRILES):
        obstaculos_carril = [obs for obs in lista_obstaculos if obs.carril == carril and not obs.cambiando_carril]
        obstaculos_carril.sort(key=lambda obs: obs.x)

        for i in range(1, len(obstaculos_carril)):
            obs_adelante = obstaculos_carril[i - 1]
            obs_detras = obstaculos_carril[i]
            limite_detras = obs_adelante.x + obs_adelante.ancho + separacion_min

            if obs_detras.x < limite_detras:
                obs_detras.x = limite_detras
                obs_detras.rect.x = int(obs_detras.x)
                obs_detras.vel = max(1, min(int(obs_detras.vel), int(obs_adelante.vel)))

# --- ESTADO INICIAL DEL JUEGO ---
if player_frames:
    base_w, base_h = player_frames[0].get_size()
elif player_img:
    base_w, base_h = player_img.get_size()
else:
    base_w, base_h = (80, 40)

JUGADOR_HITBOX_SIZE = min(base_w, base_h)
jugador = pygame.Rect(100, ALTO // 2, JUGADOR_HITBOX_SIZE, JUGADOR_HITBOX_SIZE)
scroll_x = 0
velocidad_fondo = 3
MAX_VIDAS = 3
vidas = MAX_VIDAS
invulnerable = False
tiempo_invulnerable = 0
TIEMPO_INVULNERABLE = 1500
vida_perdida_indice = -1
tiempo_parpadeo_vida = 0
DURACION_PARPADEO_VIDA = 700
INTERVALO_PARPADEO_VIDA = 120
tiempo_inicio = pygame.time.get_ticks()
duracion_nivel = 60000  # 1 minuto en milisegundos
reloj = pygame.time.Clock()
juego_activo = True
game_over = False
tiempo_game_over = None
nivel_completado = False
player_frame_index = 0
player_last_anim_time = pygame.time.get_ticks()
player_anim_offset_y = 0
menu_pausa_activo = False
indice_menu_pausa = 0
tiempo_pausa_acumulado = 0
inicio_pausa = None
nivel_iniciado = False
cursor_visible = True
pygame.mouse.set_visible(True)
aplicar_dificultad(dificultad_actual)
aplicar_volumen_musica()
OBSTACULOS_INICIO_NIVEL = cantidad_obstaculos_inicial()
lista_obstaculos = [Obstaculo() for _ in range(OBSTACULOS_INICIO_NIVEL)]
for obs in lista_obstaculos:
    obs.reset(lista_obstaculos, 0, jugador)

def reiniciar_partida():
    global vidas, invulnerable, tiempo_invulnerable, vida_perdida_indice, tiempo_parpadeo_vida
    global lista_obstaculos, scroll_x, game_over, tiempo_game_over, nivel_completado
    global player_frame_index, player_last_anim_time, player_anim_offset_y, tiempo_inicio
    global tiempo_pausa_acumulado, inicio_pausa, menu_pausa_activo, indice_menu_pausa
    global OBSTACULOS_INICIO_NIVEL, nivel_iniciado, cursor_visible

    vidas = MAX_VIDAS
    invulnerable = False
    tiempo_invulnerable = 0
    vida_perdida_indice = -1
    tiempo_parpadeo_vida = 0
    OBSTACULOS_INICIO_NIVEL = cantidad_obstaculos_inicial()
    lista_obstaculos = [Obstaculo() for _ in range(OBSTACULOS_INICIO_NIVEL)]
    for obs in lista_obstaculos:
        obs.reset(lista_obstaculos, 0, jugador)
    jugador.x = 100
    jugador.y = ALTO // 2
    scroll_x = 0
    game_over = False
    tiempo_game_over = None
    nivel_completado = False
    player_frame_index = 0
    player_last_anim_time = pygame.time.get_ticks()
    player_anim_offset_y = 0
    tiempo_inicio = pygame.time.get_ticks()
    tiempo_pausa_acumulado = 0
    inicio_pausa = None
    nivel_iniciado = False
    cursor_visible = True
    pygame.mouse.set_visible(True)
    menu_pausa_activo = False
    indice_menu_pausa = 0

    if music_loaded:
        pygame.mixer.music.load(resolver_recurso_audio(MUSIC_FILE))
        aplicar_volumen_musica()
        pygame.mixer.music.play(-1)

def cerrar_menu_pausa():
    global menu_pausa_activo, tiempo_pausa_acumulado, inicio_pausa
    menu_pausa_activo = False
    if inicio_pausa is not None:
        tiempo_pausa_acumulado += pygame.time.get_ticks() - inicio_pausa
        inicio_pausa = None

def ejecutar_opcion_menu_pausa(opcion):
    global music_muted, juego_activo
    if opcion == 0:
        cerrar_menu_pausa()
    elif opcion == 2:
        music_muted = not music_muted
        aplicar_volumen_musica()
    elif opcion == 3:
        idx = DIFICULTADES.index(dificultad_actual)
        aplicar_dificultad(DIFICULTADES[(idx + 1) % len(DIFICULTADES)])
    elif opcion == 4:
        idx = MODOS_PANTALLA.index(modo_pantalla_actual)
        cambiar_modo_pantalla(MODOS_PANTALLA[(idx + 1) % len(MODOS_PANTALLA)])
    elif opcion == 5:
        reiniciar_partida()
    elif opcion == 6:
        juego_activo = False

def layout_menu_pausa():
    ancho_ui, alto_ui = VENTANA.get_size()
    escala = max(1.0, min(3.2, min(ancho_ui / ANCHO_BASE, alto_ui / ALTO_BASE)))
    titulo_y = int(alto_ui * 0.18)
    inicio_opciones_y = int(alto_ui * 0.36)
    separacion_y = max(42, int(alto_ui * 0.085))
    ayuda_y = int(alto_ui * 0.92)
    return {
        "ancho_ui": ancho_ui,
        "alto_ui": alto_ui,
        "escala": escala,
        "titulo_y": titulo_y,
        "inicio_opciones_y": inicio_opciones_y,
        "separacion_y": separacion_y,
        "ayuda_y": ayuda_y,
        "rect_ancho": min(int(ancho_ui * 0.75), int(900 * escala)),
        "rect_alto": max(44, int(54 * escala)),
    }

def obtener_rect_opcion_pausa(indice):
    layout = layout_menu_pausa()
    rect = pygame.Rect(0, 0, layout["rect_ancho"], layout["rect_alto"])
    rect.center = (
        layout["ancho_ui"] // 2,
        layout["inicio_opciones_y"] + indice * layout["separacion_y"],
    )
    return rect

def cambiar_modo_pantalla(nuevo_modo):
    global modo_pantalla_actual, VENTANA
    if nuevo_modo not in MODOS_PANTALLA:
        return
    modo_pantalla_actual = nuevo_modo
    VENTANA = aplicar_modo_pantalla(modo_pantalla_actual)
    actualizar_escena_tras_cambio_modo()

def actualizar_escena_tras_cambio_modo():
    global bg_img, scroll_x
    carril_anterior = 0
    if ALTURA_CARRIL > 0:
        carril_anterior = int((jugador.centery - LANE_START_Y) // ALTURA_CARRIL)
    carril_anterior = max(0, min(NUM_CARRILES - 1, carril_anterior))

    actualizar_parametros_carriles()
    recalcular_escalado_elementos()
    bg_img = cargar_recurso('cadiz9.png', (ANCHO, ALTO))
    centro_jugador_x = jugador.centerx
    jugador.size = (JUGADOR_HITBOX_SIZE, JUGADOR_HITBOX_SIZE)
    jugador.centerx = max(jugador.width // 2, min(centro_jugador_x, ANCHO - (jugador.width // 2)))
    jugador.centery = LANE_START_Y + (carril_anterior * ALTURA_CARRIL) + (ALTURA_CARRIL // 2)
    jugador.y = max(LANE_START_Y, min(jugador.y, LANE_AREA_BOTTOM - jugador.height))

    if 'lista_obstaculos' in globals():
        for obs in lista_obstaculos:
            carril_obs = max(0, min(NUM_CARRILES - 1, int(getattr(obs, 'carril', 0))))
            carril_obj = max(0, min(NUM_CARRILES - 1, int(getattr(obs, 'carril_objetivo', carril_obs))))
            centro_obs_x = obs.rect.centerx
            obs.ancho = BUS_ANCHO if getattr(obs, 'es_bus', False) else CAR_ANCHO
            obs.alto = BUS_ALTO if getattr(obs, 'es_bus', False) else CAR_ALTO
            alto_obs = obs.alto
            obs.carril = carril_obs
            obs.carril_objetivo = carril_obj
            obs.y = LANE_START_Y + (carril_obs * ALTURA_CARRIL) + (ALTURA_CARRIL // 2 - alto_obs // 2)
            obs.y_objetivo = LANE_START_Y + (carril_obj * ALTURA_CARRIL) + (ALTURA_CARRIL // 2 - alto_obs // 2)
            obs.rect.width = obs.ancho
            obs.rect.height = obs.alto
            obs.rect.centerx = centro_obs_x
            obs.x = obs.rect.x
            obs.rect.y = int(obs.y)
            if obs.es_bus and bus_images:
                obs.image = random.choice(bus_images)
            elif (not obs.es_bus) and car_images:
                obs.image = random.choice(car_images)

    scroll_x = max(-ANCHO, min(scroll_x, 0))

# --- BUCLE PRINCIPAL ---
while juego_activo:
    reloj.tick(60)
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            juego_activo = False

        if evento.type == pygame.KEYDOWN and not nivel_iniciado and not game_over and not nivel_completado:
            nivel_iniciado = True
            tiempo_inicio = pygame.time.get_ticks()
            player_last_anim_time = tiempo_inicio
            continue

        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_F11:
            cambiar_modo_pantalla("Ventana" if modo_pantalla_actual == "Pantalla completa" else "Pantalla completa")
        if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_ESCAPE, pygame.K_p):
            if not game_over and not nivel_completado:
                if not menu_pausa_activo:
                    menu_pausa_activo = True
                    inicio_pausa = pygame.time.get_ticks()
                    indice_menu_pausa = 0
                else:
                    cerrar_menu_pausa()

        if menu_pausa_activo and evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_UP, pygame.K_w):
                indice_menu_pausa = (indice_menu_pausa - 1) % 7
            elif evento.key in (pygame.K_DOWN, pygame.K_s):
                indice_menu_pausa = (indice_menu_pausa + 1) % 7
            elif evento.key in (pygame.K_LEFT, pygame.K_a):
                if indice_menu_pausa == 1:
                    music_volume = max(0.0, round(music_volume - 0.1, 2))
                    if music_volume > 0:
                        music_muted = False
                    aplicar_volumen_musica()
                elif indice_menu_pausa == 3:
                    idx = DIFICULTADES.index(dificultad_actual)
                    aplicar_dificultad(DIFICULTADES[(idx - 1) % len(DIFICULTADES)])
                elif indice_menu_pausa == 4:
                    idx = MODOS_PANTALLA.index(modo_pantalla_actual)
                    cambiar_modo_pantalla(MODOS_PANTALLA[(idx - 1) % len(MODOS_PANTALLA)])
            elif evento.key in (pygame.K_RIGHT, pygame.K_d):
                if indice_menu_pausa == 1:
                    music_volume = min(1.0, round(music_volume + 0.1, 2))
                    if music_volume > 0:
                        music_muted = False
                    aplicar_volumen_musica()
                elif indice_menu_pausa == 3:
                    idx = DIFICULTADES.index(dificultad_actual)
                    aplicar_dificultad(DIFICULTADES[(idx + 1) % len(DIFICULTADES)])
                elif indice_menu_pausa == 4:
                    idx = MODOS_PANTALLA.index(modo_pantalla_actual)
                    cambiar_modo_pantalla(MODOS_PANTALLA[(idx + 1) % len(MODOS_PANTALLA)])
            elif evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                ejecutar_opcion_menu_pausa(indice_menu_pausa)

        if menu_pausa_activo and evento.type == pygame.MOUSEMOTION:
            if not cursor_visible:
                cursor_visible = True
                pygame.mouse.set_visible(True)
            for i in range(7):
                if obtener_rect_opcion_pausa(i).collidepoint(evento.pos):
                    indice_menu_pausa = i
                    break

        if menu_pausa_activo and evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for i in range(7):
                if obtener_rect_opcion_pausa(i).collidepoint(evento.pos):
                    indice_menu_pausa = i
                    ejecutar_opcion_menu_pausa(i)
                    break
        # Reiniciar nivel cuando estás en estado de 'game over' o nivel completado y pulsas R
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_r and (game_over or nivel_completado):
            reiniciar_partida()

    jugando_activo = nivel_iniciado and not game_over and not nivel_completado and not menu_pausa_activo
    if jugando_activo and cursor_visible:
        cursor_visible = False
        pygame.mouse.set_visible(False)
    
    # Calcular tiempo transcurrido
    tiempo_actual = pygame.time.get_ticks()
    pausa_en_curso = (tiempo_actual - inicio_pausa) if (menu_pausa_activo and inicio_pausa is not None) else 0
    tiempo_transcurrido = tiempo_actual - tiempo_inicio - tiempo_pausa_acumulado - pausa_en_curso
    if not nivel_iniciado:
        tiempo_transcurrido = 0
    if game_over:
        if tiempo_game_over is None:
            tiempo_game_over = tiempo_transcurrido
        tiempo_transcurrido = tiempo_game_over
    progreso_nivel = min(1.0, tiempo_transcurrido / duracion_nivel)
    factor_dificultad = 1.0 + (MULT_DIFICULTAD_MAX - 1.0) * progreso_nivel
    
    # Verificar si se completó el nivel (solo si no está en game over)
    if nivel_iniciado and tiempo_transcurrido >= duracion_nivel and not game_over and not nivel_completado:
        print("¡NIVEL COMPLETADO! ¡Llegaste a la escuela!")
        jugador.x = max(0, ANCHO - jugador.width - 20)
        nivel_completado = True
        # Reproducir música de victoria una sola vez
        if win_music_loaded:
            try:
                pygame.mixer.music.load(resolver_recurso_audio(WIN_MUSIC_FILE))
                aplicar_volumen_musica()
                pygame.mixer.music.play(0)
            except Exception as e:
                print(f"Error al reproducir música de victoria: {e}")

    if nivel_completado:
        tiempo_transcurrido = duracion_nivel

    # Aumentar densidad de obstáculos conforme pasa el tiempo (más choques tras 30s)
    jugador_moviendo_render = False
    if nivel_iniciado and not game_over and not nivel_completado and not menu_pausa_activo:
        objetivo_obstaculos = max(OBSTACULOS_BASE, min(OBSTACULOS_INICIO_NIVEL, OBSTACULOS_MAX))
        if tiempo_transcurrido >= SEGUNDO_SUBIDA_DENSIDAD:
            objetivo_obstaculos = OBSTACULOS_MAX

        while len(lista_obstaculos) < objetivo_obstaculos:
            nuevo_obs = Obstaculo()
            nuevo_obs.reset(lista_obstaculos, tiempo_transcurrido, jugador)
            lista_obstaculos.append(nuevo_obs)

        while len(lista_obstaculos) > objetivo_obstaculos:
            lista_obstaculos.pop()

    # Si estamos en estado game over, no avanzamos fondo ni procesamos movimiento
    if nivel_iniciado and not game_over and not nivel_completado and not menu_pausa_activo:
        scroll_x -= velocidad_fondo * factor_dificultad
        if scroll_x <= -ANCHO:
            scroll_x = 0

        # 2. MOVIMIENTO JUGADOR (Limitado a los carriles de Cádiz - Solo vertical)
        teclas = pygame.key.get_pressed()
        jugador_moviendo = False
        entrada_movimiento = (
            teclas[pygame.K_UP]
            or teclas[pygame.K_w]
            or teclas[pygame.K_DOWN]
            or teclas[pygame.K_s]
        )

        # Si han pasado 58 segundos, desplazarse al final de la pantalla
        if tiempo_transcurrido >= 58000:
            velocidad_final = max(8, int((ANCHO / ANCHO_BASE) * 8))
            objetivo_final_x = max(0, ANCHO - jugador.width - 20)
            jugador.x = min(objetivo_final_x, jugador.x + velocidad_final)
            jugador_moviendo = True
        else:
            # Si no, permitir movimiento normal
            if (teclas[pygame.K_UP] or teclas[pygame.K_w]) and jugador.top > LANE_START_Y:
                jugador.y -= 5
            if (teclas[pygame.K_DOWN] or teclas[pygame.K_s]) and jugador.bottom < LANE_AREA_BOTTOM:
                jugador.y += 5
            jugador_moviendo = entrada_movimiento

        jugador_moviendo_render = jugador_moviendo

        # Actualizar animación del jugador (siempre activa durante el juego)
        if player_anim_frames and len(player_anim_frames) > 0:
            ahora_anim = pygame.time.get_ticks()
            if ahora_anim - player_last_anim_time >= PLAYER_ANIM_MS:
                player_frame_index = (player_frame_index + 1) % len(player_anim_frames)
                player_last_anim_time = ahora_anim
            player_anim_offset_y = -1 if (jugador_moviendo and player_frame_index % 2 == 0) else (1 if jugador_moviendo else 0)

    # 3. MOVIMIENTO DE OBSTÁCULOS Y COLISIONES
    if nivel_iniciado and not game_over and not nivel_completado and not menu_pausa_activo:
        if tiempo_transcurrido < 56000:
            # Antes del segundo 56: movimiento normal con regeneración
            for obs in lista_obstaculos:
                obs.mover(lista_obstaculos, tiempo_transcurrido, factor_dificultad, jugador)
                if jugador.colliderect(obs.rect) and not invulnerable:
                    reproducir_sonido_choque()
                    vida_perdida_indice = max(0, vidas - 1)
                    tiempo_parpadeo_vida = pygame.time.get_ticks()
                    vidas -= 1
                    invulnerable = True
                    tiempo_invulnerable = pygame.time.get_ticks()
                    print(f"¡Choque! Vidas restantes: {vidas}")
                    obs.reset(lista_obstaculos, tiempo_transcurrido, jugador)
                    if vidas <= 0:
                        print("GAME OVER - ¡No llegaste a clase!")
                        game_over = True
                        if tiempo_game_over is None:
                            tiempo_game_over = tiempo_transcurrido
                        # Reproducir música de game over
                        if gameover_music_loaded:
                            try:
                                pygame.mixer.music.load(resolver_recurso_audio(GAMEOVER_MUSIC_FILE))
                                aplicar_volumen_musica()
                                pygame.mixer.music.play(0)  # Reproducir una sola vez
                            except Exception as e:
                                print(f"Error al reproducir música de game over: {e}")
            desatascar_obstaculos(lista_obstaculos)
        else:
            # A partir del segundo 56: solo mover los obstáculos existentes
            for obs in lista_obstaculos:
                obs.x -= obs.vel * factor_dificultad
                obs.rect.x = obs.x
                obs.actualizar_cambio_carril()
                
                # Detectar colisiones con otros obstáculos
                for otro_obs in lista_obstaculos:
                    if otro_obs is not obs and obs.rect.colliderect(otro_obs.rect):
                        obs.ajustar_trafico(otro_obs)
                        break
                else:
                    obs.vel = velocidad_obstaculo(tiempo_transcurrido) if obs.vel == 0 else obs.vel
                
                # Detectar colisión con jugador
                if jugador.colliderect(obs.rect) and not invulnerable:
                    reproducir_sonido_choque()
                    vida_perdida_indice = max(0, vidas - 1)
                    tiempo_parpadeo_vida = pygame.time.get_ticks()
                    vidas -= 1
                    invulnerable = True
                    tiempo_invulnerable = pygame.time.get_ticks()
                    print(f"¡Choque! Vidas restantes: {vidas}")
                    if vidas <= 0:
                        print("GAME OVER - ¡No llegaste a clase!")
                        game_over = True
                        if tiempo_game_over is None:
                            tiempo_game_over = tiempo_transcurrido
                        # Reproducir música de game over
                        if gameover_music_loaded:
                            try:
                                pygame.mixer.music.load(resolver_recurso_audio(GAMEOVER_MUSIC_FILE))
                                aplicar_volumen_musica()
                                pygame.mixer.music.play(0)  # Reproducir una sola vez
                            except Exception as e:
                                print(f"Error al reproducir música de game over: {e}")
            desatascar_obstaculos(lista_obstaculos)
    
    # Actualizar invulnerabilidad
    if nivel_iniciado and not menu_pausa_activo and invulnerable and pygame.time.get_ticks() - tiempo_invulnerable > TIEMPO_INVULNERABLE:
        invulnerable = False

    # 4. DIBUJADO (La secuencia mágica)
    if bg_img:
        # Dibujamos la imagen de Cádiz dos veces para que no haya huecos
        VENTANA.blit(bg_img, (scroll_x, 0))
        VENTANA.blit(bg_img, (scroll_x + ANCHO, 0))
    else:
        VENTANA.fill((100, 100, 100)) # Gris asfalto si falla la imagen

    # Dibujar obstáculos
    for obs in lista_obstaculos:
        if obs.image:
            VENTANA.blit(obs.image, obs.rect)
        else:
            pygame.draw.rect(VENTANA, ROJO, obs.rect)

    # Dibujar jugador con parpadeo si está invulnerable
    if not invulnerable or (pygame.time.get_ticks() // 200) % 2 == 0:
        if player_anim_frames:
            if player_frame_index >= len(player_anim_frames):
                player_frame_index = 0
            sprite_jugador = player_anim_frames[player_frame_index]
            sprite_rect = sprite_jugador.get_rect(center=jugador.center)
            sprite_rect.y += player_anim_offset_y
            VENTANA.blit(sprite_jugador, sprite_rect)
        elif player_img:
            sprite_rect = player_img.get_rect(center=jugador.center)
            VENTANA.blit(player_img, sprite_rect)
        else:
            pygame.draw.rect(VENTANA, AZUL, jugador)

    ancho_ui, alto_ui = VENTANA.get_size()

    # Mostrar Vidas y Tiempo en pantalla
    fuente = pygame.font.SysFont("Arial", 30)
    for i in range(max(0, vidas)):
        pos_x = 20 + (i * 38)
        pos_y = 18
        if vida_img:
            VENTANA.blit(vida_img, (pos_x, pos_y))
        else:
            pygame.draw.circle(VENTANA, ROJO, (pos_x + 14, pos_y + 14), 12)

    # Parpadeo de la vida perdida recientemente
    tiempo_desde_impacto = pygame.time.get_ticks() - tiempo_parpadeo_vida
    if (
        vida_perdida_indice >= 0
        and tiempo_desde_impacto < DURACION_PARPADEO_VIDA
        and (tiempo_desde_impacto // INTERVALO_PARPADEO_VIDA) % 2 == 0
    ):
        pos_x = 20 + (vida_perdida_indice * 38)
        pos_y = 18
        if vida_img:
            VENTANA.blit(vida_img, (pos_x, pos_y))
        else:
            pygame.draw.circle(VENTANA, ROJO, (pos_x + 14, pos_y + 14), 12)
    
    # Mostrar tiempo restante
    tiempo_restante = max(0, (duracion_nivel - tiempo_transcurrido) // 1000)
    texto_tiempo = fuente.render(f"Tiempo: {tiempo_restante}s", True, BLANCO)
    rect_tiempo = texto_tiempo.get_rect(topright=(ancho_ui - 20, 20))
    panel_tiempo = pygame.Surface((rect_tiempo.width + 20, rect_tiempo.height + 12), pygame.SRCALPHA)
    panel_tiempo.fill((0, 0, 0, 150))
    VENTANA.blit(panel_tiempo, (rect_tiempo.x - 10, rect_tiempo.y - 6))
    VENTANA.blit(texto_tiempo, rect_tiempo)

    # Menú de pausa
    if menu_pausa_activo and not game_over and not nivel_completado:
        layout_pausa = layout_menu_pausa()
        overlay = pygame.Surface((ancho_ui, alto_ui), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        VENTANA.blit(overlay, (0, 0))

        fuente_titulo = pygame.font.SysFont("Arial", max(48, int(56 * layout_pausa["escala"])), bold=True)
        fuente_menu = pygame.font.SysFont("Arial", max(28, int(34 * layout_pausa["escala"])))
        titulo = fuente_titulo.render("PAUSA", True, BLANCO)
        VENTANA.blit(titulo, titulo.get_rect(center=(ancho_ui // 2, layout_pausa["titulo_y"])))

        opciones = [
            "Continuar",
            f"Volumen: {int(music_volume * 100)}%",
            f"Música: {'Silenciada' if music_muted else 'Activa'}",
            f"Dificultad: {dificultad_actual}",
            f"Pantalla: {modo_pantalla_actual}",
            "Reiniciar nivel",
            "Salir",
        ]

        for i, texto in enumerate(opciones):
            color = (255, 230, 120) if i == indice_menu_pausa else BLANCO
            linea = fuente_menu.render(texto, True, color)
            VENTANA.blit(
                linea,
                linea.get_rect(
                    center=(
                        ancho_ui // 2,
                        layout_pausa["inicio_opciones_y"] + i * layout_pausa["separacion_y"],
                    )
                ),
            )

        ayuda = pygame.font.SysFont("Arial", max(18, int(22 * layout_pausa["escala"]))).render("↑↓ seleccionar  |  ←→ ajustar  |  Enter o clic confirmar  |  Esc salir", True, BLANCO)
        VENTANA.blit(ayuda, ayuda.get_rect(center=(ancho_ui // 2, layout_pausa["ayuda_y"])))

    # Espera de inicio del nivel
    if not nivel_iniciado and not game_over and not nivel_completado:
        overlay_inicio = pygame.Surface((ancho_ui, alto_ui), pygame.SRCALPHA)
        overlay_inicio.fill((0, 0, 0, 135))
        VENTANA.blit(overlay_inicio, (0, 0))

        escala_inicio = max(1.0, min(2.2, alto_ui / ALTO_BASE))
        fuente_inicio = pygame.font.SysFont("Arial", int(46 * escala_inicio), bold=True)
        fuente_sub = pygame.font.SysFont("Arial", int(26 * escala_inicio))
        texto_inicio = fuente_inicio.render("Pulsa cualquier tecla", True, BLANCO)
        texto_sub = fuente_sub.render("para empezar el nivel", True, BLANCO)
        VENTANA.blit(texto_inicio, texto_inicio.get_rect(center=(ancho_ui // 2, alto_ui // 2 - int(22 * escala_inicio))))
        VENTANA.blit(texto_sub, texto_sub.get_rect(center=(ancho_ui // 2, alto_ui // 2 + int(26 * escala_inicio))))
    
    # Si estás en game over, mostrar mensaje de pérdida y cómo reiniciar
    if game_over:
        fuente_big = pygame.font.SysFont("Arial", 72)
        texto_perdiste = fuente_big.render("HAS PERDIDO", True, (200, 0, 0))
        rect_perdiste = texto_perdiste.get_rect(center=(ancho_ui // 2, alto_ui // 2 - 40))
        VENTANA.blit(texto_perdiste, rect_perdiste)

        fuente_small = pygame.font.SysFont("Arial", 28)
        texto_reiniciar = fuente_small.render("Presiona R para reiniciar el nivel", True, BLANCO)
        rect_reiniciar = texto_reiniciar.get_rect(center=(ancho_ui // 2, alto_ui // 2 + 40))
        VENTANA.blit(texto_reiniciar, rect_reiniciar)
    
    # Mostrar mensaje de nivel completado
    if nivel_completado:
        overlay_victoria = pygame.Surface((ancho_ui, alto_ui), pygame.SRCALPHA)
        overlay_victoria.fill((0, 0, 0, 95))
        VENTANA.blit(overlay_victoria, (0, 0))

        panel_ancho = min(900, ancho_ui - 80)
        panel_alto = min(280, alto_ui - 120)
        panel_x = (ancho_ui - panel_ancho) // 2
        panel_y = (alto_ui - panel_alto) // 2
        panel_victoria = pygame.Surface((panel_ancho, panel_alto), pygame.SRCALPHA)
        panel_victoria.fill((0, 0, 0, 170))
        VENTANA.blit(panel_victoria, (panel_x, panel_y))

        fuente_grande = pygame.font.SysFont("Arial", 60, bold=True)
        texto_completado = fuente_grande.render("¡NIVEL COMPLETADO!", True, (0, 255, 0))
        fuente_pequeña = pygame.font.SysFont("Arial", 40)
        texto_escuela = fuente_pequeña.render("¡HAS LLEGADO A LA ESCUELA!", True, (0, 255, 0))
        texto_reiniciar = pygame.font.SysFont("Arial", 28).render("Presiona R para jugar otra vez", True, BLANCO)

        centro_x = ancho_ui // 2
        base_y = alto_ui // 2
        rect_completado = texto_completado.get_rect(center=(centro_x, base_y - 55))
        rect_escuela = texto_escuela.get_rect(center=(centro_x, base_y + 15))
        rect_reiniciar = texto_reiniciar.get_rect(center=(centro_x, base_y + 75))
        
        VENTANA.blit(texto_completado, rect_completado)
        VENTANA.blit(texto_escuela, rect_escuela)
        VENTANA.blit(texto_reiniciar, rect_reiniciar)

    pygame.display.flip()

pygame.quit()