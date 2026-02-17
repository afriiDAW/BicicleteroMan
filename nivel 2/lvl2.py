import pygame
import random

# Inicialización
pygame.init()
ANCHO, ALTO = 800, 600
VENTANA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Camino a la escuela - Nivel 2")

# Colores
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)
NEGRO = (0, 0, 0)

# Protagonista

jugador = pygame.Rect(ANCHO//3, ALTO//2, 80, 30)
velocidad = 5
vidas = 3
invulnerable = False
invulnerable_timer = 0
TIEMPO_INVULNERABLE = 1500  # ms


# Carriles
NUM_CARRILES = 6
ALTURA_CARRIL = ALTO // NUM_CARRILES



# Inicializar peatones: uno por carril menos uno (siempre un hueco)
def generar_peatones():
    carriles = list(range(NUM_CARRILES))
    random.shuffle(carriles)
    hueco_libre = carriles.pop()  # Carril sin obstáculo
    peatones = []
    largo_coche = 100
    largo_autobus = largo_coche * 2
    # Elegir aleatoriamente un carril para el autobús
    carril_autobus = random.choice(carriles)
    for carril in carriles:
        y = carril * ALTURA_CARRIL
        if carril == carril_autobus:
            peatones.append(pygame.Rect(random.randint(300, ANCHO-50), y, largo_autobus, ALTURA_CARRIL))
        else:
            peatones.append(pygame.Rect(random.randint(300, ANCHO-50), y, largo_coche, ALTURA_CARRIL))
    return peatones, hueco_libre

peatones, hueco_libre = generar_peatones()

# Power-ups
power_ups = [pygame.Rect(random.randint(300, ANCHO-50), random.randint(0, ALTO-40), 30, 30) for _ in range(2)]
power_up_activo = False
power_up_timer = 0

# Meta (escuela)
meta = pygame.Rect(ANCHO-80, 0, 60, ALTO)

# Reloj

clock = pygame.time.Clock()
juego_activo = True
tiempo_inicio = pygame.time.get_ticks()
duracion_nivel = 60000  # 1 minuto en milisegundos
avance_final = False

while juego_activo:
    clock.tick(60)
    tiempo_actual = pygame.time.get_ticks()
    tiempo_transcurrido = tiempo_actual - tiempo_inicio

    # Si ha pasado el minuto, activar avance automático
    if tiempo_transcurrido >= duracion_nivel:
        avance_final = True

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            juego_activo = False

    # Movimiento del jugador
    teclas = pygame.key.get_pressed()
    if not avance_final:
        if (teclas[pygame.K_UP] or teclas[pygame.K_w]) and jugador.top > 0:
            jugador.y -= velocidad
        if (teclas[pygame.K_DOWN] or teclas[pygame.K_s]) and jugador.bottom < ALTO:
            jugador.y += velocidad
    else:
        # Avance automático hacia la meta
        if jugador.x + jugador.width < meta.x:
            jugador.x += velocidad
        else:
            print("¡Nivel completado!")
            juego_activo = False

    # Movimiento de peatones (de derecha a izquierda)
    velocidad_peaton = 3 + int(4 * tiempo_transcurrido / duracion_nivel)  # Aumenta hasta 7
    if tiempo_transcurrido < 57000:
        carriles = list(range(NUM_CARRILES))
        random.shuffle(carriles)
        hueco_libre = carriles.pop()  # Carril sin obstáculo
        for i, peat in enumerate(peatones):
            peat.x -= velocidad_peaton
            if peat.right < 0:
                # Reasignar a un nuevo carril (excepto el hueco)
                carril = carriles.pop()
                peat.x = ANCHO + random.randint(0, 200)
                peat.y = carril * ALTURA_CARRIL
        # Si hay menos peatones que carriles-1, regenerar
        if len(peatones) < NUM_CARRILES-1:
            peatones, hueco_libre = generar_peatones()
    else:
        # A partir del segundo 55, solo mover los peatones existentes
        for peat in peatones:
            peat.x -= velocidad_peaton

    # Movimiento de power-ups (de derecha a izquierda)
    for pu in power_ups:
        pu.x -= 2
        if pu.right < 0:
            pu.x = ANCHO + random.randint(0, 200)
            pu.y = random.randint(0, ALTO-30)

    # Colisiones con peatones
    if not invulnerable:
        for peat in peatones:
            if jugador.colliderect(peat):
                vidas -= 1
                jugador.x, jugador.y = 100, ALTO//2
                invulnerable = True
                invulnerable_timer = pygame.time.get_ticks()
                if vidas == 0:
                    juego_activo = False

    # Fin de invulnerabilidad
    if invulnerable and pygame.time.get_ticks() - invulnerable_timer > TIEMPO_INVULNERABLE:
        invulnerable = False

    # Colisiones con power-ups
    for pu in power_ups:
        if jugador.colliderect(pu):
            power_up_activo = True
            power_up_timer = pygame.time.get_ticks()
            power_ups.remove(pu)
            velocidad = 8  # Ejemplo: aumenta velocidad

    # Power-up dura 3 segundos
    if power_up_activo and pygame.time.get_ticks() - power_up_timer > 3000:
        power_up_activo = False
        velocidad = 5

    # Llegada a la meta
    if jugador.colliderect(meta):
        print("¡Has llegado a la escuela!")
        juego_activo = False

    # Dibujar todo
    VENTANA.fill(BLANCO)
    pygame.draw.rect(VENTANA, AZUL, jugador)
    for peat in peatones:
        pygame.draw.rect(VENTANA, ROJO, peat)
    for pu in power_ups:
        pygame.draw.rect(VENTANA, VERDE, pu)
    # No dibujar la meta para que no tape la visión
    # pygame.draw.rect(VENTANA, NEGRO, meta)
    # Vidas
    fuente = pygame.font.SysFont(None, 36)
    texto_vidas = fuente.render(f"Vidas: {vidas}", True, NEGRO)
    VENTANA.blit(texto_vidas, (10, 10))
    pygame.display.flip()

pygame.quit()