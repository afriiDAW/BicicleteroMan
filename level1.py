import random
from platform import Platform, MovingPlatform

# Semilla fija para que la generación aleatoria del nivel sea reproducible
LEVEL_SEED = 12345
random.seed(LEVEL_SEED)
from obstacle import Obstacle
from powerup import PowerUp
from thief import Thief

LEVEL_LENGTH = 3000  # ancho total del nivel

def load_level():

    # Diseño mejorado del nivel:
    # - Suelo largo
    # - Secciones de plataformas bajas y altas
    # - Grupos de pequeñas plataformas para saltos de precisión
    # - Escalera de plataformas ascendentes para llegar a un tramo elevado
    # - Obstáculos y powerups repartidos en puntos de riesgo/recompensa
    platforms = [
        # Suelo
        Platform(0, 450, LEVEL_LENGTH, 50),

        # Primera sección: plataformas amplias para acostumbrarse
        Platform(160, 360, 180, 20),
        Platform(420, 330, 140, 20),

    # Pequeñas plataformas dispersas -> precisión (menos altura entre ellas)
    Platform(700, 330, 70, 20),
    Platform(800, 300, 70, 20),
    Platform(900, 280, 70, 20),

        # Plataforma móvil horizontal (patrulla sobre gap)
        MovingPlatform(1020, 300, 120, 20, axis='x', range_px=160, speed=1.4),

    # Tramo central: plataformas con pasos más suaves (menos verticalidad)
    Platform(1260, 340, 160, 20),
    Platform(1520, 320, 130, 20),
    Platform(1720, 300, 120, 20),

        # Plataforma móvil vertical (sube/baja)
        MovingPlatform(1880, 320, 120, 20, axis='y', range_px=80, speed=0.9),

    # Escalera ascendiente (suavizada)
    Platform(2060, 360, 80, 20),
    Platform(2160, 330, 80, 20),
    Platform(2260, 300, 80, 20),

        # Tramo final con plataformas horizontales y un pequeño salto final
        Platform(2380, 320, 160, 20),
        Platform(2620, 300, 140, 20),

        # Plataforma móvil en el final para mayor desafío
        MovingPlatform(2800, 260, 100, 20, axis='x', range_px=100, speed=1.2),
    ]

    # Obstáculos en el suelo (posiciones base)
    obstacles = []
    ground_xs = [420, 1400, 2100]
    for gx in ground_xs:
        obstacles.append(Obstacle(gx, 410))

    # Añadir obstáculos sobre una selección aleatoria de plataformas largas
    # Condición para 'larga': ancho >= 150 (excluyendo la plataforma suelo y plataformas móviles)
    eligible = [p for p in platforms if type(p) is Platform and p.rect.width >= 150 and p.rect.width < LEVEL_LENGTH]
    if eligible:
        # elegir ~50% de las plataformas largas (al menos 1 si hay disponibles)
        k = max(1, len(eligible) // 2)
        chosen = random.sample(eligible, k)
        for p in chosen:
            ox = p.rect.centerx - 20  # centrar obstáculo (obstáculo 40px de ancho)
            oy = p.rect.top - 40      # situar encima de la plataforma
            obstacles.append(Obstacle(ox, oy))

    powerups = [
        # Recompensas situadas en zonas de precisión o de riesgo (ajustadas)
        PowerUp(850, 300),   # ahora sobre plataformas pequeñas accesibles
        PowerUp(1500, 260),  # cerca del tramo central
        PowerUp(2240, 320),  # antes del tramo final
    ]

    # Ladrón: colocarlo justo delante del jugador para que sea visible al inicio
    thief = Thief(400, 390)

    return platforms, obstacles, powerups, thief
