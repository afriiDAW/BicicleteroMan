import random
from plataformas import Platform, MovingPlatform
from obstacle import Obstacle
from powerup import PowerUp
from thief import Thief

# ---------------- CONFIGURACIÓN DEL NIVEL ----------------
LEVEL_SEED = 12345  # Semilla fija para generación reproducible
LEVEL_LENGTH = 3000

# Inicializar semilla
random.seed(LEVEL_SEED)

# ---------------- FUNCIONES DE UTILIDAD ----------------
def create_base_platforms():
    """Crea las plataformas principales del nivel."""
    return [
        # Suelo principal con textura en mosaico
        Platform(0, 450, LEVEL_LENGTH, 300, texture_path='suelo.png', tile=True),
        
        # Sección inicial - plataformas amplias
        Platform(160, 360, 180, 20),
        Platform(420, 330, 140, 20),
        
        # Plataformas pequeñas para precisión
        Platform(700, 330, 70, 20),
        Platform(800, 300, 70, 20), 
        Platform(900, 280, 70, 20),
        
        # Plataforma móvil horizontal
        MovingPlatform(1020, 300, 120, 20, axis='x', range_px=160, speed=1.4),
        
        # Tramo central con pasos suaves
        Platform(1260, 340, 160, 20),
        Platform(1520, 320, 130, 20),
        Platform(1720, 300, 120, 20),
        
        # Plataforma móvil vertical
        MovingPlatform(1880, 320, 120, 20, axis='y', range_px=80, speed=0.9),
        
        # Escalera ascendente
        Platform(2060, 360, 80, 20),
        Platform(2160, 330, 80, 20),
        Platform(2260, 300, 80, 20),
        
        # Tramo final
        Platform(2380, 320, 160, 20),
        Platform(2620, 300, 140, 20),
        
        # Plataforma móvil final
        MovingPlatform(2800, 260, 100, 20, axis='x', range_px=100, speed=1.2),
    ]

def create_obstacles(platforms):
    """Genera obstáculos en el suelo y sobre plataformas elegibles."""
    obstacles = []
    
    # Obstáculos fijos en el suelo
    ground_positions = [420, 1400, 2100]
    obstacles.extend([Obstacle(x, 410) for x in ground_positions])
    
    # Obstáculos sobre plataformas largas (excluyendo suelo y plataformas móviles)
    eligible_platforms = [
        p for p in platforms 
        if (type(p) is Platform and 
            p.rect.width >= 150 and 
            p.rect.width < LEVEL_LENGTH)
    ]
    
    if eligible_platforms:
        # Seleccionar ~50% de plataformas elegibles (mínimo 1)
        num_selected = max(1, len(eligible_platforms) // 2)
        selected_platforms = random.sample(eligible_platforms, num_selected)
        
        # Crear obstáculos centrados encima de cada plataforma
        for platform in selected_platforms:
            obstacle_x = platform.rect.centerx - 20  # Centrar obstáculo (40px ancho)
            obstacle_y = platform.rect.top - 40       # Situar encima
            obstacles.append(Obstacle(obstacle_x, obstacle_y))
    
    return obstacles

def create_powerups():
    """Crea los powerups del nivel en posiciones estratégicas."""
    return [
        PowerUp(850, 300),   # Sobre plataformas pequeñas
        PowerUp(1500, 260),  # Tramo central
        PowerUp(2240, 320),  # Antes del final
    ]

def load_level():
    """Carga y retorna todos los elementos del nivel."""
    
    # Generar elementos del nivel
    platforms = create_base_platforms()
    obstacles = create_obstacles(platforms)
    powerups = create_powerups()
    
    # Crear ladrón en posición inicial
    thief = Thief(400, 390)
    
    return platforms, obstacles, powerups, thief
