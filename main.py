import pygame
import sys

from player import Player
from camera import Camera
from level1 import load_level, LEVEL_LENGTH

pygame.init()

# ---------------- CONFIGURACIÓN ----------------
WIDTH, HEIGHT = 900, 500
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nivel 1 - Plataformas con Cámara")

CLOCK = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Fuente para HUD/debug
FONT = pygame.font.Font(None, 24)
BIG_FONT = pygame.font.Font(None, 48)
BUTTON_FONT = pygame.font.Font(None, 30)

# ---------------- CARGAR NIVEL ----------------
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
    CLOCK.tick(FPS)
    SCREEN.fill(WHITE)

    # -------- EVENTOS --------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

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

    SCREEN.blit(player.image, camera.apply(player.rect))
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
